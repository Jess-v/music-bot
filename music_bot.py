from discord.ext import commands
import os
from bot import config

config.load()

bot = commands.Bot(command_prefix=config.DISCORD_COMMAND_PREFIX)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.load_extension('cogs.music')

bot.run(config.DISCORD_API_TOKEN)

