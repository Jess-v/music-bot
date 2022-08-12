FROM python:3.8.13-slim-bullseye

WORKDIR /app

COPY . .

RUN apt update && apt install libffi-dev libnacl-dev ffmpeg -y

RUN pip3 install -r requirements.txt

CMD ["python3", "./music_bot.py"]