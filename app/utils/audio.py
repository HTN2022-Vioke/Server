from pydub import AudioSegment

def createWavFromMp3(filename, file_directory, output_directory): # will be outputted to the same directory as the original
  assert(len(filename) > 3)
  sound = AudioSegment.from_mp3("{dir}/{filename}".format(dir = file_directory, filename = filename))
  filename_wav = filename[:len(filename)-3] + "wav"
  filepath_wav = "{dir}/{filename}".format(dir = output_directory, filename = filename_wav)
  sound.export(filepath_wav, format="wav")
  return filepath_wav
