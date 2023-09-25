from external import redis
from fastapi import FastAPI, UploadFile, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import aiofiles
import os
import pitch_shift
import utils.session as session
import utils.audio_utils as audio_utils
import get_off_vocal

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

  wav_path = request.wav_path
  shift_semitones = request.shift_semitones

  if not os.path.isfile(wav_path):
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

#TODO: make "upload audio file" into a separate function

@app.post("/get-off-vocal/")
async def getOffVocal(file: UploadFile): # assume mp3, TODO: convert any kind to wav here
  validate_directories()
  # store audio file to uploads folder
  filename = file.filename
  filepath = "{dir}/{filename}".format(dir = UPLOAD_ROOT_PATH, filename = filename)
  async with aiofiles.open(filepath, 'wb') as out:
    content = await file.read()  # async read
    await out.write(content)  # async write

  song_name = filename[:len(filename)-4]
  song_dir = "{dir1}/{dir2}".format(dir1 = OUTPUT_ROOT_PATH, dir2 = song_name)
  create_dir_if_not_exists(song_dir) # TODO: handle/warn when folder exists
  
  # create wav
  wav_path = audio_utils.createWavFromMp3(filename, UPLOAD_ROOT_PATH, song_dir)

  # create off vocal
  filepath_off_vocal = "{dir}/{filename}".format(
    dir = song_dir,
    filename = song_name + OFF_VOCAL_SUFFIX + AUDIO_FILE_EXTENSION
  )

  if not os.path.isfile(filepath_off_vocal):
    get_off_vocal.createOffVocal(wav_path, filepath_off_vocal)

  return {
    ON_VOCAL_RETURN_KEY_NAME: "/" + wav_path,
    OFF_VOCAL_RETURN_KEY_NAME: "/" + filepath_off_vocal
  }
