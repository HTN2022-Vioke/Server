from fastapi import FastAPI, UploadFile, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel


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


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.middleware("http")
async def create_session_if_not_exist(request: Request, call_next):
    session_jwt = request.cookies.get("session")
    if request.url.path not in protected_paths[request.method]:
        return await call_next(request)
    if session_jwt is None:
        # create new session
        session_obj = redis.new_session()
        token = session.create_jwt_token({"uuid": session_obj.uuid})
        request.cookies["session"] = token
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
    session_jwt = request.cookies.get("session")
    if session_jwt is None:
        return JSONResponse({"message": "no session"})
    session = await redis.get_session(session.decode_jwt_token(session_jwt)["uuid"])
    return JSONResponse(session.get_data())

