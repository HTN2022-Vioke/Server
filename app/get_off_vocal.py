
from audio_separator import Separator
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.utils import make_chunks
import datetime
import joblib
import soundfile as sf
import utils.audio_utils as audio_utils
import wave

SLICE_SIZE_MS = 15 * 1000
TEMP_DIRECTORY = "temp" # make sure the temp folder exists
MODEL_NAME = "UVR_MDXNET_KARA_2"
NUM_THREADS = 8

def createOffVocal(filepath, output_path): # must be wav
  f = sf.SoundFile(filepath)
  sample_rate = f.samplerate

  audio = AudioSegment.from_file(filepath , "wav")
  chunks = make_chunks(audio, SLICE_SIZE_MS)

  in_files = list()
  
  with joblib.parallel_backend("loky", inner_max_num_threads=NUM_THREADS):
    in_files = joblib.Parallel(n_jobs=NUM_THREADS)(\
      joblib.delayed(processChunk)(i, chunk) for i, chunk in enumerate(chunks))
  
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
  
  
# returns the path to the off vocal wav of the given chunk
def processChunk(idx, chunk): # has to be wav
  chunk_path = "{dir}/chunk{idx}.wav".format(dir = TEMP_DIRECTORY, idx = idx)
  chunk.export(chunk_path, format="wav")
  separator = Separator(chunk_path, model_name=MODEL_NAME)
  inst_path, _ = separator.separate()
  # audio_separator's default saving path
  # chunk_path_off_vocal = "{dir}/chunk{idx}_(Instrumental)_{model}.wav"\
  #   .format(dir = TEMP_DIRECTORY, idx = idx, model=MODEL_NAME)
  return inst_path
  

# test code
start = datetime.datetime.now()
song = "lig"
# convert to wav
sound = AudioSegment.from_mp3("{song}.mp3".format(song=song))
sound.export("{song}.wav".format(song=song), format="wav")
createOffVocal("{song}.wav".format(song=song), "{song}_off_vocal.wav".format(song=song))
end = datetime.datetime.now()
print("duration: " + str(end-start))
