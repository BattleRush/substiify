from sqlite3.dbapi2 import Cursor
import discord
from discord import role
from discord import guild
from discord.ext import commands, tasks
from discord.ext.commands.core import command
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.daydeal.ch/"

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.mention_role = None
        self.endTime = None

    async def availableBarCreator(self, available):
        bar = "["
        if int(available) == 50:
            bar += ("l" * int(available)) + "]"
        else:
            bar += ("l" * int(available)) + "||" + ("l" * (50 - int(available))) + "||]"
        bar += " (" + str(int(available) * 2) + "%)"
        return bar

    async def createDaydealEmbed(self):
        # Web Scraping
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        self.endTime = datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')
        product_description = soup.find('section', class_='product-description')
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        product_img = soup.find('img', class_='product-img-main-pic')['src']
        new_price = soup.find('h2', class_='product-pricing__prices-new-price').text
        old_price = soup.find('span', class_='js-old-price')
        if old_price is not None:
            old_price = old_price.text
        else:
            old_price = ""
        available = int(soup.find('strong', class_='product-progress__availability').text.strip('%')) / 2
        ends_in = self.endTime - datetime.now().replace(microsecond=0)
        description_str = ""
        for element in description_details:
            description_str += "• " + element.text + "\n"

        # Create embed message
        embed = discord.Embed(title=title2, description=description_str, url=URL, colour=0x23b40c)
        embed.set_thumbnail(url="https://static.daydeal.ch/2.17.10/images/logo-top.png")
        embed.set_image(url=product_img)
        embed.set_author(name='Today\'s deal: ' + title1)
        embed.add_field(name="Price", value="Now: " + new_price + ", Old: " + old_price, inline=False)
        embed.add_field(name="Available", value=str(await self.availableBarCreator(available)), inline=False)
        embed.add_field(name="Ends in", value=str(ends_in), inline=False)
        return embed

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     db = sqlite3.connect('main.sqlite')
    #     cursor = db.cursor()
    #     cursor.execute(f"SELECT * FROM daydeal")
    #     result = cursor.fetchone()
    #     if result is not None:
    #         await self.daydeal_task.start()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setupDaydeal(self, ctx, channel: discord.TextChannel, mention_role: discord.Role):
        self.channel = channel
        self.mention_role = mention_role
        if self.channel is None:
            self.channel = ctx.channel
        if self.channel and self.mention_role:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM daydeal WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO daydeal(guild_id, channel_id, role_id) VALUES (?, ?, ?)")
                val = (str(ctx.guild.id), str(channel.id), str(mention_role.id))
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await self.channel.send(content=self.mention_role.mention,embed=await self.createDaydealEmbed())
                await ctx.channel.send("Setup successful.")
                await self.daydeal_task.start()
            else:
                await ctx.channel.send("Daydeal is already set up.")


    @setupDaydeal.error
    async def setupDaydeal_error(self, ctx, error):
        await ctx.channel.send(str(error))

    @commands.command()
    async def test(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        for row in cursor.execute(f"SELECT * FROM daydeal"):
            channel = discord.utils.get(guild.TextChannel, id=row[1])

            # messages = await 
            await ctx.channel.send(channel)
            await ctx.channel.send("test")

    @tasks.loop(seconds=180.0)
    async def daydeal_task(self):
        if datetime.now() >= self.endTime:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM daydeal")
            result = cursor.fetchall()
            await self.channel.send(result)
            # await self.channel.send(content=self.mention_role.mention,embed=await self.createDaydealEmbed())

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def stopDaydeal(self, ctx):
        await self.daydeal_task.cancel()
        await ctx.channel.send("Daydeal stopped.")

    @commands.cooldown(4, 10)
    @commands.command()
    async def deal(self, ctx):
        await ctx.channel.send(embed=await self.createDaydealEmbed())

    @deal.error
    async def deal_error(self, ctx, error):
        await ctx.channel.send('error:  ' + str(error))


def setup(bot):
    bot.add_cog(Daydeal(bot))
