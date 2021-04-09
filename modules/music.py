from helper.YTDLSource import YTDLSource
from helper.MusicPlayer import MusicPlayer
from discord.ext import commands
from urllib.parse import urlparse
from urllib.parse import parse_qs
from random import shuffle
import logging
import itertools
import asyncio
import discord

async def isInBotVC(ctx):
    members = ctx.voice_client.channel.voice_states.keys()
    if ctx.author.id in members:
        return True
    await ctx.send(f'You are not in the VC!')
    return False

async def isInAnyVC(ctx):
    if ctx.author.voice:
        return True
    await ctx.send('You are not in a VC!')
    return False

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    def checkIfYoutubePlaylist(self, url):
        return 'list=' in url

    async def parseUrl(self, ctx, player, url):
        if url.startswith('<'):
            url = url[1:-1]
        if self.checkIfYoutubePlaylist(url):
            parsed = urlparse(url)
            newUrl = f'https://youtube.com/playlist?list={parse_qs(parsed.query)["list"][0]}'
            urls = YTDLSource.get_playlist_info(newUrl)['urls']
            for entry in urls:
                source = await YTDLSource.from_url(ctx, entry, loop=self.bot.loop, stream=True)
                await player.queue.put(source)
            await ctx.send(f'Queued **{len(urls)}** songs')
        else:
            source = await YTDLSource.from_url(ctx, url, loop=self.bot.loop, stream=True)
            if ctx.voice_client.is_playing():
                await ctx.send(f'**Queued:** {source.title}')
            await player.queue.put(source)
        await ctx.message.delete()

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url):
        vc = ctx.voice_client
        if not vc:
            if await isInAnyVC(ctx):
                await ctx.invoke(self.connect)
                player = self.get_player(ctx)
                await self.parseUrl(ctx, player, url)
        else:
            if await isInBotVC(ctx):
                player = self.get_player(ctx)
                await self.parseUrl(ctx, player, url)

    @commands.command()
    @commands.check(isInBotVC)
    async def pause(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        elif vc.is_paused():
            return
        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command()
    @commands.check(isInBotVC)
    async def resume(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        elif not vc.is_paused():
            return
        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command()
    @commands.check(isInBotVC)
    async def skip(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return
        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    @commands.command(name='queue', aliases=['q'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=30)
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')
        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        fmt = '\n'.join(f'**`{song["title"]}`**' for song in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)
        await ctx.send(embed=embed)

    @commands.command(aliases=['currentsong', 'now'])
    async def now_playing(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=30)
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')
        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass
        player.np = await ctx.send(f'**Now Playing:** `{vc.source.title}` '
                                   f'requested by `{vc.source.requester}`')

    @commands.command()
    @commands.check(isInBotVC)
    async def stop(self, ctx):
        """Stop the currently playing song and destroy the player."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        await self.cleanup(ctx.guild)
        await ctx.message.delete()

    @commands.command()
    @commands.check(isInBotVC)
    async def shuffle(self, ctx: commands.Context):
        if self.get_player(ctx).queue.qsize() == 0:
            return await ctx.send('Empty queue.')

        shuffle(self.get_player(ctx).queue._queue)
        await ctx.message.delete()
        await ctx.send('Queue has been shuffled', delete_after=15)

    @commands.command()
    async def connect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await ctx.send(f'Connected to: **{channel}**', delete_after=30)

def setup(bot):
    bot.add_cog(Music(bot))