import discord
from discord.ext import commands
import config


bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.load_extension('cogs.music')

bot.run(config.token)

