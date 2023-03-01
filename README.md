![Build](https://img.shields.io/github/actions/workflow/status/Jess-v/music-bot/build-publish.yaml) 
![Latest Version](https://img.shields.io/docker/v/jessvv/music-bot?sort=semver)
![Image Pulls](https://img.shields.io/docker/pulls/jessvv/music-bot)
![Docker Stars](https://img.shields.io/docker/stars/jessvv/music-bot)
![Image Size](https://img.shields.io/docker/image-size/jessvv/music-bot)

# music-bot
This is a Dockerized Discord music bot based upon Python and the [discord.py](https://discordpy.readthedocs.io/en/stable/) library. 

## Environment Variables

| Variable                 | Default | Description                                                           | Required? |
|--------------------------|---------|-----------------------------------------------------------------------|-----------|
| `DISCORD_COMMAND_PREFIX` | `!`     | Character(s) that each bot command will be prefixed with              | `False`   |
| `DISCORD_API_TOKEN`      | `None`  | Discord Bot Auth Token                                                | `True`    |
| `MUSIC_MAX_DURATION_MINS`| `20`    | The maximum length in minutes of a video that is allowed to be played | `False`   |
| `MUSIC_QUEUE_PER_PAGE`   | `10`    | The number of songs that appear in each page of the queue             | `False`   |

## Setup

You will need to create an env file (or optionally you can pass your environment variables through CLI). Assuming you'll be naming your env file `.env`, it will need to contain the following:

```env
DISCORD_COMMAND_PREFIX=<your chosen character(s) for command prefix>
DISCORD_API_TOKEN=<your Discord API token>
```

If you do not yet have a Discord API token, the discord.py team has a [guide on how to generate one](https://discordpy.readthedocs.io/en/stable/discord.html).

Once you have completed those steps, run the image like this:

```bash
docker run --rm --env-file .env --name="music-bot" -d jessvv/music-bot:latest
```

For more stable deployment, I recommend replacing `latest` with a specific version tag, which you can find [here](https://hub.docker.com/r/jessvv/music-bot/tags).
