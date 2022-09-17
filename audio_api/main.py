from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "home"}

@app.post("/upload/")
async def upload(file: UploadFile):
  return {"filename": file.filename, "content_type": file.content_type, "file": file}