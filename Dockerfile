FROM python:3.12.2-slim-bullseye

WORKDIR /app

COPY . .

RUN apt update && apt install libffi-dev libnacl-dev ffmpeg -y

RUN pip3 install -r requirements.txt

CMD ["python3", "./music_bot.py"]