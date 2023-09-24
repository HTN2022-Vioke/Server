import redis
from session import Session

"""
session:{uuid}: {
    lrc: string
    audio: string
    timestamp: int    
}
"""

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# r.hset("session:123", mapping={
#     "lrc": "lig.lrc",
#     "audio": "lig-nv.wav",
#     "timestamp": 1234,
# })

async def new_session(lrc = "", audio = "", timestamp = 0):
    session = Session(lrc=lrc, audio=audio, timestamp=timestamp)
    await r.hset(f"session:{session.uuid}", mapping=session.get_data())
    return session

def update_session(session: Session):
    return r.hset(f"session:{session.uuid}", mapping=session.get_data())


def remove_session(session_uuid: str):
    return r.delete(f"session:{session_uuid}")

async def get_session(session_uuid: str):
    session_dict = await r.hgetall(f"session:{session_uuid}")
    return Session(
        uuid=session_dict["uuid"],
        lrc=session_dict["lrc"],
        audio=session_dict["audio"],
        timestamp=int(session_dict["timestamp"]),
    )
