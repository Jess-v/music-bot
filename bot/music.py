import discord
import youtube_dl

DURATION_CEILING = 20 * 60

DURATION_CEILING_STRING = '20mins'


class Queue(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_song = None
        self._skip_voters = []

    def next_song(self):
        self._current_song = self.pop(0)

        return self._current_song

    def clear(self):
        super().clear()
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
            song['description'] = f'{song.description[:300]}...'

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
        embed.add_field(name='Requested By', value=song.requested_by.display_name, inline=True)

        return embed


class SongRequestError(Exception):
    pass


class Song(dict):

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    def __init__(self, url: str, author: discord.Member):
        super().__init__()
        self.download_info(url, author)

        if self.duration_raw > DURATION_CEILING:
            raise SongRequestError(f'Your song was too long, keep it under {DURATION_CEILING_STRING}')
        elif self.get('is_live', True):
            raise SongRequestError('Invalid video - either live stream or unsupported website.')
        elif self.url is None:
            raise SongRequestError('Invalid URL provided or no video found.')

    @property
    def url(self):
        return self.get('url', None)

    @property
    def title(self):
        return self.get('title', 'Unable To Fetch')

    @property
    def uploader(self):
        return self.get('uploader', 'Unable To Fetch')

    @property
    def duration_raw(self):
        return self.get('duration', 0)

    @property
    def duration_formatted(self):
        minutes, seconds = self.duration_raw // 60, self.duration_raw % 60
        return f'{minutes}m, {seconds}s'

    @property
    def description(self):
        return self.get('description', 'Unable To Fetch')

    @property
    def upload_date_raw(self):
        return self.get('upload_date', '01011970')

    @property
    def upload_date_formatted(self):
        m, d, y = self.upload_date_raw[4:6], self.upload_date_raw[6:8], self.upload_date_raw[0:4]
        return f'{m}/{d}/{y}'

    @property
    def views(self):
        return self.get('view_count', 0)

    @property
    def likes(self):
        return self.get('like_count', 0)

    @property
    def dislikes(self):
        return self.get('dislike_count', 0)

    @property
    def thumbnail(self):
        return self.get('thumbnail', 'http://i.imgur.com/dDTCO6e.png')

    @property
    def requested_by(self):
        return self.get('requested_by', None)

    def download_info(self, url: str, author: discord.Member):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            self.update(ydl.extract_info(url, download=False))

            if not url.startswith('https'):
                self.update(ydl.extract_info(self['entries'][0]['webpage_url'], download=False))

            self['url'] = url
            self['requested_by'] = author
