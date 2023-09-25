import pyrubberband as pyrb
import soundfile as sf
import utils.audio_utils as audio_utils

# has to be wav, which is fine since the off vocal is always returned as wav
def shift_audio(filepath, output_path, shift_semitones):
  data, sample_rate = sf.read(filepath)
  data_shift = pyrb.pitch_shift(data, sample_rate, shift_semitones)
  audio_utils.writeWaveformArrToWav(data_shift, output_path, sample_rate)
