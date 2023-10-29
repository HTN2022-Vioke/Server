from jose import jwt
from os import getenv
from utils.clocker import Clocker
from db_models import SessionPayload

JWT_ALGORITHM = "HS256"
JWT_SECRET = getenv("AUTH_JWT_KEY")

def create_jwt_token(payload: SessionPayload, exp="7d") -> str:
    return jwt.encode({ **payload.to_dict(), "exp": Clocker().add_time(exp).time }, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> SessionPayload:
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return SessionPayload(decoded["uuid"])
