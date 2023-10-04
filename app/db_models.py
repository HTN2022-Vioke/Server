from uuid import uuid4
from typing import Dict, Any, Optional, Union


class SessionPayload:
    def __init__(self, uuid: str):
        self.uuid = uuid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
        }

class Audio:
    def __init__(
        self,
        name: Union[None, str] = None,
        uuid = uuid4().hex,
        lrc_file: Union[None, str] = None,
        vocal_file: Union[None, str] = None,
        off_vocal_file: Union[None, str] = None,
    ):
        self.uuid = uuid
        self.name = name
        self.lrc_file = lrc_file
        self.vocal_file = vocal_file
        self.off_vocal_file = off_vocal_file

    @classmethod
    def from_dict(
        cls,
        dict: Dict[str, Any],
    ):
        return cls(
            uuid = dict.get("uuid", None),
            lrc_file = dict.get("lrcFile", None),
            vocal_file = dict.get("vocalFile", None),
            off_vocal_file = dict.get("offVocalFile", None),
            name = dict.get("name", None)
        )

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "lrcFile": self.lrc_file,
            "vocalFile": self.vocal_file,
            "offVocalFile": self.off_vocal_file,
        }

class Session:
    def __init__(
        self,
        uuid = uuid4().hex,
        timestamp: Union[None, int] = None,
        cur_key_shift: Union[None, int] = None,
        has_vocal: Union[None, bool] = None,
        audio = Audio(),
    ):
        self.uuid = uuid
        self.audio = audio
        self.cur_key_shift = cur_key_shift
        self.has_vocal = has_vocal
        self.timestamp = timestamp

    @classmethod
    def from_dict(
        cls,
        dict: Dict[str, Any],
    ):
        
        return cls(
            uuid = dict.get("uuid", None),
            audio = Audio.from_dict(dict.get("audio", {})),
            cur_key_shift = dict.get("curKeyShift", None),
            has_vocal = dict.get("hasVocal", None),
            timestamp = dict.get("timestamp", None),
        )

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "audio": self.audio.to_dict() if self.audio is not None else None,
            "timestamp": self.timestamp,
            "curKeyShift": self.cur_key_shift,
            "hasVocal": self.has_vocal,
        }
