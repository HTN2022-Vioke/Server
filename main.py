from audio_api import get_off_vocal, pitch_shift
from audio_api.utils import createWavFromMp3
from fastapi import FastAPI, UploadFile
import aiofiles

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

AUDIO_FILE_EXTENSION = ".wav"
OFF_VOCAL_RETURN_KEY_NAME = "audioNvUrl"
OFF_VOCAL_SUFFIX = "_off_vocal"
ON_VOCAL_RETURN_KEY_NAME = "audioUrl"
OUTPUT_ROOT_PATH = "outputs"
SHIFT_DIRECTORY = "shifted"
UPLOAD_ROOT_PATH = "uploads"

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "home"}

@app.post("/get-off-vocal/")
async def getOffVocal(file: UploadFile): # assume mp3
  # store mp3 file to uploads folder
  filename = file.filename
  filepath = "{dir}/{filename}".format(dir = UPLOAD_ROOT_PATH, filename = filename)
  async with aiofiles.open(filepath, 'wb') as out:
    content = await file.read()  # async read
    await out.write(content)  # async write

  song_name = filename[:len(filename)-3]

  # create wav
  wav_dir = "{dir1}/{dir2}".format(dir1 = OUTPUT_ROOT_PATH, dir2 = song_name)
  wav_path = createWavFromMp3(filename, UPLOAD_ROOT_PATH, wav_dir)

  # create off vocal
  filepath_off_vocal = "{dir1}/{dir2}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = filename,
    filename = file.filename[:len(filename)-4] + AUDIO_FILE_EXTENSION
  )
  get_off_vocal.createOffVocal(wav_dir, filepath_off_vocal) # needs wav

  return {
    ON_VOCAL_RETURN_KEY_NAME: wav_path,
    OFF_VOCAL_RETURN_KEY_NAME: filepath_off_vocal
  }


@app.post("/get-shifted-audio/")
async def getShiftedAudio(original_filename: str, shift_semitones: int):
  song_name = original_filename[:len(original_filename)-4]
  shifted_song_name = "{name}_{shift}".format(song_name, shift_semitones)

  # TODO: make on and off vocal concurrent?
  path_on_vocal = "{dir1}/{dir2}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    filename = song_name + AUDIO_FILE_EXTENSION
  )

  output_path_on_vocal = "{dir1}/{dir2}/{dir3}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    dir3 = SHIFT_DIRECTORY,
    filename = shifted_song_name + AUDIO_FILE_EXTENSION
  )
  pitch_shift.shiftAudio(path_on_vocal, output_path_on_vocal, shift_semitones)

  path_off_vocal = "{dir1}/{dir2}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    filename = song_name + OFF_VOCAL_SUFFIX + AUDIO_FILE_EXTENSION
  )
  output_path_off_vocal = "{dir1}/{dir2}/{dir3}/{filename}".format(
    dir1 = OUTPUT_ROOT_PATH,
    dir2 = song_name,
    dir3 = SHIFT_DIRECTORY,
    filename = shifted_song_name + OFF_VOCAL_SUFFIX + AUDIO_FILE_EXTENSION
  )
  pitch_shift.shiftAudio(path_off_vocal, output_path_off_vocal, shift_semitones)

  return {
    ON_VOCAL_RETURN_KEY_NAME: output_path_on_vocal,
    OFF_VOCAL_RETURN_KEY_NAME: output_path_off_vocal
  }