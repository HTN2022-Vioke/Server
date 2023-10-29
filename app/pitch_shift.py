from scipy.io.wavfile import write
import numpy as np
import pyrubberband as pyrb
import soundfile as sf

# has to be wav, which is fine since the off vocal is always returned as wav
def shift_audio(filepath, output_path, shift_semitones):
  data, sample_rate = sf.read(filepath)
  waveform_arr_shifted = pyrb.pitch_shift(data, sample_rate, shift_semitones)
  write(output_path, sample_rate, np.int16(waveform_arr_shifted * 32767))
