import argparse
import sqlite3
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from bragi_api.server import router


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
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY,
            youtube_id TEXT,
            custom_url TEXT,
            state TEXT
        );
        CREATE INDEX IF NOT EXISTS youtube_id_index ON videos (youtube_id);
        CREATE INDEX IF NOT EXISTS custom_url_index ON videos (custom_url);
        
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY,
            video_id INTEGER,
            start_time INTEGER,
            end_time INTEGER,
            text TEXT,
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

if __name__ == "__main__":
    uvicorn.run("bragi_api.__main__:app", reload=True)
