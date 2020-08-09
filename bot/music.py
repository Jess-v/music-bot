import discord
import youtube_dl


class Queue(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_song = None
        self._skip_voters = []

    def next_song(self):
        song = self.pop(0)
        self._current_song = song
        return song

    def clear(self):
        super(Queue, self).clear()
        self._current_song = None

    def add_skip_vote(self, voter: discord.Member):
        self._skip_voters.append(voter)

    def clear_skip_votes(self):
        self._skip_voters.clear()

    @property
    def skip_voters(self):
        return self._skip_voters

    @property
    def current_song(self):
        return self._current_song

    def get_embed(self, song_id: int):
        if song_id <= 0:
            song = self.current_song
        else:
            song = self[song_id-1]

        if len(song.description) > 300:
            song['description'] = f'{song.description[0:300]}...'

        embed = discord.Embed(title="Audio Info")
        embed.set_thumbnail(url=song.thumbnail)
        embed.add_field(name='Song', value=song.title, inline=True)
        embed.add_field(name='Uploader', value=song.uploader, inline=True)
        embed.add_field(name='Duration', value=song.duration_formatted, inline=True)
        embed.add_field(name='Description', value=song.description, inline=True)
        embed.add_field(name='Upload Date', value=song.upload_date_formatted, inline=True)
        embed.add_field(name='Views', value=song.views, inline=True)
        embed.add_field(name='Likes', value=song.likes, inline=True)
        embed.add_field(name='Dislikes', value=song.dislikes, inline=True)
        embed.add_field(name='Requested By', value=song.requested_by_username, inline=True)
        return embed


class Song:
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def __init__(self, ctx, url):
        self.song_data = {}
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            try:
                self.song_data = ydl.extract_info(url, download=False)
                if self.song_data.get('is_live', False):
                    raise
            except:
                raise
            if 'https' not in url:
                try:
                    self.song_data = ydl.extract_info(self.song_data['entries'][0]['webpage_url'], download=False)
                    if self.song_data.get('is_live', False):
                        raise
                except:
                    raise
            self.song_data["url"] = url
            self.song_data["requested_by"] = str(ctx.author.name)
            self.song_data["requested_by_id"] = ctx.author.id

    def url(self):
        return self.song_data.get('url', None)

    def title(self):
        return self.song_data.get('title', None)

    def uploader(self):
        return self.song_data.get('uploader', None)

    def duration(self):
        return self.song_data.get('duration', None)

    def duration_formatted(self):
        raw_duration = self.song_data.get('duration', None)
        try:
            minutes, seconds = raw_duration // 60, raw_duration % 60
        except:
            return
        formatted_duration = f'{minutes}m, {seconds}s'
        return formatted_duration

    def description(self):
        return self.song_data.get('description', None)

    def upload_date(self):
        return self.song_data.get('upload_date', None)

    def upload_date_formatted(self):
        raw_date = self.song_data.get('upload_date', None)
        try:
            formatted_date = f'{raw_date[4:6]}/{raw_date[6:8]}/{raw_date[0:4]}'
        except:
            return
        return formatted_date

    def views(self):
        return self.song_data.get('view_count', None)

    def likes(self):
        return self.song_data.get('like_count', None)

    def dislikes(self):
        return self.song_data.get('dislike_count', None)

    def thumbnail(self):
        return self.song_data.get('thumbnail', None)

    def requested_by(self):
        return self.song_data.get('requested_by', None)

    def requested_by_id(self):
        return self.song_data.get('requested_by_id', None)

    def get_dict(self):
        return dict(self.song_data)
