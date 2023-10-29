import redis
from os import getenv
from db_models import Session, Audio
from models import Session as SessionModel

"""
session:{uuid}: {
    audioUuid: string
    curKeyShift: int
    hasVocal: bool
    timestamp: int
}

audio:{uuid}: {
    name: string
    lrc: string
    vocal: string
    offVocal: string
}
"""

r = redis.Redis.from_url(getenv("REDIS_URL"))

# r.hset("session:123", mapping={
#     "lrc": "lig.lrc",
#     "audio": "lig-nv.wav",
#     "timestamp": 1234,
# })

def new_session():
    session = Session()
    upsert_session(session)
    return session

def upsert_session(session: SessionModel):
    r.hset(f"session:{session.uuid}", mapping={
        "audioUuid": session.audio.uuid if session.audio.uuid is not None else 'null',
        "curKeyShift": session.cur_key_shift if session.cur_key_shift is not None else 'null',
        "hasVocal": str(session.has_vocal) if session.has_vocal is not None else 'null',
        "timestamp": session.timestamp if session.timestamp is not None else 'null',
    })

    r.hset(f"audio:{session.audio.uuid}", mapping={
        "name": session.audio.name if session.audio.name is not None else 'null',
        "lrcFile": session.audio.lrc_file if session.audio.lrc_file is not None else 'null',
    })
    print(session.audio)
    print(session)

def remove_session(session_uuid: str):
    return r.delete(f"session:{session_uuid}")

def get_session(session_uuid: str):
    session_dict = r.hgetall(f"session:{session_uuid}")
    session_dict = { k.decode(): v.decode() if v.decode() != "null" else None for k, v in session_dict.items()}
    session_dict["uuid"] = session_uuid
    print(session_dict)
    if "audioUuid" not in session_dict:
        return Session.from_dict(session_dict)
    audio_dict = r.hgetall(f"audio:{session_dict['audioUuid']}")
    audio_dict = { k.decode(): v.decode() if v.decode() != "null" else None for k, v in audio_dict.items()}
    audio_dict["uuid"] = session_dict["audioUuid"]
    session_dict["audio"] = audio_dict
    print(session_dict)
    return Session.from_dict(session_dict)
