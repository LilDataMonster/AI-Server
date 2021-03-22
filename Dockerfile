FROM python:3.9-slim-buster

RUN apt-get update -y && \
    apt-get install -y ffmpeg libsm6 libxext6 \
	tesseract-ocr libtesseract-dev

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app/
