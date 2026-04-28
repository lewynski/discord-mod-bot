import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import time
import random
import aiosqlite
import asyncio

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # No timeout so button stays active

    @discord.ui.button(label="Enter", style=discord.ButtonStyle.green, emoji="🎁", custom_id="enter_giveaway")
    async def enter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect("giveaways.db") as db:
            # Check if user already entered
            cursor = await db.execute("SELECT entries FROM giveaways WHERE message_id = ?", (interaction.message.id,))
            row = await cursor.fetchone()
            
            if not row:
                return await interaction.response.send_message("☁️ This giveaway seems to have ended!", ephemeral=True)
            
            entries = row[0].split(",") if row[0] else []
            if str(interaction.user.id) in entries:
                return await interaction.response.send_message("🌻 You've already joined this sunshine drop!", ephemeral=True)
            
            entries.append(str(interaction.user.id))
            await db.execute("UPDATE giveaways SET entries = ? WHERE message_id = ?", (",".join(entries), interaction.message.id))
            await db.commit()
            
            await interaction.response.send_message("✨ You've entered! Good luck, sunny friend!", ephemeral=True)

class Giveaway(commands.GroupCog, name="giveaway"):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    async def cog_load(self):
        # Create database table if it doesn't exist
        async with aiosqlite.connect("giveaways.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaways (
                    message_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    end_time REAL,
                    prize TEXT,
                    winners INTEGER,
                    entries TEXT,
                    thumbnail TEXT,
                    image TEXT
                )
            """)
            await db.commit()
        self.bot.add_view(GiveawayView()) # Register the button globally

    def cog_unload(self):
        self.check_giveaways.cancel()

    # --- START GIVEAWAY ---
    @app_commands.command(name="start", description="Start a sunny giveaway drop!")
    @app_commands.describe(
        duration="How long? (e.g. 10m, 1h, 1d)",
        winners="Number of winners",
        prize="What is the prize?",
        thumbnail="Optional side image URL",
        image="Optional bottom image URL"
    )
    async def start(self, interaction: discord.Interaction, duration: str, winners: int, prize: str, thumbnail: str = None, image: str = None):
        # Convert duration to seconds
        amount = int(duration[:-1])
        unit = duration[-1].lower()
        seconds = amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
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
        msg = await interaction.channel.send(embed=embed, view=GiveawayView())

        async with aiosqlite.connect("giveaways.db") as db:
            await db.execute(
                "INSERT INTO giveaways (message_id, channel_id, end_time, prize, winners, entries, thumbnail, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (msg.id, interaction.channel.id, end_time, prize, winners, "", thumbnail, image)
            )
            await db.commit()

    # --- STOP GIVEAWAY ---
    @app_commands.command(name="stop", description="End a giveaway early.")
    async def stop(self, interaction: discord.Interaction, message_id: str):
        async with aiosqlite.connect("giveaways.db") as db:
            await db.execute("UPDATE giveaways SET end_time = ? WHERE message_id = ?", (time.time(), int(message_id)))
            await db.commit()
        await interaction.response.send_message("🌅 Ending the giveaway now...", ephemeral=True)

    # --- BACKGROUND TASK ---
    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        now = time.time()
        async with aiosqlite.connect("giveaways.db") as db:
            cursor = await db.execute("SELECT * FROM giveaways WHERE end_time <= ?", (now,))
            ended = await cursor.fetchall()
            
            for g in ended:
                msg_id, chan_id, _, prize, winner_count, entries_str, thumb, img = g
                channel = self.bot.get_channel(chan_id)
                if not channel: continue
                
                try:
                    msg = await channel.fetch_message(msg_id)
                except: continue

                entries = entries_str.split(",") if entries_str else []
                
                if len(entries) == 0:
                    description = "Nobody entered the giveaway... the sun went down. ☁️"
                else:
                    winners = random.sample(entries, min(len(entries), winner_count))
                    winner_mentions = ", ".join([f"<@{w}>" for w in winners])
                    description = f"Congratulations {winner_mentions}! You won the **{prize}**! ☀️"

                end_embed = discord.Embed(title="🎁 GIVEAWAY ENDED", description=description, color=0x808080)
                if thumb: end_embed.set_thumbnail(url=thumb)
                if img: end_embed.set_image(url=img)
                end_embed.set_footer(text="Ensoleille | Better luck next time!")
                
                await msg.edit(embed=end_embed, view=None)
                await channel.send(f"🎊 {description}" if len(entries) > 0 else "☁️ Nobody won the giveaway.")
                
                await db.execute("DELETE FROM giveaways WHERE message_id = ?", (msg_id,))
                await db.commit()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
