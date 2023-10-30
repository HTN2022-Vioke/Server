from audio_separator import Separator
from pydub import AudioSegment
from scipy.io.wavfile import write
import numpy as np
import os
import pyrubberband as pyrb
import soundfile as sf

OFF_VOCAL_MODEL_NAME = "UVR_MDXNET_KARA_2"

def createWavFromMp3(song_name, mp3_path, output_directory): # will be outputted to the same directory as the original
  sound = AudioSegment.from_mp3(mp3_path)
  filepath_wav = f"{output_directory}/{song_name}" + ".wav"
  sound.export(filepath_wav, format="wav")
  return filepath_wav

def createOffVocal(filepath, output_path): # must be wav
  separator = Separator(filepath, model_name=OFF_VOCAL_MODEL_NAME)
  try:
    inst_path, vocal_path = separator.separate()
    os.rename(inst_path, output_path)
  except:
    if os.path.isfile(output_path):
      os.remove(inst_path)
  finally:
    os.remove(vocal_path)

# has to be wav, which is fine since the off vocal is always returned as wav
def shift_audio(filepath, output_path, shift_semitones):
  data, sample_rate = sf.read(filepath)
  waveform_arr_shifted = pyrb.pitch_shift(data, sample_rate, shift_semitones)
  try:
    write(output_path, sample_rate, np.int16(waveform_arr_shifted * 32767))
  except:
    if os.path.isfile(output_path):
      os.remove(output_path)
