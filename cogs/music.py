import asyncio
import discord
import os
import youtube_dl
from bot.music import Queue, Song
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from typing import List


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}

    @commands.command()
    async def play(self, ctx: discord.ext.commands.Context, url: str, *args: str):
        '''Adds a song to the queue either by YouTube URL or YouTube Search.'''

        music_queue = self.music_queues.get(ctx.guild, None)
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if music_queue is None:
            music_queue = Queue()
            self.music_queues[ctx.guild] = music_queue

        try:
            channel = ctx.message.author.voice.channel
        except:
            await ctx.send("You're not connected to a voice channel.")
            return

        if voice is not None and not self.client_in_same_channel(ctx.message.author, voice):
            await ctx.send("You're not in my voice channel.")
            return

        if 'https://' not in url:
            url = 'ytsearch1:' + url + ' ' + f'{" ".join(args)}'

        song = Song(url, ctx.author)
        valid_song, song_err = self.song_error_check(song)

        if not valid_song:
            await ctx.send(song_err)
            return

        if voice is None or not voice.is_connected():
            await channel.connect()
            voice = get(self.bot.voice_clients, guild=ctx.guild)

        music_queue.append(song)
        await ctx.send(f'Queued song: {song.title}')

        if not voice.is_playing():
            await self.play_song(voice, ctx.guild, music_queue.next_song())

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def stop(self, ctx):
        '''Admin command that stops playback of music and clears out the music queue.'''

        voice = self.get_voice(ctx)
        if self.client_in_same_channel(ctx, voice):
            voice.stop()
            self.queue_obj.clear()
            await ctx.send("Stopping playback")
        else:
            await ctx.send("You're not in a voice channel with me.")

    @commands.command()
    async def skip(self, ctx: discord.ext.commands.Context):
        '''Puts in your vote to skip the currently played song.'''

        voice = self.get_voice(ctx)
        if not self.client_in_same_channel(ctx, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        if not voice or not voice.is_playing():
            await ctx.send("I'm not playing a song right now.")
            return
        if ctx.author in self.skip_voters:
            await ctx.send("You've already voted to skip this song.")
            return
        channel = ctx.message.author.voice.channel
        required_votes = round(len(channel.members)/2)
        self.skip_votes += 1
        self.skip_voters.append(ctx.author)
        if self.skip_votes >= required_votes:
            await ctx.send('Skipping song after successful vote.')
            voice.stop()
            return
        else:
            await ctx.send(f'You voted to skip this song. {required_votes-self.skip_votes} more votes are required.')
            return

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def fskip(self, ctx):
        '''Admin command that forces skipping of the currently playing song.'''

        voice = self.get_voice(ctx)
        if not self.client_in_same_channel(ctx, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        if not voice or not voice.is_playing():
            await ctx.send("I'm not playing a song right now.")
            return
        voice.stop()
        return

    @commands.command()
    async def songinfo(self, ctx: discord.ext.commands.Context, song_index: int = 0):
        '''Print out more information on the song currently playing.'''

        queue = self.music_queues.get(ctx.guild)

        if song_index < 0 or song_index > (len(queue)) and song_index != 0:
            await ctx.send("A song does not exist at that index in the queue.")
            return
        
        embed = queue.get_embed(song_index)
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx: discord.ext.commands.Context, song_id: int = 0):
        '''Removes the last song you requested from the queue, or a specific song if queue position specified.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not self.client_in_same_channel(ctx.message.author, voice):
            await ctx.send("You're not in a voice channel with me.")
            return

        if song_id == 0:
            queue = self.music_queues.get(ctx.guild)

            for index, song in reversed(list(enumerate(queue))):
                if ctx.author.id == song.requested_by_id:
                    queue.pop(index)
                    await ctx.send(f'Song "{song.title}" removed from queue.')
                        return
        else:
            queue = self.music_queues.get(ctx.guild)
            song = queue[song_id-1]

            if ctx.author.id == song.requested_by_id:
                queue.pop(song_id-1)
                await ctx.send(f'Song {song.title} removed from queue.')
            else:
                await ctx.send('You cannot remove a song requested by someone else.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def fremove(self, ctx: discord.ext.commands.Context, song_id: int = 0):
        '''Admin command to forcibly remove a song from the queue by it's position.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        queue = self.music_queues.get(guild=ctx.guild)

        if not self.client_in_same_channel(ctx.message.author, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        
        if song_id == 0:
            await ctx.send("You need to specify a song by it's queue index.")
            return
        
        try:
            song = queue[song_id-1]
            song_title = song.title
        except:
            await ctx.send("A song does not exist at this queue index.")
            return
        
        queue.pop[song_id-1]
            await ctx.send(f"Removed {song_title} from the queue.")
            return

    @commands.command()
    async def queue(self, ctx: discord.ext.commands.Context, page: int = 1):
        '''Prints out a specified page of the music queue, defaults to first page.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        queue = self.music_queues.get(ctx.guild)

        if not self.client_in_same_channel(ctx.message.author, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        
        if len(queue) < 1:
            await ctx.send("I don't have anything in my queue right now.")
            return

        to_send = '```\n    Song                                                              Uploader              '\
                  '              Requested By               '
        start_index = (page-1)*10

        for index in range(start_index, start_index+10):
            try:
                song = queue[index]
            except:
                break
            
            if song is not None:
                queue_pos = str(index+1) + ')'
                title = song.title
                uploader = song.uploader
                requested_by = song.requested_by_username

                while len(queue_pos) < 4:
                    queue_pos = queue_pos + ' '

                if len(title) < 65:
                    while len(title) < 65:
                        title = title + ' '
                else:
                    title = title[:65]

                if len(uploader) < 35:
                    while len(uploader) < 35:
                        uploader = uploader + ' '
                else:
                    uploader = uploader[:35]
                
                to_send = to_send + f'\n{queue_pos}{title}|{uploader}|{requested_by}'

            else:
                break

        to_send = to_send + '\n```'
        await ctx.send(to_send)

    async def play_song(self, voice: List[discord.VoiceClient], guild: discord.Guild, song: Song):
        '''Downloads and starts playing a YouTube video's audio.'''

        queue = self.music_queues.get(guild)
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'./audio/{guild.id}.mp3',
        }

        if not os.path.exists('./audio'):
            os.makedirs('./audio')
        song_there = os.path.isfile(f"./audio/{guild.id}.mp3")

        if song_there:
            os.remove(f'./audio/{guild.id}.mp3')
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'{song.url}'])
        except:
                await self.process_queue(voice, guild)
                print('Error downloading song. Skipping.')
            return

        voice.play(discord.FFmpegPCMAudio(f"./audio/{guild.id}.mp3"))
        queue.clear_skip_votes()
        await self.process_queue(voice, guild)

    async def process_queue(self, voice: List[discord.VoiceClient], guild: discord.Guild):
        '''Continuously checks for the opportunity to play the next video.'''

        queue = self.music_queues.get(guild)

        while voice.is_playing():
            await asyncio.sleep(1)

        if len(queue) > 0:
            song = queue.next_song()
            await self.play_song(voice, guild, song)
        else:
            await self.inactivity_disconnect(voice, guild)

    async def inactivity_disconnect(self, voice: List[discord.VoiceClient], guild: discord.Guild):
        '''If a song is not played for 5 minutes, automatically disconnects bot from server.'''

        queue = self.music_queues.get(guild)
        last_song = queue.current_song

        await asyncio.sleep(300)
        if queue.current_song == last_song:
            await voice.disconnect()

    def get_voice(self, ctx):
        '''Simple function to return a voice object'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        return voice

    @staticmethod
    def client_in_same_channel(author: discord.Member, voice: List[discord.VoiceClient]):
        '''Checks to see if a client is in the same channel as the bot.'''

        try:
            channel = author.voice.channel
        except:
            return False
        
        if voice is not None and voice.is_connected() and channel == voice.channel:
            return True
        else:
            return False

    @staticmethod
    def song_error_check(song: Song):
        ''' Checks song properties to ensure that the song is both valid and doesn't match any filtered properties'''

        if song.url is None:
            return False, "Invalid URL provided or no video found."
        
        if song.get("is_live", True):
            return False, "Invalid video - either live stream or unsupported website."
        
        if song.duration_raw > 1200:
            return False, "Video is too long. Keep it under 20mins."
        
        return True, None


def setup(bot):
    bot.add_cog(Music(bot))
