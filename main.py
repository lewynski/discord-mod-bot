import discord
import os
import asyncio
from discord.ext import commands
from aiohttp import web

# 1. Setup Intents and Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', intents=intents, help_command=None)

# 2. Ensoleille Heartbeat (For Render)
async def handle(request):
    return web.Response(text="Ensoleille is shining! ☀️")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# 3. Startup Events
@bot.event
async def on_ready():
    print(f'--- Ensoleille is Online ---')
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")
    await bot.change_presence(activity=discord.Game(name="under the sun ☀️"))

# 4. Main Execution (Fixing the Indentation here)
async def main():
    await start_server()
    async with bot:
        # These MUST be indented exactly 8 spaces (2 levels in)
        await bot.load_extension('cogs.moderation')
        await bot.load_extension('cogs.fun')
        await bot.load_extension('cogs.welcome')
        await bot.load_extension('cogs.afk')
        await bot.load_extension('cogs.games')
        
        token = os.environ.get('DISCORD_TOKEN')
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
