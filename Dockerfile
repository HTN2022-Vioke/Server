FROM python:3.9

# Install dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt-get -y upgrade \
  && apt-get install -y build-essential ffmpeg lbzip2 ninja-build libsndfile1-dev pkg-config \
  && rm -rf /var/lib/apt/lists/*
RUN pip install meson

# Download and unpack the rubberband source code
ADD https://breakfastquay.com/files/releases/rubberband-3.3.0.tar.bz2 /
RUN tar -xf /rubberband-3.3.0.tar.bz2
RUN ls
RUN cd rubberband-3.3.0 && ls

# Build the Rubber Band library using Meson and Ninja, and add the binary to PATH
WORKDIR /rubberband-3.3.0
RUN meson setup build && ninja -C build \
  && cp build/rubberband /usr/local/bin/

# Install pip requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Launch the app
COPY ./app /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
