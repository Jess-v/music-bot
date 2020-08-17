# music-bot
Python-based discord music bot

## Installation
This will be assuming that you are running the bot on an Ubuntu-based Linux distribution. Instructions may need to be adjusted if using other distributions or another OS.
### Prerequisites
- Python 3.5.3 or later
- libffi
- libnacl
- python3-dev
- ffmpeg

>sudo apt install libffi-dev libnacl-dev python3-dev ffmpeg

### Python Packages
- discord.py[voice]
- youtube_dl
- asyncio

>pip3 install discord.py[voice] youtube_dl asyncio
or
>pip3 install -r requirements.txt

### Generate config.py
In the root directory create file named config.py

Edit the following and paste into the file:
>token = "place_token_here"
