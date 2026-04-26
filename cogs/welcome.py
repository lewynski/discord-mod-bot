import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}
        
        # Your aesthetic GIFs
        self.side_gif = "https://i.imgur.com/9XNKaoD.gif"
        self.bottom_gif = "https://i.imgur.com/sYf5n80.gif"
        
        # Your specific Welcome Channel ID
        self.welcome_channel_id = 1496907552271892604

    # --- INVITE CACHING ---
    async def cog_load(self):
        # We cache the invites when the cog loads so we can track the next join
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except discord.Forbidden:
                print(f"I don't have permission to see invites in {guild.name}!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter_mention = "a mysterious breeze"
        
        # 1. Logic to find who invited the user
        try:
            invites_before = self.invites.get(member.guild.id)
            invites_after = await member.guild.invites()
            
            if invites_before:
                for invite in invites_before:
                    # Check if this specific invite code has a new use
                    for current_invite in invites_after:
                        if invite.code == current_invite.code and invite.uses < current_invite.uses:
                            inviter_mention = current_invite.inviter.mention
                            break
            
            # Update cache for the next person
            self.invites[member.guild.id] = invites_after
        except Exception as e:
            print(f"Could not track invite: {e}")

        # 2. Get the specific channel
        channel = self.bot.get_channel(self.welcome_channel_id)
        if not channel:
            return

        # 3. Create the Aesthetic Embed
        embed = discord.Embed(
            title="☁️ A new friend has arrived!",
            description=(
                f"Hello {member.mention}! Welcome to the warm fields of **Ensoleille**. 🌻\n\n"
                f"We are so happy you've joined our little family. "
                f"It looks like you were brought here by {inviter_mention}! ✨"
            ),
            color=0xFFF0F5 # Lavender Blush (Very soft pink/white)
        )
        
        # Side GIF
        embed.set_thumbnail(url=self.side_gif)
        # Bottom GIF
        embed.set_image(url=self.bottom_gif)
        
        # Aesthetic Quote
        embed.set_footer(text="“Every new morning brings a new ray of light to our garden.”")
        
        await channel.send(content=f"Welcome home, {member.mention}! 🌿", embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
