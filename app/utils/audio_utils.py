# from pydub import AudioSegment
# from scipy.io.wavfile import read as read_wav
# from scipy.io.wavfile import write
# import numpy as np
# import soundfile as sf

# def getSampleRate(filepath): # has to be wav
#     sample_rate, _ = read_wav(filepath)
#     return sample_rate

# def getDuration(filepath): # has to be wav
#     f = sf.SoundFile(filepath)
#     print('samples = {}'.format(f.frames))
#     print('sample rate = {}'.format(f.samplerate))

#     print('seconds = {}'.format(f.frames / f.samplerate))

# def createWavFromMp3(filename, file_directory, output_directory): # will be outputted to the same directory as the original
#     assert(len(filename) > 3)
#     sound = AudioSegment.from_mp3("{dir}/{filename}".format(dir = file_directory, filename = filename))
#     filename_wav = filename[:len(filename)-3] + "wav"
#     filepath_wav = "{dir}/{filename}".format(dir = output_directory, filename = filename_wav)
#     sound.export(filepath_wav, format="wav")
#     return filepath_wav

# def writeWaveformArrToWav(waveform_arr, output_path, sample_rate):
#   write(output_path, sample_rate, np.int16(waveform_arr * 32767))

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
