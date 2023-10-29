
from audio_separator import Separator
import os 
# --- test code
# from pydub import AudioSegment
# from pydub import AudioSegment
# import datetime

MODEL_NAME = "UVR_MDXNET_KARA_2"

def createOffVocal(filepath, output_path): # must be wav
  separator = Separator(filepath, model_name=MODEL_NAME)
  inst_path, vocal_path = separator.separate()
  os.remove(vocal_path)
  os.rename(inst_path, output_path)
  
# --- test code
# start = datetime.datetime.now()
# song = "hc"
# # convert to wav
# sound = AudioSegment.from_mp3("{song}.mp3".format(song=song))
# sound.export("{song}.wav".format(song=song), format="wav")
# createOffVocal("{song}.wav".format(song=song), "outputs/{song}_off_vocal.wav".format(song=song))
# end = datetime.datetime.now()
# print("duration: " + str(end-start))
