import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {} 
        self.side_gif = "https://i.imgur.com/w6JbMxD.gif"

    @commands.hybrid_command(name="afk", description="Let everyone know you're taking a little break.")
    @app_commands.describe(reason="What are you up to while you're away?")
    async def afk(self, ctx, *, reason: str = "Taking a cozy break"):
        # We store the ID of the message that set the AFK status
        # so we can ignore it in the listener
        self.afk_users[ctx.author.id] = {
            "reason": reason,
            "setup_message_id": ctx.message.id if ctx.message else None
        }
        
        embed = discord.Embed(
            title="☁️ Ensoleille | Time for a rest",
            description=f"{ctx.author.mention} is now resting... \n**Reason:** {reason}",
            color=0xADD8E6
        )
        embed.set_thumbnail(url=self.side_gif)
        embed.set_footer(text="“Rest well, we'll be here when you return.”")
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. Ignore if it's a bot
        if message.author.bot:
            return

        # 2. Check if the message is a valid command (like *afk or *help)
        # This is the strongest way to prevent the "double trigger"
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        # 3. Check if the person sending the message was AFK
        if message.author.id in self.afk_users:
            # Extra safety: Make sure it's not the same message that set the AFK
            afk_data = self.afk_users[message.author.id]
            if message.id == afk_data["setup_message_id"]:
                return

            # They are officially back!
            del self.afk_users[message.author.id]
            
            embed = discord.Embed(
                description=f"Welcome back, {message.author.mention}! ☀️\nI've removed your away status for you.",
                color=0xFFD700
            )
            await message.channel.send(embed=embed, delete_after=10)

        # 4. Check if anyone mentioned in the message is AFK
        if message.mentions:
            for mentioned in message.mentions:
                if mentioned.id in self.afk_users and mentioned.id != message.author.id:
                    reason = self.afk_users[mentioned.id]["reason"]
                    
                    embed = discord.Embed(
                        title="🌸 Just a note...",
                        description=f"{mentioned.mention} is currently away.\n**Reason:** {reason}",
                        color=0xFFB6C1
                    )
                    embed.set_thumbnail(url=self.side_gif)
                    embed.set_footer(text="They'll see your message when they're back!")
                    await message.reply(embed=embed, delete_after=15)

async def setup(bot):
    await bot.add_cog(AFK(bot))
