
from audio_separator import Separator
import os

MODEL_NAME = "UVR_MDXNET_KARA_2"

def createOffVocal(filepath, output_path): # must be wav
  separator = Separator(filepath, model_name=MODEL_NAME)
  inst_path, vocal_path = separator.separate()
  os.remove(vocal_path)
  os.rename(inst_path, output_path)

