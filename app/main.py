from db_models import SessionPayload
from external import redis as redis_connector
from fastapi import FastAPI, UploadFile, Request, Response, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from models import Session as SessionModel, GetAudioFile as GetAudioFileModel
from pydantic import BaseModel
from typing import Annotated, List
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

def getLocalPath(song_name, has_vocal=False, key_shift=0, include_root_path=True):
    path = f"{FILES_ROOT_PATH}/{song_name}/{song_name}" if include_root_path else f"{song_name}/{song_name}"
    if has_vocal:
        path += OFF_VOCAL_SUFFIX
    if key_shift != 0:
        path += "_" + ("+" if (key_shift>0) else "-") + str(abs(key_shift))
    path += ".wav"
    return path

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

@app.get("/files/{name}/{file_name}")
async def get_outputs(name: str, file_name: str):
    path = f"{FILES_ROOT_PATH}/{name}/{file_name}"
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
async def upload_vocal(
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()]
):
    filename = file.filename
    song_name = name
    song_dir = f"{FILES_ROOT_PATH}/{song_name}"
    createDirIfNotExists(song_dir) # TODO: handle/warn when folder exists
    
    song_path_original = f"{FILES_ROOT_PATH}/{song_name}/{filename}"
    async with aiofiles.open(song_path_original, 'wb') as out:
        content = await file.read()  # async read
        await out.write(content)  # async write
    
    _, file_extension = os.path.splitext(filename)
    song_path_wav = f"{song_dir}/{song_name + '.wav'}"
    if (file_extension != "wav"):
        audio_utils.createWavFromMp3(song_name, song_path_original, song_dir)

    return JSONResponse({"message": "success", "url": song_path_wav})


@app.post("/upload-lrc")
async def upload_vocal(
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()]
):
    filename = file.filename
    path = f"{FILES_ROOT_PATH}/{name}/{filename}"
    async with aiofiles.open(path, 'wb') as out:
        content = await file.read()  # async read
        await out.write(content)  # async write
        
    return JSONResponse({"message": "success", "url": f"{name}/{filename}"})

@app.post("/get-audio-file")
async def get_audio_file(request: Request, file_requests: List[GetAudioFileModel]):
    response = []
    for file in file_requests:
        target_path = getLocalPath(file.name, file.has_vocal, file.key_shift)
        # generate off vocal if needed
        if (not file.has_vocal) and (not os.path.isfile(target_path)):
            audio_utils.createOffVocal(getLocalPath(file.name), getLocalPath(file.name, False))
        
        # generate key shift if needed
        if (file.key_shift != 0) and (not os.path.isfile(target_path)):
            audio_utils.shift_audio(getLocalPath(file.name, file.has_vocal), target_path, file.key_shift)
        
        response.append({
            "name": file.name,
            "url": getLocalPath(file.name, file.has_vocal, file.key_shift, include_root_path=False),
            "hasVocal": True if file.has_vocal else False,
            "keyShift": file.key_shift
        })
        
    return JSONResponse(response)
