import discord
from discord.ext import commands

# The Role IDs you provided
ADMIN_ROLE_IDS = [
    1496909970464178248,
    1497441701701095615,
    1497234157275840692
]

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.action_gif = "https://i.imgur.com/dFtSKYS.gif"

    # --- ERROR HANDLER ---
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(
                title="☁️ Oh! Just a second...",
                description="This sunny power is only for the server's special friends! (๑ > ▽ <) ",
                color=0xFFE4B5 # Soft Gold
            )
            embed.set_footer(text="Ensoleille • Keeping our skies bright.")
            await ctx.send(embed=embed, delete_after=10)

    # --- KICK COMMAND ---
    @commands.command()
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title="🌻 Ensoleille | A sweet farewell",
            description=f"**{member.name}** was carried away by a gentle breeze. We wish them well!",
            color=0xFFD700 # Gold
        )
        embed.add_field(name="Note", value=f"```\n{reason}\n```", inline=False)
        embed.add_field(name="Sunny Friend", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=self.action_gif)
        
        embed.set_footer(text="“Keep your face to the sunshine and you cannot see a shadow.”")
        await ctx.send(embed=embed)

    # --- BAN COMMAND ---
    @commands.command()
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title="☀️ Ensoleille | A long rest",
            description=f"**{member.name}** has reached their sunset here. They are tucked away from our fields now.",
            color=0xFFA500 # Orange
        )
        embed.add_field(name="Note", value=f"```\n{reason}\n```", inline=False)
        embed.add_field(name="Sunny Friend", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=self.action_gif)
        
        embed.set_footer(text="“Even the longest day eventually reaches its sunset.”")
        await ctx.send(embed=embed)

    # --- UNBAN COMMAND ---
    @commands.command()
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.name == member_name:
                await ctx.guild.unban(ban_entry.user)
                
                embed = discord.Embed(
                    description=f"☁️ **{ban_entry.user.name}** is back! The clouds have cleared for a new morning.",
                    color=0x87CEEB # Sky Blue
                )
                embed.set_footer(text="“No matter how long the night, the dawn will always break.”")
                await ctx.send(embed=embed)
                return
        await ctx.send("❌ I couldn't find that friend in the shadows!")

    # --- HELP COMMAND ---
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="✨ Ensoleille | Warm Wishes",
            description="Here are the ways we keep our home bright and happy!",
            color=0xFFFFE0 # Light Yellow
        )
        embed.add_field(name="Our tools", value="`*kick` • `*ban` • `*unban` • `*help` ", inline=False)
        embed.set_footer(text="“Let's stay warm and kind to one another today!”")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
