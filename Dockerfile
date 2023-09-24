FROM python:3.8-alpine3.17

COPY requirements.txt requirements.txt

RUN apk update && apk add ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app
COPY ./assets /assets

WORKDIR /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
