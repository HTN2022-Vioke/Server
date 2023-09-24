make sure to have ffmpeg installed
https://www.ffmpeg.org/download.html#build-windows

get models
https://github.com/deezer/spleeter/releases

@article{spleeter2020,
  doi = {10.21105/joss.02154},
  url = {https://doi.org/10.21105/joss.02154},
  year = {2020},
  publisher = {The Open Journal},
  volume = {5},
  number = {50},
  pages = {2154},
  author = {Romain Hennequin and Anis Khlif and Felix Voituret and Manuel Moussallam},
  title = {Spleeter: a fast and efficient music source separation tool with pre-trained models},
  journal = {Journal of Open Source Software},
  note = {Deezer Research}
}

spleeter cant be added to poetry for some reason, so dont forget to install that

needs keras-2.6.0

python = ">=3.9, <3.11"
librosa = "^0.8.0"
fastapi = "^0.85.0"
uvicorn = "^0.18.3"
SoundFile = "^0.10.3.post1"
pydub = "^0.25.1"