from discord.ext import commands
import os

prefix = os.getenv('DISCORD_COMMAND_PREFIX')
apiToken = os.getenv('DISCORD_API_TOKEN')


bot = commands.Bot(command_prefix=prefix)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.load_extension('cogs.music')

bot.run(apiToken)

