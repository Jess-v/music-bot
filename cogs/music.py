import asyncio
import discord
import os
import youtube_dl
from bot.music import Queue, Song
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from typing import List


# 20 minutes, in seconds
DURATION_CEILING = 20 * 60

SONGS_PER_PAGE = 10


def set_str_len(s: str, lower_limit: int = None, upper_limit: int = None):
    '''Pad string if shorter than lower_limit and/or trim string if longer than upper_limit'''

    assert lower_limit <= upper_limit, f'set_str_len bounds invalid: attempted range {lower_limit} <= {upper_limit}'

    # Extend
    if lower_limit is not None:
        s = f'{s:<{lower_limit}}'

    # Strip
    if upper_limit is not None:
        s = s[:upper_limit]

    return s


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

        if not url.startswith('https://'):
            url = f'ytsearch1:{url} {" ".join(args)}'

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

        await self.play_all_songs()
        if not voice.is_playing():
            await self.play_song(voice, ctx.guild, music_queue.next_song())

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def stop(self, ctx: discord.ext.commands.Context):
        '''Admin command that stops playback of music and clears out the music queue.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        queue = self.music_queues.get(ctx.guild)

        if self.client_in_same_channel(ctx.message.author, voice):
            voice.stop()
            queue.clear()
            await ctx.send("Stopping playback")
            await voice.disconnect()
        else:
            await ctx.send("You're not in a voice channel with me.")

    @commands.command()
    async def skip(self, ctx: discord.ext.commands.Context):
        '''Puts in your vote to skip the currently played song.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        queue = self.music_queues.get(ctx.guild)

        if not self.client_in_same_channel(ctx.message.author, voice):
            await ctx.send("You're not in a voice channel with me.")
            return

        if voice is None or not voice.is_playing():
            await ctx.send("I'm not playing a song right now.")
            return

        if ctx.author in queue.skip_voters:
            await ctx.send("You've already voted to skip this song.")
            return

        channel = ctx.message.author.voice.channel
        required_votes = round(len(channel.members)/2)

        queue.add_skip_vote(ctx.author.name)
        voters = queue.skip_voters

        if len(voters) >= required_votes:
            await ctx.send('Skipping song after successful vote.')
            voice.stop()
        else:
            await ctx.send(f'You voted to skip this song. {required_votes-len(voters)} more votes are required.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def fskip(self, ctx: discord.ext.commands.Context):
        '''Admin command that forces skipping of the currently playing song.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not self.client_in_same_channel(ctx.message.author, voice):
            await ctx.send("You're not in a voice channel with me.")
            return

        if voice is None or not voice.is_playing():
            await ctx.send("I'm not playing a song right now.")
            return

        voice.stop()
        return

    @commands.command()
    async def songinfo(self, ctx: discord.ext.commands.Context, song_index: int = 0):
        '''Print out more information on the song currently playing.'''

        queue = self.music_queues.get(ctx.guild)

        if song_index not in range(len(queue)):
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
        start_index = (page-1) * SONGS_PER_PAGE
        end_index = min(start_index + SONGS_PER_PAGE, len(queue))

        for index in range(start_index, end_index):
            song = queue[index]

            queue_pos = set_str_len(f'{index + 1})', lower_limit=4)
            title = set_str_len(song.title, lower_limit=65, upper_limit=65)
            uploader = set_str_len(song.uploader, lower_limit=35, upper_limit=35)

            requested_by = song.requested_by_username

            to_send += f'\n{queue_pos}{title}|{uploader}|{requested_by}'

        to_send += '\n```'
        await ctx.send(to_send)

    async def play_all_songs(self, voice: List[discord.VoiceClient], guild: discord.Guild):
        # Play next song until queue is empty
        while len(queue) > 0:
            song = queue.next_song()
            await self.play_song(voice, guild, song)
            await self.wait_for_end_of_song(voice)

        # Disconnect after song queue is empty
        await self.inactivity_disconnect(voice, guild)

    async def play_song(self, voice: List[discord.VoiceClient], guild: discord.Guild, song: Song):
        '''Downloads and starts playing a YouTube video's audio.'''

        audio_dir = os.path.join('.', 'audio')
        audio_path = os.path.join(audio_dir, f'{guild.id}.mp3')

        queue = self.music_queues.get(guild)
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_path
        }

        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        song_there = os.path.isfile(audio_path)

        if song_there:
            os.remove(audio_path)
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'{song.url}'])
            except:
                await self.process_queue(voice, guild)
                print('Error downloading song. Skipping.')
                return
        
        voice.play(discord.FFmpegPCMAudio(audio_path))
        queue.clear_skip_votes()

    async def wait_for_end_of_song(self, voice: List[discord.VoiceClient]):
        queue = self.music_queues.get(guild)

        while voice.is_playing():
            await asyncio.sleep(1)

    async def inactivity_disconnect(self, voice: List[discord.VoiceClient], guild: discord.Guild):
        '''If a song is not played for 5 minutes, automatically disconnects bot from server.'''

        queue = self.music_queues.get(guild)
        last_song = queue.current_song

        await asyncio.sleep(300)
        if queue.current_song == last_song:
            await voice.disconnect()

    @staticmethod
    def client_in_same_channel(author: discord.Member, voice: List[discord.VoiceClient]):
        '''Checks to see if a client is in the same channel as the bot.'''

        try:
            channel = author.voice.channel
        except:
            return False
        
        return voice is not None and voice.is_connected() and channel == voice.channel:

    @staticmethod
    def song_error_check(song: Song):
        ''' Checks song properties to ensure that the song is both valid and doesn't match any filtered properties'''

        if song.url is None:
            return False, "Invalid URL provided or no video found."
        
        if song.get("is_live", True):
            return False, "Invalid video - either live stream or unsupported website."

        if song.duration_raw > DURATION_CEILING:
            return False, "Video is too long. Keep it under 20mins."
        
        return True, None


def setup(bot):
    bot.add_cog(Music(bot))
