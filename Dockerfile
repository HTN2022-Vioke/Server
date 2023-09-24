FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt

ENV DEBIAN_FRONTEND noninteractive
RUN apt update
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

WORKDIR /code/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
