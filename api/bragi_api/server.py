import asyncio
import logging
import os
from enum import Enum
from typing import Optional

import yt_dlp
from fastapi import APIRouter
from faster_whisper import WhisperModel
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

from bragi_api.common import lock

router = APIRouter()
logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
model = WhisperModel("medium", device="cpu", compute_type="int8")


class Action(str, Enum):
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    START_TRANSCRIPTION = "start_transcription"
    STREAM_SEGMENTS = "stream_segments"


class State(str, Enum):
    IDLE = "idle"
    TRANSCRIBING = "transcribing"
    ERROR = "error"
    SUCCESS = "success"


class WebsocketMessage(BaseModel):
    action: Action

    # Error
    error: Optional[str] = None

    # Start transcription
    youtube_id: Optional[str] = None
    custom_url: Optional[str] = None

    # Language
    language: Optional[str] = "en"
    delay: Optional[float] = 0

    # Stream segments
    segment_start_time: Optional[float] = None
    segment_end_time: Optional[float] = None
    segment_text: Optional[str] = None
    segment_stop: Optional[bool] = False


async def ping(websocket: WebSocket):
    await websocket.send_json(
        WebsocketMessage(action=Action.PONG).dict(exclude_none=True))


def blocking_youtube_download(youtube_id: str, data_dir: str):
    # First download audio into data_dir using youtube_dl
    ydl_opts = {
        "outtmpl": f"{data_dir}/%(id)s.%(ext)s",
        # Only download the audio
        "format": "bestaudio",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={youtube_id}"])


def blocking_transcribe(audio_path: str, video_id: int, language: str, db):
    segments, _ = model.transcribe(
        audio_path,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        language=language,
    )
    for segment in segments:
        lock.acquire()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO segments (video_id, start_time, end_time, text, language) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (video_id, segment.start, segment.end, segment.text, language))
        db.commit()
        lock.release()

    # Set the state to success
    lock.acquire()
    cur = db.cursor()
    cur.execute("UPDATE videos SET state = ? WHERE id = ?",
                (State.SUCCESS, video_id))
    db.commit()
    lock.release()


async def transcribe_background(data_dir: str, video_id: int,
    custom_url: Optional[str],
    websocket: WebSocket,
    msg: WebsocketMessage):
    audio_path = f"{data_dir}/{msg.youtube_id}.webm" if not custom_url else f"{data_dir}/{custom_url}.mp4"
    # Check if the audio file already exists
    if not os.path.exists(audio_path):
        if custom_url:
            # Check mp3 file
            audio_path = f"{data_dir}/{custom_url}.mp3"
            if not os.path.exists(audio_path):
                await websocket.send_json(
                    WebsocketMessage(action=Action.ERROR,
                                     error="Audio file not found").dict(
                        exclude_none=True))
                return
        else:
            # Download the audio file
            await asyncio.create_task(asyncio.to_thread(
                blocking_youtube_download, msg.youtube_id, data_dir))

    asyncio.create_task(
        asyncio.to_thread(blocking_transcribe, audio_path, video_id,
                          msg.language,
                          websocket.app.db))


