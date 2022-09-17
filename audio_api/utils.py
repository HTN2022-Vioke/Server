from pydub import AudioSegment
from scipy.io.wavfile import read as read_wav
from scipy.io.wavfile import write
import numpy as np
import soundfile as sf

def getSampleRate(filepath): # has to be wav
  sample_rate, _ = read_wav(filepath)
  return sample_rate

def getDuration(filepath): # has to be wav
  f = sf.SoundFile(filepath)
  print('samples = {}'.format(f.frames))
  print('sample rate = {}'.format(f.samplerate))

  print('seconds = {}'.format(f.frames / f.samplerate))

def createWavFromMp3(filepath): # will be outputted to the same directory as the original
  assert(len(filepath) > 3)
  sound = AudioSegment.from_mp3(filepath)
  filepath_wav = filepath[:len(filepath)-3] + "wav"
  sound.export(filepath_wav, format="wav")
  return filepath_wav

def writeWaveformArrToWav(waveform_arr, output_path, sample_rate):
  write(output_path, sample_rate, np.int16(waveform_arr * 32767))