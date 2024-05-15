import secrets
import time

import bcrypt
from fastapi import APIRouter
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response

from bragi_api.common import lock

router = APIRouter()


class SignUpRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class Me(BaseModel):
    id: int
    email: str

@router.get("/me")
def get_me(request: Request):
    return Me(id=request.state.user[0], email=request.state.user[1])

@router.post("/users", status_code=201)
def sign_up(params: SignUpRequest, request: Request):
    hashed_password = bcrypt.hashpw(params.password.encode("utf-8"),
                                    bcrypt.gensalt())
    lock.acquire()
    cur = request.app.db.cursor()
    cur.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (params.email, hashed_password))
    request.app.db.commit()
    lock.release()

    return {}

@router.post("/users:login")
def sign_in(params: LoginRequest, request: Request, response: Response):
    cur = request.app.db.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE email = ?",
                (params.email,))
    row = cur.fetchone()
    if not row:
        return {"error": "Invalid email or password"}

    user_id, password_hash = row
    if not bcrypt.checkpw(params.password.encode("utf-8"), password_hash):
        return {"error": "Invalid email or password"}

    new_token = secrets.token_hex(30)
    lock.acquire()
    cur.execute("INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, new_token, int(time.time()) + 60 * 60 * 24 * 7))
    request.app.db.commit()
    lock.release()

    # Not really ideal, but just for simplicity
    response.set_cookie("token", new_token, httponly=True, max_age=60 * 60 * 24 * 7)

    return {"token": new_token}