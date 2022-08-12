# music-bot
Python-based discord music bot

## Deployment

Running this bot is very simple, first create a file containing your environment variables (I will be assuming it is named .env for this example) with the following contents:

```env
DISCORD_COMMAND_PREFIX=<your chosen character(s) for command prefix>
DISCORD_API_TOKEN=<your Discord API token>
```

Afterwards, just run `docker run --rm --env-file .env --name="music-bot" -d jessvv/music-bot:latest` to deploy the latest image build.

For more stable deployment, I recommend replacing `latest` with a specific version tag, which you can find [here](https://hub.docker.com/r/jessvv/music-bot/tags).
