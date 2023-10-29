
from audio_separator import Separator
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.utils import make_chunks
import datetime
import soundfile as sf
import utils.audio_utils as audio_utils
import wave
import os 

SLICE_SIZE_MS = 15 * 1000
TEMP_DIRECTORY = "temp" # make sure the temp folder exists
MODEL_NAME = "UVR_MDXNET_KARA_2"
NUM_THREADS = 8

def createOffVocal(filepath, output_path): # must be wav
  separator = Separator(filepath, model_name=MODEL_NAME)
  inst_path, vocal_path = separator.separate()
  os.remove(vocal_path)
  os.rename(inst_path, output_path)
  
# test code
start = datetime.datetime.now()
song = "hc"
# convert to wav
sound = AudioSegment.from_mp3("{song}.mp3".format(song=song))
sound.export("{song}.wav".format(song=song), format="wav")
createOffVocal("{song}.wav".format(song=song), "outputs/{song}_off_vocal.wav".format(song=song))
end = datetime.datetime.now()
print("duration: " + str(end-start))
