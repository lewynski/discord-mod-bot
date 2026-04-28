import discord
import os
import asyncio
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

# 1. Setup Intents and Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', intents=intents, help_command=None)

# 2. THE HEARTBEAT (This keeps Render awake!)
async def handle(request):
    return web.Response(text="Ensoleille is shining bright! ☀️")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render provides the port automatically
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

# 3. Startup Logic
@bot.event
async def on_ready():
    print(f'--- Ensoleille Online | Database Connected ---')
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"Sync error: {e}")
    
    await bot.change_presence(activity=discord.Game(name="under the sun ☀️"))

# 4. Main Execution
async def main():
    # A. Start the web server first
    await start_server()
    
    # B. Setup Mongo Cloud Connection
    mongo_uri = os.environ.get('MONGO_URI')
    bot.mongo = AsyncIOMotorClient(mongo_uri)
    bot.db = bot.mongo.ensoleille_db
    
    async with bot:
        # C. Load Extensions
        extensions = [
            'cogs.moderation', 
            'cogs.fun', 
            'cogs.welcome', 
            'cogs.afk', 
            'cogs.games', 
            'cogs.giveaway'
        ]
        
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"Loaded: {ext}")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")
        
        # D. Start the Bot
        token = os.environ.get('DISCORD_TOKEN')
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
