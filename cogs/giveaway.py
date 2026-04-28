import discord
from discord.ext import commands, tasks
from discord import app_commands
import time
import random

# The Staff Role IDs
ADMIN_ROLE_IDS = [
    1496909970464178248,
    1497441701701095615,
    1497234157275840692
]

class GiveawayView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Enter", style=discord.ButtonStyle.green, emoji="🎁", custom_id="enter_giveaway")
    async def enter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = self.bot.db.giveaways
        giveaway = await db.find_one({"message_id": interaction.message.id})
        
        if not giveaway or giveaway.get("ended"):
            return await interaction.response.send_message("☁️ This giveaway has already ended!", ephemeral=True)
        
        if interaction.user.id in giveaway["entries"]:
            return await interaction.response.send_message("🌻 You've already joined this sunshine drop!", ephemeral=True)
        
        await db.update_one(
            {"message_id": interaction.message.id},
            {"$push": {"entries": interaction.user.id}}
        )
        await interaction.response.send_message("✨ You've entered! Good luck!", ephemeral=True)

    @discord.ui.button(label="View Entries", style=discord.ButtonStyle.gray, emoji="📜", custom_id="view_entries")
    async def entries_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = self.bot.db.giveaways
        giveaway = await db.find_one({"message_id": interaction.message.id})
        if not giveaway: return
        
        entries = giveaway.get("entries", [])
        entry_list = ", ".join([f"<@{uid}>" for uid in entries]) if entries else "No entries yet."
        if len(entry_list) > 1900: entry_list = entry_list[:1900] + "..."

        embed = discord.Embed(title="🌸 Participants", description=entry_list, color=0xFFFACD)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Giveaway(commands.GroupCog, name="giveaway"):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    async def cog_load(self):
        self.bot.add_view(GiveawayView(self.bot))

    @app_commands.command(name="start", description="Start a giveaway.")
    @app_commands.checks.has_any_role(*ADMIN_ROLE_IDS)
    async def start(self, interaction: discord.Interaction, duration: str, winners: int, prize: str, host: discord.Member = None, thumbnail: str = None, image: str = None):
        host_user = host if host else interaction.user
        amount = int(duration[:-1])
        unit = duration[-1].lower()
        seconds = amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
        end_time = time.time() + seconds

        embed = discord.Embed(
            title=f"🎁 ENSOLEILLE DROP | {prize}",
            description=f"Click to join! ☀️\n**Ends:** <t:{int(end_time)}:R>\n**Hosted by:** {host_user.mention}",
            color=0xFFD700
        )
        if thumbnail: embed.set_thumbnail(url=thumbnail)
        if image: embed.set_image(url=image)

        await interaction.response.send_message("☀️ Creating...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=GiveawayView(self.bot))

        await self.bot.db.giveaways.insert_one({
            "message_id": msg.id,
            "channel_id": interaction.channel.id,
            "end_time": end_time,
            "prize": prize,
            "winners_count": winners,
            "entries": [],
            "thumbnail": thumbnail,
            "image": image,
            "host_id": host_user.id,
            "ended": False
        })

    # --- NEW REROLL COMMAND ---
    @app_commands.command(name="reroll", description="Pick a new winner from an ended giveaway.")
    @app_commands.describe(message_id="The ID of the giveaway message")
    @app_commands.checks.has_any_role(*ADMIN_ROLE_IDS)
    async def reroll(self, interaction: discord.Interaction, message_id: str):
        db = self.bot.db.giveaways
        giveaway = await db.find_one({"message_id": int(message_id)})

        if not giveaway:
            return await interaction.response.send_message("❌ Giveaway not found in database.", ephemeral=True)
        
        if not giveaway.get("ended"):
            return await interaction.response.send_message("☁️ That giveaway hasn't ended yet! Use `/giveaway stop` first.", ephemeral=True)

        entries = giveaway.get("entries", [])
        if not entries:
            return await interaction.response.send_message("🎐 No entries found to reroll from.", ephemeral=True)

        winner = random.choice(entries)
        
        reroll_embed = discord.Embed(
            title="🎊 New Winner Rerolled!",
            description=f"The sun has chosen a new winner for **{giveaway['prize']}**!\n\nCongratulations <@{winner}>! ☀️",
            color=0xFFA500
        )
        await interaction.channel.send(content=f"✨ **Reroll Result:** <@{winner}>", embed=reroll_embed)
        await interaction.response.send_message("Successfully rerolled!", ephemeral=True)

    @app_commands.command(name="stop", description="End a giveaway early.")
    @app_commands.checks.has_any_role(*ADMIN_ROLE_IDS)
    async def stop(self, interaction: discord.Interaction, message_id: str):
        await self.bot.db.giveaways.update_one({"message_id": int(message_id)}, {"$set": {"end_time": time.time()}})
        await interaction.response.send_message("🌅 Ending now...", ephemeral=True)

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        now = time.time()
        db = self.bot.db.giveaways
        cursor = db.find({"end_time": {"$lte": now}, "ended": False})
        
        async for g in cursor:
            channel = self.bot.get_channel(g["channel_id"])
            if not channel: continue
            try:
                msg = await channel.fetch_message(g["message_id"])
            except: continue

            entries = g["entries"]
            if not entries:
                result_text = "No one entered... ☁️"
            else:
                winners = random.sample(entries, min(len(entries), g["winners_count"]))
                mentions = ", ".join([f"<@{w}>" for w in winners])
                result_text = f"Congratulations {mentions}! You won **{g['prize']}**! ☀️"

            end_embed = discord.Embed(title="🎁 GIVEAWAY ENDED", description=result_text, color=0x808080)
            if g["thumbnail"]: end_embed.set_thumbnail(url=g["thumbnail"])
            if g["image"]: end_embed.set_image(url=g["image"])
            
            await msg.edit(embed=end_embed, view=None)
            await channel.send(f"🎊 {result_text}")
            
            # CHANGE: We mark it as ended instead of deleting it!
            await db.update_one({"_id": g["_id"]}, {"$set": {"ended": True}})

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
