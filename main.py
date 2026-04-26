import discord
import os
import asyncio
from discord.ext import commands
from aiohttp import web

# 1. Setup Intents and Bot
# We use help_command=None to prevent the collision error with your custom help command
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', intents=intents, help_command=None)

# 2. Ensoleille Heartbeat (For Render & Cron-job.org)
async def handle(request):
    return web.Response(text="Ensoleille is shining! ☀️")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render uses the PORT environment variable (usually 8080 or 10000)
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server is listening on port {port}")

# 3. Startup Events
@bot.event
async def on_ready():
    print(f'--- Ensoleille is Online ---')
    print(f'Logged in as: {bot.user.name}')
    
    # This part "Syncs" your slash commands so they show up in the / menu
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")
    
    await bot.change_presence(activity=discord.Game(name="under the sun ☀️"))

# 4. Main Execution
async def main():
    # Start the web server in the background
    await start_server()
    
    async with bot:
        # This pulls your cute moderation tools from the cogs folder
        await bot.load_extension('cogs.moderation')
        
        # This gets your secret token from Render's Environment Variables
        token = os.environ.get('DISCORD_TOKEN')
        if token:
            await bot.start(token)
        else:
            print("ERROR: No DISCORD_TOKEN found in Environment Variables!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handles local testing shutdowns gracefully
        pass