async def start_transcription(websocket: WebSocket, data: WebsocketMessage):
    if not data.youtube_id and not data.custom_url:
        await websocket.send_json(WebsocketMessage(action=Action.ERROR,
                                                   error="youtube_id or custom_url is required").dict(
            exclude_none=True))
        return

    # Check if any other transcription is running
    found = False
    while True:
        cur = websocket.app.db.cursor()
        cur.execute(
            "SELECT state FROM videos WHERE youtube_id = ? OR custom_url = ?",
            (data.youtube_id, data.custom_url))
        row = cur.fetchone()

        # If success, then we already have the segments
        # If error, then re-transcribe
        # Otherwise, we can just wait for it to finish
        if row:
            state = State(row[0])
            if state == State.SUCCESS:
                found = True
                break
            else:
                break
        else:
            break

    # Pass off to a background job then return
    if not found:
        # Check if it already exists
        cur = websocket.app.db.cursor()
        cur.execute(
            "SELECT id, state, custom_url FROM videos WHERE (youtube_id = ? OR custom_url = ?) AND language = ?",
            (data.youtube_id, data.custom_url, data.language))
        row = cur.fetchone()
        video_id = None
        custom_url = None
        if not row:
            lock.acquire()
            cur.execute(
                "INSERT INTO videos (youtube_id, custom_url, state, language) VALUES (?, ?, ?, ?)",
                (data.youtube_id, data.custom_url, State.TRANSCRIBING,
                 data.language))
            websocket.app.db.commit()
            video_id = cur.lastrowid
            custom_url = data.custom_url
            lock.release()
        else:
            video_id = row[0]
            custom_url = row[2]

            # Set the state to transcribing
            if State(row[1]) == State.SUCCESS:
                await websocket.send_json(
                    WebsocketMessage(action=Action.ERROR,
                                     error="Transcription already exists").dict(
                        exclude_none=True))
                return
            lock.acquire()
            cur = websocket.app.db.cursor()
            cur.execute("UPDATE videos SET state = ? WHERE id = ?",
                        (State.TRANSCRIBING, video_id))
            websocket.app.db.commit()
            lock.release()
        asyncio.create_task(
            transcribe_background(websocket.app.data_dir, video_id, custom_url,
                                  websocket,
                                  data))

    await websocket.send_json(
        WebsocketMessage(action=Action.START_TRANSCRIPTION,
                         youtube_id=data.youtube_id,
                         custom_url=data.custom_url,
                         language=data.language).dict(exclude_none=True))


async def stream_segments(websocket: WebSocket, data: WebsocketMessage):
    if data.segment_stop:
        return
    # We pass off one segment at a time, if no segment is found
    # for time then we just block until a new segment is found
    current_time = data.segment_start_time
    if not current_time:
        current_time = 0

    # Check if a video id is present
    cur = websocket.app.db.cursor()
    cur.execute("SELECT id FROM videos WHERE (youtube_id = ? OR custom_url = ?) AND language = ?",
                (data.youtube_id, data.custom_url, data.language))
    row = cur.fetchone()
    if not row:
        asyncio.ensure_future(start_transcription(websocket, data))
        while True:
            cur.execute(
                "SELECT id FROM videos WHERE (youtube_id = ? OR custom_url = ?) AND language = ?",
                (data.youtube_id, data.custom_url, data.language))
            row = cur.fetchone()
            if row:
                break
            await asyncio.sleep(1)

    video_id = row[0]
    logger.info(f"Streaming segments for video_id: {video_id}")

    while True:
        logger.info(f"Checking for segments at time: {current_time}")

        cur = websocket.app.db.cursor()
        cur.execute(
            "SELECT start_time, end_time, text FROM segments WHERE video_id = ? AND start_time >= ? AND language = ? ORDER BY start_time LIMIT 1",
            (video_id, current_time, data.language))
        row = cur.fetchone()
        if row:
            await websocket.send_json(
                WebsocketMessage(action=Action.STREAM_SEGMENTS,
                                 segment_start_time=row[0],
                                 segment_end_time=row[1],
                                 segment_text=row[2]).dict(exclude_none=True))
            # Sleep the duration of the segment, account for the start_time duration.
            # Sometimes we can be given a 0 start time while the segment starts at a later time.
            time_to_sleep = row[1] - row[0]
            if current_time < row[1]:
                time_to_sleep += row[0] - current_time
            if data.delay:
                time_to_sleep += data.delay

            current_time = row[1]
            await asyncio.sleep(time_to_sleep)
        else:
            logger.info(f"No segments found at time: {current_time}")
            await asyncio.sleep(1)
    pass


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_task = None
    try:
        while True:
            data = WebsocketMessage(**(await websocket.receive_json()))
            match data.action:
                case Action.PING:
                    await ping(websocket)
                case Action.START_TRANSCRIPTION:
                    await start_transcription(websocket, data)
                case Action.STREAM_SEGMENTS:
                    if stream_task and (
                        not stream_task.done() or stream_task.cancelled()):
                        stream_task.cancel()
                        stream_task = None
                    stream_task = asyncio.ensure_future(
                        stream_segments(websocket, data))
    except WebSocketDisconnect:
        if stream_task and (not stream_task.done() or stream_task.cancelled()):
            stream_task.cancel()
