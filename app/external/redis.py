import redis
from os import getenv
from utils.session import Session

"""
session:{uuid}: {
    lrc: string
    audio: string
    timestamp: int    
}
"""

r = redis.Redis.from_url(getenv("REDIS_URL"))

# r.hset("session:123", mapping={
#     "lrc": "lig.lrc",
#     "audio": "lig-nv.wav",
#     "timestamp": 1234,
# })

def new_session(lrc = "", audio = "", timestamp = 0):
    session = Session(lrc=lrc, audio=audio, timestamp=timestamp)
    r.hset(f"session:{session.uuid}", mapping=session.get_data())
    return session

def update_session(session: Session):
    return r.hset(f"session:{session.uuid}", mapping=session.get_data())

def remove_session(session_uuid: str):
    return r.delete(f"session:{session_uuid}")

def get_session(session_uuid: str):
    session_dict = r.hgetall(f"session:{session_uuid}")
    return Session(
        uuid=session_dict["uuid"],
        lrc=session_dict["lrc"],
        audio=session_dict["audio"],
        timestamp=int(session_dict["timestamp"]),
    )
