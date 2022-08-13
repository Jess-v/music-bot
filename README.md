![Docker Pulls](https://img.shields.io/docker/pulls/jessvv/music-bot?style=for-the-badge) ![Docker Stars](https://img.shields.io/docker/stars/jessvv/music-bot?style=for-the-badge) ![Latest Image Version](https://img.shields.io/docker/v/jessvv/music-bot?style=for-the-badge)

# music-bot
This is a Dockerized Discord music bot based upon Python and the [discord.py](https://discordpy.readthedocs.io/en/stable/) library. 

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
