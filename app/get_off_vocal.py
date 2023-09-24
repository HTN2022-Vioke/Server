# import datetime # for test code only
# import utils
# from pydub import AudioSegment
# from pydub.utils import make_chunks
# from spleeter.audio.adapter import AudioAdapter
# from spleeter.separator import Separator
# import soundfile as sf
# import wave

# AUDIO_LOADER = AudioAdapter.default()
# SEPARATOR = Separator('spleeter:2stems')
# SLICE_SIZE_MS = 30 * 1000
# TEMP_DIRECTORY = "temp" # make sure the temp folder exists

# def createOffVocal(filepath, output_path): # must be wav
#   f = sf.SoundFile(filepath)
#   sample_rate = f.samplerate

#   audio = AudioSegment.from_file(filepath , "wav")
#   chunks = make_chunks(audio, SLICE_SIZE_MS)

#   in_files = list()
#   for i, chunk in enumerate(chunks):
#     chunk_path = "{dir}/chunk{n}.wav".format(dir = TEMP_DIRECTORY, n = i)
#     chunk.export(chunk_path, format="wav")

#     chunk_path_off_vocal = "{dir}/chunk{n}_off_vocal.wav".format(dir = TEMP_DIRECTORY, n = i)
#     data = getOffVocalWaveformArr(chunk_path, sample_rate)
#     writeWaveformArrToWav(data, chunk_path_off_vocal, sample_rate)
#     in_files.append(chunk_path_off_vocal)
  
#   data= []
#   for in_file in in_files:
#     w = wave.open(in_file, 'rb')
#     data.append( [w.getparams(), w.readframes(w.getnframes())] )
#     w.close()
    
#   output = wave.open(output_path, 'wb')
#   output.setparams(data[0][0])
#   for i in range(len(data)):
#     output.writeframes(data[i][1])
#   output.close()
  
  
# def getOffVocalWaveformArr(filepath, sample_rate): # has to be wav
#   waveform, _ = AUDIO_LOADER.load(filepath, sample_rate=sample_rate)
#   prediction = SEPARATOR.separate(waveform)
#   return prediction["accompaniment"]

# test code
# start = datetime.datetime.now()
# # convert to wav
# sound = AudioSegment.from_mp3("syl.mp3")
# sound.export("syl.wav", format="wav")
# createOffVocal("syl.wav", "syl_off_vocal.wav")
# end = datetime.datetime.now()
# print("duration: " + str(end-start))
