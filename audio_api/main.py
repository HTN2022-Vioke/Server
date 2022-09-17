from fastapi import FastAPI, UploadFile
import aiofiles
import get_off_vocal

OFF_VOCAL_EXTENSION = ".wav"
OFF_VOCAL_PATH = "off_vocals"
UPLOAD_FILE_PATH = "uploads"

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "home"}

@app.post("/upload/")
async def upload(file: UploadFile):
  # store to local
  filename = file.filename
  filepath = "{dir}/{filename}".format(dir = UPLOAD_FILE_PATH, filename = filename)
  async with aiofiles.open(filepath, 'wb') as out:
    content = await file.read()  # async read
    await out.write(content)  # async write

  # create off vocal
  filepath_off_vocal = "{dir}/{filename}".format(dir = OFF_VOCAL_PATH, filename = file.filename[:len(filename)-4] + OFF_VOCAL_EXTENSION)
  get_off_vocal.createOffVocal(filepath, filepath_off_vocal) # assuming input is always mp3

  # send url to off vocal
  return {"response": filepath_off_vocal}