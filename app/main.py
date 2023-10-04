from fastapi import FastAPI, UploadFile, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from utils.clocker import Clocker
from utils.utils import create_jwt_token, decode_jwt_token

from external import redis as redis_connector
from db_models import SessionPayload
from models import Session as SessionModel

# right now, we're assuming all uploads are mp3

# Structure:
# UPLOAD_ROOT_PATH
#   -- songname.mp3
# OUTPUT_ROOT_PATH
#   -- /songname
#     -- songname.wav
#     -- songname_off_vocal.wav
#     -- /SHIFT_DIRECTORY
#       -- songname_on_vocal_+2.wav
#       -- songname_off_vocal_+2.wav


app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", 'POST', 'PATCH', 'DELETE'],
    expose_headers=["Set-Cookie"],
)

def create_dir_if_not_exists(path):
  if not os.path.exists(path):
    os.makedirs(path)

protected_paths = {
    "GET": [
        "/"
    ],
    "POST": [],
}

# `request.state` is a custom dict for storing data across middlewares and handlers

@app.middleware("http")
async def parse_session(request: Request, call_next):
    print(request.url)
    request.state.session_uuid = None
    session_jwt = request.cookies.get("session")
    if session_jwt is not None:
        session = decode_jwt_token(session_jwt)
        request.state.session_uuid = session.uuid
    print(request.state.session_uuid, session_jwt, request.cookies, request)
    return await call_next(request)

@app.get("/")
async def root():
    return {"message": "homeasfasfasdf"}

@app.get("/files/{file_name}")
async def get_outputs(file_name: str):
    path = f"outputs/{file_name}"
    # TODO: need to sanitize path later to prevent os path injection os they don't steal all the os system secrets
    return FileResponse(
        path,
        media_type="audio/wav", 
        headers={
            "Accept-Ranges": "bytes"
        }
    )

@app.get("/session")
async def get_session(request: Request):
    print(request.state.session_uuid)
    if request.state.session_uuid is None:
        return JSONResponse({"message": "session does not exist"}, status_code=404)
    session = redis_connector.get_session(request.state.session_uuid)
    return JSONResponse(session.to_dict())

@app.post("/session")
async def create_session(request: Request, response: Response):
    if request.state.session_uuid is not None:
        return JSONResponse({"message": "session already exists"})
    session = redis_connector.new_session()
    token = create_jwt_token(SessionPayload(uuid=session.uuid))
    response.set_cookie(
        key="session", 
        value=token,
        expires=Clocker().add_time("7d").time,
        # httponly=True,
        samesite="none",
        secure=True,
    )
    return session.to_dict()

@app.patch("/session")
async def update_session(request: Request, session: SessionModel):
    if request.state.session_uuid is None:
        return JSONResponse({"message": "session does not exist"})
    redis_connector.upsert_session(session)
    return JSONResponse({"message": "session updated"})

@app.post("/get-off-vocal")
async def get_off_vocal(request: Request):
    # generate files
    # ...

    files = {
        "audioUrl": "lig.mp3",
        "audioNvUrl": "lig-nv.wav",
    }
    # add to session data
    request.state.session_uuid


    return files
