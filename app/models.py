from pydantic import BaseModel
from typing import Union

class Audio(BaseModel):
    uuid: Union[str, None]
    lrc_file: Union[str, None]
    vocal_file: Union[str, None]
    off_vocal_file: Union[str, None]
    name: Union[str, None]

class Session(BaseModel):
    uuid: str
    audio: Audio
    timestamp: int
    cur_key_shift: int
    has_vocal: bool
