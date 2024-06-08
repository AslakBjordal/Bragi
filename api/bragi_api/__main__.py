import argparse
import asyncio
import sqlite3
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from bragi_api import file, users
from bragi_api.common import lock
from bragi_api.server import router


# noinspection SqlNoDataSourceInspection
@asynccontextmanager
async def lifespan(app: FastAPI):
    parser = argparse.ArgumentParser(description="Bragi API")

    # Bragi is currently incredibly simple. It is not distributed and stateful.
    # The files are stored in a file system and the server should only run in ONE place.
    # Since we're using FastAPI, we can serve concurrent requests, but we should
    # probably add some rate limiting if we don't convert to a distributed architecture.
    parser.add_argument("--data-dir", type=str, required=True,
                        help="Path to the directory where the files are stored")
    # Simple sqlite3 database should be enough for us to store the metadata.
    parser.add_argument("--sqlite-path", type=str, required=True,
                        help="Path to the sqlite3 database")

    args = parser.parse_args()

    app.data_dir = args.data_dir

    # check_same_thread=False is usually unsafe, but we're going to guard writes with a lock
    con = sqlite3.connect(args.sqlite_path, check_same_thread=False)

    # Create tables if they don't exist
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL,
            password_hash TEXT
        );
        
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            token TEXT,
            expires_at INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY,
            name TEXT,
            youtube_id TEXT,
            custom_url TEXT,
            state TEXT,
            language TEXT
        );
        CREATE INDEX IF NOT EXISTS youtube_id_index ON videos (youtube_id);
        CREATE INDEX IF NOT EXISTS custom_url_index ON videos (custom_url);
        
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY,
            video_id INTEGER,
            start_time INTEGER,
            end_time INTEGER,
            text TEXT,
            language TEXT,
            FOREIGN KEY(video_id) REFERENCES videos(id)
        );
        CREATE INDEX IF NOT EXISTS video_id_index ON segments (video_id);
        CREATE INDEX IF NOT EXISTS video_id_start_time_index ON segments (video_id, start_time);
        CREATE INDEX IF NOT EXISTS video_id_start_time_end_time_index ON segments (video_id, start_time, end_time);
        CREATE UNIQUE INDEX IF NOT EXISTS video_id_start_time_end_time_text_index ON segments (video_id, start_time, end_time, text);
        """
    )

    app.db = con

    yield

    con.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(users.router)
app.include_router(file.router)


def blocking_check(db: sqlite3.Connection, token: str) -> dict:
    lock.acquire()
    cur = db.cursor()
    cur.execute(
        "SELECT u.* FROM sessions s INNER JOIN users u on u.id = s.user_id WHERE token = ? AND expires_at > ?",
        (token, int(time.time())))
    row = cur.fetchone()
    lock.release()
    return row


@app.middleware("http")
async def authenticated(request: Request, call_next):
    match (request.method, request.url.path):
        case ("POST", "/users") | ("POST", "/users:login"):
            return await call_next(request)

    token = request.headers.get("authorization")
    if not token:
        token = request.cookies.get("token")
        if not token:
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        token = f"Bearer {token}"

    if not token.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    token = token.split(" ")[1]

    user = await asyncio.to_thread(blocking_check, app.db, token)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    request.state.user = user

    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run("bragi_api.__main__:app", reload=True)
