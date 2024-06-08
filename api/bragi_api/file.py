import os
import uuid

from fastapi import APIRouter, UploadFile, Request, Header
from fastapi.responses import Response

router = APIRouter()


@router.post("/file")
async def upload_file(req: Request, file: UploadFile):
    new_uuid = uuid.uuid4().hex
    data_dir = req.app.data_dir
    filename = file.filename
    final_path = os.path.join(data_dir, new_uuid) + os.path.splitext(filename)[
        1]
    with open(final_path, "wb") as f:
        f.write(await file.read())

    return {"uuid": new_uuid}


@router.get("/videos/{custom_url}/stream")
async def stream_video(custom_url: str, req: Request,
    range: str = Header(None)):
    db = req.app.db
    cur = db.cursor()
    cur.execute("SELECT id FROM videos WHERE custom_url = ?", (custom_url,))
    row = cur.fetchone()
    if not row:
        return {"error": "Video not found"}, 404

    data_dir = req.app.data_dir
    audio_path = f"{data_dir}/{custom_url}.mp4"
    if not os.path.exists(audio_path):
        audio_path = f"{data_dir}/{custom_url}.mp3"
        if not os.path.exists(audio_path):
            return {"error": "Video not found"}, 404

    start, end = 0, os.path.getsize(audio_path)
    if range:
        start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + (1024 * 1024)
    with open(audio_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(os.stat(audio_path).st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers,
                        media_type="video/mp4" if audio_path.endswith(
                            ".mp4") else "audio/mpeg")
