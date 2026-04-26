import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="toss-a-petal", description="Toss a flower petal into the breeze to make a choice!")
    async def toss_a_petal(self, ctx):
        # The two sunny outcomes
        outcomes = [
            {"side": "Yellow Petal", "message": "The sun is shining on the golden side!", "color": 0xFFD700},
            {"side": "Pink Petal", "message": "The soft pink side landed facing the sky!", "color": 0xFFB6C1}
        ]
        
        result = random.choice(outcomes)
        
        embed = discord.Embed(
            title="🌻 Ensoleille | A petal in the wind...",
            description=f"You tossed a petal and watched it dance before landing on the **{result['side']}**!",
            color=result['color']
        )
        embed.add_field(name="The Result", value=f"✨ {result['message']}", inline=False)
        
        # A cute flower icon
        embed.set_thumbnail(url="https://i.imgur.com/8m4F7U6.png")
        
        embed.set_footer(text="“Let the breeze guide your heart today.”")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
