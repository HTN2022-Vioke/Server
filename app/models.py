from pydantic import BaseModel
from typing import Union

class Audio(BaseModel):
    uuid: Union[str, None]
    lrc_file: Union[str, None]
    name: Union[str, None]

class Session(BaseModel):
    uuid: str
    audio: Audio
    timestamp: float
    cur_key_shift: int
    has_vocal: bool

class GetAudioFile(BaseModel):
    name: str
    has_vocal: bool
    cur_key_shift: int
