import discord
from discord.ext import commands, tasks
from discord import app_commands
import time
import random

# The Role IDs you provided for staff protection
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
        
        if not giveaway:
            return await interaction.response.send_message("☁️ This giveaway is no longer active!", ephemeral=True)
        
        if interaction.user.id in giveaway["entries"]:
            return await interaction.response.send_message("🌻 You've already joined this sunshine drop!", ephemeral=True)
        
        # Add user ID to the list in Mongo
        await db.update_one(
            {"message_id": interaction.message.id},
            {"$push": {"entries": interaction.user.id}}
        )
        
        await interaction.response.send_message("✨ You've entered! Good luck, sunny friend!", ephemeral=True)

class Giveaway(commands.GroupCog, name="giveaway"):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    async def cog_load(self):
        # Keep the button active even after a bot restart
        self.bot.add_view(GiveawayView(self.bot))

    def cog_unload(self):
        self.check_giveaways.cancel()

    # --- START COMMAND (Staff Only) ---
    @app_commands.command(name="start", description="Start a sunny giveaway drop!")
    @app_commands.checks.has_any_role(*ADMIN_ROLE_IDS)
    async def start(self, interaction: discord.Interaction, duration: str, winners: int, prize: str, thumbnail: str = None, image: str = None):
        # Convert duration (e.g., 10m, 1h) to seconds
        try:
            amount = int(duration[:-1])
            unit = duration[-1].lower()
            seconds = amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
        except:
            return await interaction.response.send_message("❌ Please use a valid time format like `10m`, `1h`, or `1d`!", ephemeral=True)

        end_time = time.time() + seconds

        embed = discord.Embed(
            title=f"🎁 ENSOLEILLE DROP | {prize}",
            description=f"Click the button below to enter!\n\n**Ends:** <t:{int(end_time)}:R>\n**Hosted by:** {interaction.user.mention}",
            color=0xFFD700
        )
        if thumbnail: embed.set_thumbnail(url=thumbnail)
        if image: embed.set_image(url=image)
        embed.set_footer(text=f"{winners} Winner(s) • Good luck! ✨")

        await interaction.response.send_message("☀️ Creating the giveaway...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=GiveawayView(self.bot))

        # Save to MongoDB
        await self.bot.db.giveaways.insert_one({
            "message_id": msg.id,
            "channel_id": interaction.channel.id,
            "end_time": end_time,
            "prize": prize,
            "winners_count": winners,
            "entries": [],
            "thumbnail": thumbnail,
            "image": image
        })

    # --- STOP COMMAND (Staff Only) ---
    @app_commands.command(name="stop", description="End a giveaway early.")
    @app_commands.checks.has_any_role(*ADMIN_ROLE_IDS)
    async def stop(self, interaction: discord.Interaction, message_id: str):
        result = await self.bot.db.giveaways.update_one(
            {"message_id": int(message_id)},
            {"$set": {"end_time": time.time()}}
        )
        if result.modified_count > 0:
            await interaction.response.send_message("🌅 Ending the giveaway now...", ephemeral=True)
        else:
            await interaction.response.send_message("❌ I couldn't find a giveaway with that message ID.", ephemeral=True)

    # --- BACKGROUND CHECKER ---
    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        now = time.time()
        db = self.bot.db.giveaways
        
        cursor = db.find({"end_time": {"$lte": now}})
        async for g in cursor:
            channel = self.bot.get_channel(g["channel_id"])
            if not channel: continue
            
            try:
                msg = await channel.fetch_message(g["message_id"])
            except: 
                await db.delete_one({"_id": g["_id"]})
                continue

            entries = g["entries"]
            if not entries:
                result_text = "Nobody entered the giveaway... the sun went down. ☁️"
            else:
                winners = random.sample(entries, min(len(entries), g["winners_count"]))
                mentions = ", ".join([f"<@{w}>" for w in winners])
                result_text = f"Congratulations {mentions}! You won the **{g['prize']}**! ☀️"

            end_embed = discord.Embed(title="🎁 GIVEAWAY ENDED", description=result_text, color=0x808080)
            if g["thumbnail"]: end_embed.set_thumbnail(url=g["thumbnail"])
            if g["image"]: end_embed.set_image(url=g["image"])
            
            await msg.edit(embed=end_embed, view=None)
            await channel.send(f"🎊 {result_text}")
            
            await db.delete_one({"_id": g["_id"]})

    # Error handler for Staff IDs
    @start.error
    @stop.error
    async def giveaway_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            await interaction.response.send_message("☁️ Only server staff with sunny powers can start giveaways! (๑ > ▽ <) ", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
