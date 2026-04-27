import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {} # Tracks channel_id: game_active_status

    @commands.hybrid_command(name="hangman", description="Protect the blossom by guessing the secret word!")
    async def hangman(self, ctx):
        # 1. Prevent multiple games in one channel
        if ctx.channel.id in self.active_games:
            return await ctx.send("☁️ A game is already blooming in this channel! Please finish it first.", ephemeral=True)

        self.active_games[ctx.channel.id] = True
        
        # 2. Game Setup
        words = ["sunshine", "blossom", "garden", "butterfly", "breeze", "morning", "meadow", "honeybee", "rainbow", "daisies", "sunflower"]
        secret_word = random.choice(words).lower()
        guessed_letters = []
        lives = 6
        first_turn = True

        def get_display_word():
            return " ".join([letter if letter in guessed_letters else " \_ " for letter in secret_word])

        embed = discord.Embed(
            title="🌻 Ensoleille | The Wilting Blossom",
            description=f"Protect the flower! Guess the letters to find the hidden word.\n\n**Word:** `{get_display_word()}`",
            color=0xFFD700
        )
        embed.add_field(name="Petals Left", value="🌸" * lives)
        embed.set_footer(text="Type a letter to guess! You have 60 seconds per turn.")
        
        game_msg = await ctx.send(embed=embed)

        # 3. Game Loop
        while lives > 0:
            def check(m):
                return m.channel == ctx.channel and len(m.content) == 1 and m.content.isalpha() and m.author != self.bot.user

            try:
                # 60-second cooldown/timeout
                guess_msg = await self.bot.wait_for("message", check=check, timeout=60.0)
                guess = guess_msg.content.lower()
                
                # Delete user guess to keep channel clean
                try:
                    await guess_msg.delete()
                except:
                    pass

                if guess in guessed_letters:
                    continue

                guessed_letters.append(guess)

                if guess in secret_word:
                    # THE TWIST: Vowel Bonus
                    if first_turn and guess in "aeiou":
                        lives += 1
                        bonus_text = "✨ **Sunny Bonus!** You guessed a vowel first! +1 Petal!"
                    else:
                        bonus_text = "✅ That letter is in the word!"
                else:
                    lives -= 1
                    bonus_text = "☁️ Oh no! A petal has fallen..."

                first_turn = False

                # Check Win/Loss
                if all(letter in guessed_letters for letter in secret_word):
                    embed.title = "🎊 Ensoleille | The Flower Blooms!"
                    embed.description = f"Congratulations! The word was **{secret_word}**.\nThe garden is safe and bright!"
                    embed.color = 0x00FF00
                    embed.clear_fields()
                    await game_msg.edit(embed=embed)
                    break

                # Update Embed
                embed.description = f"{bonus_text}\n\n**Word:** `{get_display_word()}`"
                embed.set_field_at(0, name="Petals Left", value="🌸" * lives if lives > 0 else "🥀 All petals have fallen...")
                await game_msg.edit(embed=embed)

            except asyncio.TimeoutError:
                embed.title = "☁️ Ensoleille | The Clouds Rolled In"
                embed.description = f"The game ended because everyone got quiet. The word was **{secret_word}**."
                embed.color = 0x808080
                embed.clear_fields()
                await game_msg.edit(embed=embed)
                break

        if lives == 0:
            embed.title = "🥀 Ensoleille | The Blossom Wilted"
            embed.description = f"Oh no! You ran out of petals. The word was **{secret_word}**."
            embed.color = 0xFF0000
            await game_msg.edit(embed=embed)

        # Remove channel from active games list
        del self.active_games[ctx.channel.id]

async def setup(bot):
    await bot.add_cog(Games(bot))
