from audio_api import get_off_vocal, pitch_shift
from audio_api.utils import createWavFromMp3
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import os
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

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

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# sketchy hardcoded function to ensure directories exist...
def validateDirectories():
  for path in [UPLOAD_ROOT_PATH, OUTPUT_ROOT_PATH]:
    createDirIfNotExists(path)

def createDirIfNotExists(path):
  if not os.path.exists(path):
    os.makedirs(path)

@app.get("/")
async def root():
  return {"message": "home"}

# @app.get("/outputs")
# async def getOutputs():
#   path = "outputs/let_it_go/let_it_go.wav"
#   f = open(path, mode="rb")
#   headers = {"Content-Length": str(os.path.getsize(path)), "Content-Type": "audio/wav"}
#   return Response(f.read(), headers=headers)

@app.post("/get-off-vocal/")
async def getOffVocal(file: UploadFile): # assume mp3
  validateDirectories()
  # store mp3 file to uploads folder
  filename = file.filename
  filepath = "{dir}/{filename}".format(dir = UPLOAD_ROOT_PATH, filename = filename)
  async with aiofiles.open(filepath, 'wb') as out:
    content = await file.read()  # async read
    await out.write(content)  # async write

  song_name = filename[:len(filename)-4]
  song_dir = "{dir1}/{dir2}".format(dir1 = OUTPUT_ROOT_PATH, dir2 = song_name)
  createDirIfNotExists(song_dir) # TODO: handle/warn when folder exists
  
  # create wav
  wav_path = createWavFromMp3(filename, UPLOAD_ROOT_PATH, song_dir)

  # create off vocal
  filepath_off_vocal = "{dir}/{filename}".format(
    dir = song_dir,
    filename = song_name + OFF_VOCAL_SUFFIX + AUDIO_FILE_EXTENSION
  )
  get_off_vocal.createOffVocal(wav_path, filepath_off_vocal) # needs wav

  return {
    ON_VOCAL_RETURN_KEY_NAME: "/" + wav_path,
    OFF_VOCAL_RETURN_KEY_NAME: "/" + filepath_off_vocal
  }


@app.post("/get-shifted-audio/")
async def getShiftedAudio(request: GetShiftedAudioRequest):
  validateDirectories()

  wav_path = request.wav_path[1:]
  shift_semitones = request.shift_semitones

  song_filename = os.path.basename(wav_path)
  song_name = song_filename[:len(song_filename)-4]
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
  createDirIfNotExists(shift_directory)
  
  # TODO: make on and off vocal concurrent?
  # shift on-vocal
  output_path_on_vocal = "{dir}/{filename}".format(
    dir = shift_directory,
    filename = shifted_song_name_on_vocal + AUDIO_FILE_EXTENSION
  )
  pitch_shift.shiftAudio(wav_path, output_path_on_vocal, shift_semitones)

  # shift off-vocal
  path_off_vocal = "{dir1}/{dir2}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    filename = song_name + AUDIO_FILE_EXTENSION
  )
  output_path_off_vocal = "{dir}/{filename}".format(
    dir = shift_directory,
    filename = shifted_song_name_off_vocal + AUDIO_FILE_EXTENSION
  )
  pitch_shift.shiftAudio(path_off_vocal, output_path_off_vocal, shift_semitones)

  return {
    ON_VOCAL_RETURN_KEY_NAME: "/" + output_path_on_vocal,
    OFF_VOCAL_RETURN_KEY_NAME: "/" + output_path_off_vocal
  }