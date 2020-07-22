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


async def client_in_channel(ctx):
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)
    try:
        if not voice.is_connected():
            await ctx.send("im not in voice dummy")
            return False
    except:
        await ctx.send("im not in voice dummy")
        return False
    try:
        user_channel = ctx.message.author.voice.channel
    except:
        await ctx.send("ur not even in voice shut up")
        return False
    bot_channel = voice.channel
    if user_channel != bot_channel:
        await ctx.send("im not even in ur channel??")
        return False
    return True
    

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.load_extension('cogs.music')

bot.run(config.token)

