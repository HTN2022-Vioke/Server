import datetime # for test code only
import utils
import pyrubberband as pyrb
import soundfile as sf

# has to be wav, which is fine since the off vocal is always returned as wav
def shift_audio(filepath, output_path, shift_semitones):
  data, sample_rate = sf.read(filepath)
  data_shift = pyrb.pitch_shift(data, sample_rate, shift_semitones)
  utils.writeWaveformArrToWav(data_shift, output_path, sample_rate)

# test code
# start = datetime.datetime.now()
# shiftAudio("let_it_go_off_vocal.wav", "let_it_go_off_vocal_-2.wav", -2)
# end = datetime.datetime.now()
# print("duration: " + str(end-start))
