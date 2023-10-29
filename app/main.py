from typing import List
from fastapi import FastAPI, UploadFile, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from utils.clocker import Clocker
from utils.auth import create_jwt_token, decode_jwt_token

from external import redis as redis_connector
from db_models import SessionPayload
from models import Session as SessionModel, GetAudioFile as GetAudioFileModel

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", 'POST', 'PATCH', 'DELETE'],
    expose_headers=["Set-Cookie"],
)

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


@app.post("/upload-vocal")
async def upload_vocal(request: Request):
    # save current file
    # ...
    return JSONResponse({"message": "success"})

@app.post("/get-audio-file")
async def get_audio_file(request: Request, file_requests: List[GetAudioFileModel]):
    # generate files based on the saved original file
    # ...
    
    # add condition for key shifted files
    response = []
    for file in file_requests:
        if file.has_vocal:
            response.append({
                "name": file.name,
                "url": "lig.mp3",
                "hasVocal": True,
                "curKeyShift": file.cur_key_shift
            })
        else:
            response.append({
                "name": file.name,
                "url": "lig-nv.wav",
                "hasVocal": False,
                "curKeyShift": file.cur_key_shift
            })
    return JSONResponse(response)
