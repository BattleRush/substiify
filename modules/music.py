from helper.YTDLSource import YTDLSource
from helper.MusicPlayer import MusicPlayer
from discord.ext import commands
from urllib.parse import urlparse
from urllib.parse import parse_qs
from random import shuffle
import itertools
import wavelink
import logging
import asyncio
import discord

async def userIsInBotVC(ctx):
    if not ctx.voice_client == None:
        members = ctx.voice_client.channel.voice_states.keys()
        if ctx.author.id in members:
            return True
        await ctx.send(f'You are not in the VC!')
        return False

async def userIsInAnyVC(ctx):
    if ctx.author.voice:
        return True
    await ctx.send('You are not in a VC!')
    return False

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password='youshallnotpass',
                                              identifier='TEST',
                                              region='us_central')

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, query: str):
        tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        await ctx.send(f'Added {str(tracks[0])} to the queue.')
        await player.play(tracks[0])

    @commands.command()
    @commands.check(userIsInBotVC)
    async def pause(self, ctx):
        """Pause the currently playing song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        elif botsVc.is_paused():
            return
        botsVc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command()
    @commands.check(userIsInBotVC)
    async def resume(self, ctx):
        """Resume the currently paused song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        elif not botsVc.is_paused():
            return
        botsVc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command()
    @commands.check(userIsInBotVC)
    async def skip(self, ctx):
        """Skip the song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        if botsVc.is_paused():
            pass
        elif not botsVc.is_playing():
            return
        botsVc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    @commands.command(name='queue', aliases=['q'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=30)
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')
        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 10))
        fmt = '\n'.join(f'#{index+1} | **`{song.data["title"]}`**' for index, song in enumerate(upcoming))
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)
        await ctx.send(embed=embed)

    @commands.command(aliases=['currentsong', 'now'])
    async def now_playing(self, ctx):
        """Display information about the currently playing song."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=30)
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')
        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass
        player.np = await ctx.send(f'**Now Playing:** `{botsVc.source.title}` requested by `{botsVc.source.requester}`')

    @commands.command()
    @commands.check(userIsInBotVC)
    async def stop(self, ctx):
        """Stop the currently playing song and destroy the player."""
        botsVc = ctx.voice_client
        if not botsVc or not botsVc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=30)
        await self.cleanup(ctx.guild)
        await ctx.message.delete()

    @commands.command()
    @commands.check(userIsInBotVC)
    async def shuffle(self, ctx: commands.Context):
        if self.get_player(ctx).queue.qsize() == 0:
            return await ctx.send('Empty queue.')

        shuffle(self.get_player(ctx).queue._queue)
        await ctx.message.delete()
        await ctx.send('Queue has been shuffled', delete_after=15)

    @commands.command(name='connect')
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connecting to **`{channel.name}`**')
        await player.connect(channel.id)

def setup(bot):
    bot.add_cog(Music(bot))