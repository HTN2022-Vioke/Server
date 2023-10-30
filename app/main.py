from db_models import SessionPayload
from external import redis as redis_connector
from fastapi import FastAPI, UploadFile, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from models import Session as SessionModel, GetAudioFile as GetAudioFileModel
from pydantic import BaseModel
from typing import List
from utils.auth import create_jwt_token, decode_jwt_token
from utils.clocker import Clocker
import os
import utils.audio as audio_utils
import aiofiles
import shutil

FILES_ROOT_PATH = "files"
OFF_VOCAL_SUFFIX = "_off_vocal"

def createDirIfNotExists(path):
  if not os.path.exists(path):
    os.makedirs(path)
    
createDirIfNotExists(FILES_ROOT_PATH)

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
    path = f"{FILES_ROOT_PATH}/{file_name}"
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
async def upload_vocal(file: UploadFile):
    filename = file.filename
    song_name = filename[:len(filename)-4] # TODO: get this from frontend
    song_dir = f"{FILES_ROOT_PATH}/{song_name}"
    createDirIfNotExists(song_dir) # TODO: handle/warn when folder exists
    
    song_path_original = f"{FILES_ROOT_PATH}/{song_name}/{filename}"
    async with aiofiles.open(song_path_original, 'wb') as out:
        content = await file.read()  # async read
        await out.write(content)  # async write
    
    _, file_extension = os.path.splitext(filename)
    song_path_wav = "{song_dir}/{filename}".format(
        dir = song_dir,
        filename = song_name + OFF_VOCAL_SUFFIX + ".wav"
    )
    if (file_extension != "wav"):
        audio_utils.createWavFromMp3(song_path_original, song_dir)

    return JSONResponse({"message": "success", "url": song_path_wav})


@app.post("/upload-lrc")
async def upload_vocal(file: UploadFile):
    song = "lig"
    filename = file.filename
    path = "{upload}/{song}/{filename}".format(upload = FILES_ROOT_PATH, song = song, filename = filename)
    async with aiofiles.open(path, 'wb') as out:
        content = await file.read()  # async read
        await out.write(content)  # async write
        
    return JSONResponse({"message": "success", "url": path})

@app.post("/get-audio-file")
async def get_audio_file(request: Request, file_requests: List[GetAudioFileModel]):
    # generate files based on the saved original file
    # ...
    
    # add condition for key shifted files
    # file.name = name of original file
    
    response = []
    for file in file_requests:
        if file.has_vocal:
            response.append({
                "name": file.name,
                "url": "lig.mp3", # file.name
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
