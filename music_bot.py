import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import config
import os
import random
import asyncio

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.load_extension('cogs.music')

bot.run(config.token)

