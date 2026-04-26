import discord
import os
import asyncio
from discord.ext import commands
from aiohttp import web

# 1. Setup Intents and Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', intents=intents)

# ADD THIS LINE:
bot.remove_command('help')

# 2. Render Health Check (The Heartbeat)
async def handle(request):
    return web.Response(text="Bot is online and healthy!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# 3. Startup Events
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="*help for mods"))

async def main():
    await start_server()
    async with bot:
        # This loads the moderation file from your "dock" folder
        await bot.load_extension('cogs.moderation')
        # This gets your token from Render's Environment Variables
        await bot.start(os.environ.get('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
