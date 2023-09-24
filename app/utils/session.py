from jose import jwt
from os import getenv
from uuid import uuid4
from utils.clocker import Clocker

JWT_ALGORITHM = "HS256"
JWT_SECRET = getenv("AUTH_JWT_KEY")

def create_jwt_token(payload, exp="7d"):
  return jwt.encode({ **payload, "exp": Clocker().add_time(exp).time }, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token):
  return jwt.decode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)

class Session:
    def __init__(
        self,
        uuid = uuid4().hex,
        lrc = "",
        audio = "",
        timestamp = 0
    ):
        self.uuid = uuid
        self.lrc = lrc
        self.audio = audio
        self.timestamp = timestamp

    def get_data(self):
        return {
            "lrc": self.lrc,
            "audio": self.audio,
            "timestamp": self.timestamp,
        }
