import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # The Custom Help Command
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="🛡️ Bot Command Dock",
            description="Here are the tools available for moderators. Prefix: `*` ",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛠️ Moderation",
            value="`*kick @user [reason]` - Kicks a member.\n"
                  "`*ban @user [reason]` - Bans a member.\n"
                  "`*unban User#0000` - Unbans a member.",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Info",
            value="`*help` - Shows this menu.",
            inline=False
        )

        embed.set_footer(text="Aegis Moderation System | Powered by Render")
        await ctx.send(embed=embed)

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f'✅ **{member.name}** has been kicked. Reason: {reason}')

    # Ban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f'🔨 **{member.name}** has been banned. Reason: {reason}')

    # Unban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name:
                await ctx.guild.unban(user)
                await ctx.send(f'🔓 Unbanned **{user.name}**')
                return
        await ctx.send(f'❌ User "{member_name}" not found.')

async def setup(bot):
    await bot.add_cog(Moderation(bot))
