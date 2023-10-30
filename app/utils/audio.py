from pydub import AudioSegment

def createWavFromMp3(song_name, mp3_path, output_directory): # will be outputted to the same directory as the original
  sound = AudioSegment.from_mp3(mp3_path)
  filepath_wav = f"{output_directory}/{song_name}" + ".wav"
  sound.export(filepath_wav, format="wav")
  return filepath_wav
