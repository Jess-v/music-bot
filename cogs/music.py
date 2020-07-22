import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
import youtube_dl
import asyncio
import os
from bot.music import Queue
from bot.music import Song

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.skip_votes = 0
        self.skip_voters = []
    queue_obj = Queue()

    @commands.command()
    async def play(self, ctx, url, *args):
        '''Adds a song to the queue either by YouTube URL or YouTube Search.'''

        voice = self.get_voice(ctx)
        if 'https' not in url:
            url = 'ytsearch1:' + url + f' {" ".join(args)}'
        try:
            channel = ctx.message.author.voice.channel
        except:
            await ctx.send("You're not connected to a voice channel.")
            return
        if voice and not self.client_in_same_channel(ctx, voice):
            await ctx.send("You're not in my voice channel.")
            return
        if not voice or not voice.is_connected():
            await channel.connect()
        try:
            self.queue_obj.add(ctx, url)
        except:
            await ctx.send('Invalid URL or failed to search. Please try again.')
            return
        queue_list = self.queue_obj.get_queue()
        queued_song = queue_list[len(queue_list)-1]
        title = queued_song.title()
        await ctx.send(f'Queued song: {title}')
        if not voice or not voice.is_playing():
            song = self.queue_obj.next()
            await self.play_song(ctx, song)

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
    async def skip(self, ctx):
        '''Puts in your vote to skip the currently played song.'''

        voice = self.get_voice()
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
    async def songinfo(self, ctx, song_index=0):
        '''Print out more information on the song currently playing.'''

        embed = self.queue_obj.get_embed(song_index)
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, song_id=0):
        '''Removes the last song you requested from the queue, or a specific song if queue position specified.'''

        voice = self.get_voice(ctx)
        if not self.client_in_same_channel(ctx, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        remover_id = ctx.author.id
        if song_id == 0:
            music_queue = self.queue_obj.get_queue()
            music_queue.reverse()
            queue_length = len(music_queue)
            loop_count = 0
            for i in music_queue:
                song_request_id = i.requested_by_id()
                if remover_id == song_request_id:
                    try:
                        print(f'attempted removal index: {queue_length - loop_count}')
                        song_name = i.title()
                        self.queue_obj.remove(queue_length - loop_count)
                        await ctx.send(f'Song "{song_name}" removed from queue.')
                        return
                    except:
                        await ctx.send('Error removing song from queue.')
                        return
                loop_count += 1
        else:
            try:
                song = self.queue_obj.get_song(song_id)
            except:
                await ctx.send('A song does not exist at this position in the queue.')
                return
            song_request_id = song.requested_by_id()
            if remover_id == song_request_id:
                try:
                    self.queue_obj.remove(song_id)
                    await ctx.send('Song removed from queue.')
                except:
                    await ctx.send('Error removing song from queue.')
                    return
            else:
                await ctx.send('You cannot remove a song requested by someone else.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def fremove(self, ctx, song_id=0):
        '''Admin command to forcibly remove a song from the queue by it's position.'''

        voice = self.get_voice(ctx)
        if not self.client_in_same_channel(ctx, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        if song_id == 0:
            await ctx.send("You need to specify a song by it's queue index.")
            return
        try:
            song = self.queue_obj.get_song(song_id)
            song_title = song.title()
        except:
            await ctx.send("A song does not exist at this queue index.")
            return
        try:
            self.queue_obj.remove(song_id)
            await ctx.send(f"Removed {song_title} from the queue.")
            return
        except:
            await ctx.send(f'Error removing song from queue.')
            return

    @commands.command()
    async def queue(self, ctx, page=1):
        '''Prints out a specified page of the music queue, defaults to first page.'''

        voice = self.get_voice(ctx)
        queue_list = self.queue_obj.get_queue()
        if not self.client_in_same_channel(ctx, voice):
            await ctx.send("You're not in a voice channel with me.")
            return
        if len(queue_list) < 1:
            await ctx.send("I don't have anything in my queue right now.")
            return
        to_send = '```\n                                 Song                                               Uploader' \
                  '               Requested By               '
        start_index = (page-1)*10
        for x in range(start_index, start_index+10):
            try:
                song = queue_list[x]
            except:
                break
            if song:
                queue_pos = str(x+1) + ')'
                title = song.title()
                uploader = song.uploader()
                requested_by = song.requested_by()
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

    async def play_song(self, ctx, song_obj):
        '''Downloads and starts playing a YouTube video's audio.'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': './audio/song.mp3',
        }
        song_there = os.path.isfile("./audio/song.mp3")
        if song_there:
            os.remove('./audio/song.mp3')
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'{song_obj.url()}'])
            except:
                await voice.disconnect()
                return
        try:
            voice.play(discord.FFmpegPCMAudio("./audio/song.mp3"))
            self.skip_votes = 0
            self.skip_voters = []
            await self.process_queue(ctx)
        except:
            await voice.disconnect()
            return

    async def process_queue(self, ctx):
        '''Continuously checks for the opportunity to play the next video.'''

        voice = self.get_voice(ctx)
        while voice.is_playing():
            await asyncio.sleep(1)
        if len(self.queue_obj.get_queue()) > 0:
            song = self.queue_obj.next()
            await self.play_song(ctx, song)
        else:
            await self.inactivity_disconnect(ctx)

    async def inactivity_disconnect(self, ctx):
        '''If a song is not played for 5 minutes, automatically disconnects bot from server.'''

        voice = self.get_voice(ctx)
        last_song = self.queue_obj.get_current_song()
        await asyncio.sleep(300)
        if self.queue_obj.get_current_song() == last_song:
            await voice.disconnect()

    def get_voice(self, ctx):
        '''Simple function to return a voice object'''

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        return voice

    @staticmethod
    def client_in_same_channel(ctx, voice):
        '''Checks to see if a client is in the same channel as the bot.'''
        try:
            channel = ctx.message.author.voice.channel
        except:
            return False
        if voice and voice.is_connected() and channel == voice.channel:
            return True
        else:
            return False


def setup(bot):
    bot.add_cog(Music(bot))
