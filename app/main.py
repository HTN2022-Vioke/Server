from fastapi import FastAPI, UploadFile, Request, Response, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
import pitch_shift

from external import redis
import utils.session as session

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

class GetShiftedAudioRequest(BaseModel):
  wav_path: str
  shift_semitones: int    # positive for higher pitch, negative for lower

UPLOAD_ROOT_PATH = "uploads"
OUTPUT_ROOT_PATH = "outputs"

SHIFT_DIRECTORY = "shifted"
TEMP_DIRECTORY = "temp"

AUDIO_FILE_EXTENSION = ".wav"
OFF_VOCAL_SUFFIX = "_off_vocal"
ON_VOCAL_RETURN_KEY_NAME = "audioUrl"
OFF_VOCAL_RETURN_KEY_NAME = "audioNvUrl"

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# sketchy hardcoded function to ensure directories exist...
def create_dir_if_not_exists(path):
  if not os.path.exists(path):
    os.makedirs(path)
    
def validate_directories():
  for path in [UPLOAD_ROOT_PATH, OUTPUT_ROOT_PATH]:
    create_dir_if_not_exists(path)


protected_paths = {
    "GET": [
        "/"
    ],
    "POST": [],
}

# `request.state` is a custom dict for storing data across middlewares and handlers

@app.middleware("http")
async def create_session_if_not_exist(request: Request, call_next):
    session_jwt = request.cookies.get("session")
    if request.url.path not in protected_paths[request.method]:
        return await call_next(request)
    if session_jwt is None:
        # create new session
        session_obj = redis.new_session()
        token = session.create_jwt_token({"uuid": session_obj.uuid})
        request.state.session_uuid = session_obj.uuid
        response = await call_next(request)
        response.set_cookie("session", token)
        return response
    # since sessions aren't protected, we don't need to decode the jwt and authenticate the user
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
    session = await redis.get_session(request.state.session_uuid)
    return JSONResponse(session.get_data())

# @app.post("/session")


@app.post("/get-shifted-audio/")
async def get_shifted_audio(request: GetShiftedAudioRequest):
  validate_directories()

  wav_path = request.wav_path[1:]
  shift_semitones = request.shift_semitones

  if not os.path.exists(wav_path):
      raise HTTPException( \
          status_code=400, \
          detail="Song {name} does not exist in uploads".format(name = wav_path))
      
  song_filename = os.path.basename(wav_path)
  song_name = song_filename[:len(song_filename)-4]

  if (shift_semitones == 0):
    return {
      ON_VOCAL_RETURN_KEY_NAME: "/" + wav_path,
      OFF_VOCAL_RETURN_KEY_NAME: "/" + "{dir1}/{dir2}/{filename}".format(
        dir1 = OUTPUT_ROOT_PATH, dir2 = song_name, filename = song_name + OFF_VOCAL_SUFFIX + AUDIO_FILE_EXTENSION
      )
    }

  shifted_song_name_on_vocal = "{name}_{shift}".format(
    name = song_name, shift = shift_semitones
  )
  shifted_song_name_off_vocal = "{name}{suffix}_{shift}".format(
    name = song_name, suffix = OFF_VOCAL_SUFFIX, shift = shift_semitones
  )
  shift_directory = "{dir1}/{dir2}/{dir3}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    dir3 = SHIFT_DIRECTORY
  )
  create_dir_if_not_exists(shift_directory)
  
  # TODO: make on and off vocal concurrent?
  # on-vocal paths
  output_path_on_vocal = "{dir}/{filename}".format(
    dir = shift_directory,
    filename = shifted_song_name_on_vocal + AUDIO_FILE_EXTENSION
  )
  # off-vocal paths
  path_off_vocal = "{dir1}/{dir2}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    filename = song_name + OFF_VOCAL_SUFFIX + AUDIO_FILE_EXTENSION
  )
  output_path_off_vocal = "{dir}/{filename}".format(
    dir = shift_directory,
    filename = shifted_song_name_off_vocal + AUDIO_FILE_EXTENSION
  )

  if (os.path.isfile(output_path_on_vocal)):
    return {
      ON_VOCAL_RETURN_KEY_NAME: "/" + output_path_on_vocal,
      OFF_VOCAL_RETURN_KEY_NAME: "/" + output_path_off_vocal
    }

  pitch_shift.shift_audio(wav_path, output_path_on_vocal, shift_semitones)
  pitch_shift.shift_audio(path_off_vocal, output_path_off_vocal, shift_semitones)

  return {
    ON_VOCAL_RETURN_KEY_NAME: "/" + output_path_on_vocal,
    OFF_VOCAL_RETURN_KEY_NAME: "/" + output_path_off_vocal
  }
