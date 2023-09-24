FROM python:3.9-alpine3.17

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

COPY ./app /app
COPY ./assets /assets

WORKDIR /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
