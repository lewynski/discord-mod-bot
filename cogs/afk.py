import discord
from discord.ext import commands
from discord import app_commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {} # Stores user_id: reason
        self.side_gif = "https://i.imgur.com/w6JbMxD.gif"

    # --- THE AFK COMMAND ---
    @commands.hybrid_command(name="afk", description="Let everyone know you're taking a little break.")
    @app_commands.describe(reason="What are you up to while you're away?")
    async def afk(self, ctx, *, reason: str = "Taking a cozy break"):
        self.afk_users[ctx.author.id] = reason
        
        embed = discord.Embed(
            title="☁️ Ensoleille | Time for a rest",
            description=f"{ctx.author.mention} is now resting... \n**Reason:** {reason}",
            color=0xADD8E6 # Light Sky Blue
        )
        embed.set_thumbnail(url=self.side_gif)
        embed.set_footer(text="“Rest well, we'll be here when you return.”")
        
        await ctx.send(embed=embed)

    # --- THE LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 1. Check if the person who sent a message was AFK (Remove AFK)
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            
            embed = discord.Embed(
                description=f"Welcome back, {message.author.mention}! ☀️\nI've removed your away status for you.",
                color=0xFFD700
            )
            await message.channel.send(embed=embed, delete_after=10)

        # 2. Check if anyone mentioned in the message is AFK
        if message.mentions:
            for mentioned in message.mentions:
                if mentioned.id in self.afk_users:
                    reason = self.afk_users[mentioned.id]
                    
                    embed = discord.Embed(
                        title="🌸 Just a note...",
                        description=f"{mentioned.mention} is currently away.\n**Reason:** {reason}",
                        color=0xFFB6C1 # Pink
                    )
                    embed.set_thumbnail(url=self.side_gif)
                    embed.set_footer(text="They'll see your message when they're back!")
                    
                    await message.reply(embed=embed, delete_after=15)

async def setup(bot):
    await bot.add_cog(AFK(bot))
