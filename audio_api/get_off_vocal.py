from pydub import AudioSegment
from pydub.utils import make_chunks
from scipy.io.wavfile import read as read_wav
from scipy.io.wavfile import write
from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator
import numpy as np
import os
import soundfile as sf
import wave 

import datetime

AUDIO_LOADER = AudioAdapter.default()
OUTPUT_DIRECTORY = "output"
SEPARATOR = Separator('spleeter:2stems')
SLICE_SIZE_MS = 30 * 1000
TEMP_DIRECTORY = "temp"

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


def createOffVocal(filepath, output_path, is_mp3=True): # make sure the temp folder exists
  # convert to wav if needed
  if is_mp3:
    filepath_wav = createWavFromMp3(filepath)
  else:
    filepath_wav = filepath

  f = sf.SoundFile(filepath_wav)
  sample_rate = f.samplerate

  audio = AudioSegment.from_file(filepath_wav , "wav")
  chunks = make_chunks(audio, SLICE_SIZE_MS)

  in_files = list()
  for i, chunk in enumerate(chunks):
    chunk_path = "{dir}/chunk{n}.wav".format(dir = TEMP_DIRECTORY, n = i)
    chunk.export(chunk_path, format="wav")

    chunk_path_off_vocal = "{dir}/chunk{n}_off_vocal.wav".format(dir = TEMP_DIRECTORY, n = i)
    data = getOffVocalWaveformArr(chunk_path, sample_rate)
    write(chunk_path_off_vocal, sample_rate, np.int16(data * 32767))
    in_files.append(chunk_path_off_vocal)
  
  data= []
  for in_file in in_files:
    w = wave.open(in_file, 'rb')
    data.append( [w.getparams(), w.readframes(w.getnframes())] )
    w.close()
    
  output = wave.open(output_path, 'wb')
  output.setparams(data[0][0])
  for i in range(len(data)):
    output.writeframes(data[i][1])
  output.close()

  # if is_mp3:
  #   os.remove(filepath_wav)
  
  
def getOffVocalWaveformArr(filepath, sample_rate): # has to be wav
  waveform, _ = AUDIO_LOADER.load(filepath, sample_rate=sample_rate)
  prediction = SEPARATOR.separate(waveform)
  return prediction["accompaniment"]

# test code
# start = datetime.datetime.now()
# createOffVocal("let_it_go.mp3", "ligoff.wav")
# end = datetime.datetime.now()
# print("duration: " + str(end-start))