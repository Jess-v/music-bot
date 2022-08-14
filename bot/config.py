import os
import sys

DISCORD_API_TOKEN = ""
DISCORD_COMMAND_PREFIX = "!"
MUSIC_MAX_DURATION_MINS = 20
MUSIC_QUEUE_PER_PAGE = 10

def load():
    if len(os.getenv("DISCORD_API_TOKEN")):
        print("Environment variable 'DISCORD_API_TOKEN' is required!")
        sys.exit(1)
    else:
        DISCORD_API_TOKEN = os.getenv('DISCORD_API_TOKEN')
    if len(os.getenv('DISCORD_COMMAND_PREFIX')) > 0:
        DISCORD_COMMAND_PREFIX = os.getenv('DISCORD_COMMAND_PREFIX')
    if len(os.getenv('MUSIC_MAX_DURATION_MINS')) > 0:
        MUSIC_MAX_DURATION_MINS = int(os.getenv('MUSIC_MAX_DURATION_MINS'))
    if len(os.getenv('MUSIC_QUEUE_PER_PAGE')) > 0:
        MUSIC_QUEUE_PER_PAGE = int(os.getenv('MUSIC_QUEUE_PER_PAGE'))
