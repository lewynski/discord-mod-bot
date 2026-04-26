import discord
from discord.ext import commands
from discord import app_commands

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
        self.role_gif = "https://i.imgur.com/DDVWx5G.gif"

    # --- ERROR HANDLER ---
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(
                title="☁️ Oh! Just a second...",
                description="This sunny power is only for the server's special friends! (๑ > ▽ <) ",
                color=0xFFE4B5
            )
            embed.set_footer(text="Ensoleille • Keeping our skies bright.")
            await ctx.send(embed=embed, delete_after=10)

    # --- ROLE COMMAND ---
    @commands.hybrid_command(name="role", description="Gently give or take a role from a friend.")
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    @app_commands.describe(role_input="The role name, ID, or tag", member="The friend to update")
    async def role(self, ctx, role_input: str, member: discord.Member):
        role = None
        
        # Finding the role
        if role_input.startswith("<@&") and role_input.endswith(">"):
            role_id = int(role_input[3:-1])
            role = ctx.guild.get_role(role_id)
        elif role_input.isdigit():
            role = ctx.guild.get_role(int(role_input))
        
        if not role:
            role = discord.utils.find(lambda r: r.name.lower() == role_input.lower(), ctx.guild.roles)

        if not role:
            return await ctx.send(f"❌ I couldn't find a role named '{role_input}' in my sunny garden!", ephemeral=True)

        if role in member.roles:
            await member.remove_roles(role)
            title_text = "✨ Ensoleille | Lightening the load"
            desc_text = f"The **{role.name}** role has been gently taken back from **{member.name}**."
            color_hex = 0xFFB6C1
        else:
            await member.add_roles(role)
            title_text = "🌟 Ensoleille | A new sparkle"
            desc_text = f"**{member.name}** has been gifted the **{role.name}** role! It looks great on them."
            color_hex = 0xFFF0F5

        embed = discord.Embed(title=title_text, description=desc_text, color=color_hex)
        embed.set_thumbnail(url=self.role_gif)
        embed.add_field(name="Sunny Friend", value=ctx.author.mention, inline=True)
        embed.set_footer(text="“Every little change makes our world more colorful.”")
        await ctx.send(embed=embed)

    # --- KICK COMMAND ---
    @commands.hybrid_command(name="kick", description="Send a friend on a sweet farewell journey.")
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="🌻 Ensoleille | A sweet farewell",
            description=f"**{member.name}** was carried away by a gentle breeze. We wish them well!",
            color=0xFFD700
        )
        embed.add_field(name="Note", value=f"```\n{reason}\n```", inline=False)
        embed.add_field(name="Sunny Friend", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=self.action_gif)
        embed.set_footer(text="“Keep your face to the sunshine and you cannot see a shadow.”")
        await ctx.send(embed=embed)

    # --- BAN COMMAND ---
    @commands.hybrid_command(name="ban", description="Let a friend rest away from our fields.")
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="☀️ Ensoleille | A long rest",
            description=f"**{member.name}** has reached their sunset here. They are tucked away now.",
            color=0xFFA500
        )
        embed.add_field(name="Note", value=f"```\n{reason}\n```", inline=False)
        embed.add_field(name="Sunny Friend", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=self.action_gif)
        embed.set_footer(text="“Even the longest day eventually reaches its sunset.”")
        await ctx.send(embed=embed)

    # --- UNBAN COMMAND ---
    @commands.hybrid_command(name="unban", description="Clear the clouds for a friend's return.")
    @commands.has_any_role(*ADMIN_ROLE_IDS)
    async def unban(self, ctx, *, member_name: str):
        banned_users = [entry async for entry in ctx.guild.bans()]
        for ban_entry in banned_users:
            if ban_entry.user.name == member_name:
                await ctx.guild.unban(ban_entry.user)
                embed = discord.Embed(
                    description=f"☁️ **{ban_entry.user.name}** is back! The clouds have cleared.",
                    color=0x87CEEB
                )
                embed.set_footer(text="“No matter how long the night, the dawn will always break.”")
                await ctx.send(embed=embed)
                return
        await ctx.send("❌ I couldn't find that friend in the shadows!", ephemeral=True)

    # --- HELP COMMAND ---
    @commands.hybrid_command(name="help", description="See the ways we keep Ensoleille bright.")
    async def help(self, ctx):
        embed = discord.Embed(
            title="✨ Ensoleille | Warm Wishes",
            description="Here are the ways we keep our home bright and happy!",
            color=0xFFFFE0
        )
        embed.add_field(name="Our tools", value="`*role` • `*kick` • `*ban` • `*unban` • `*help` ", inline=False)
        embed.set_footer(text="“Let's stay warm and kind to one another today!”")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
