# Import libraries needed for the Discord bot
import discord           # Discord API library
import aiohttp          # For making HTTP requests to Binance API
import asyncio         # For handling asynchronous tasks
import logging         # For logging bot activity and errors
from dotenv import load_dotenv  # To load environment variables from .env
import os              # To access environment variables
from discord.ext import tasks  # For scheduling repeated tasks

# Load environment variables from .env file
load_dotenv()

# Bot configuration using environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Discord bot token
TRADING_PAIR = os.getenv('TRADING_PAIR', 'BTCUSDT')  # Crypto trading pair (e.g., BTCUSDT, ETHUSDT, SOLUSDT)
# Binance API URL for price and 24h change, dynamically set with TRADING_PAIR
BINANCE_API_URL = f'https://api.binance.com/api/v3/ticker/24hr?symbol={TRADING_PAIR}'

# Set up logging to console only (no file storage)
logging.basicConfig(
    level=logging.INFO,  # Log info, warnings, and errors
    format='%(asctime)s - %(levelname)s - %(message)s',  # Include timestamp
    handlers=[logging.StreamHandler()]  # Output to console only
)

# Set up Discord client with required intents
intents = discord.Intents.default()  # Use default intents
intents.message_content = False      # No need for message content
intents.guilds = True               # Enable server access for nickname updates
client = discord.Client(intents=intents)  # Create client (no commands)

# Event: Runs when bot connects to Discord
@client.event
async def on_ready():
    # Log that bot is ready
    logging.info(f'Bot is ready as {client.user}')
    try:
        # Start the update tasks if not running
        if not update_nickname.is_running():
            update_nickname.start()
        if not update_activity.is_running():
            update_activity.start()
    except Exception as e:
        # Log any errors starting the tasks
        logging.error(f'Error starting update tasks: {e}')

# Task: Update bot's nickname in all servers every 1.5 minutes
@tasks.loop(minutes=1.5)
async def update_nickname():
    try:
        # Fetch crypto price from Binance API
        async with aiohttp.ClientSession() as session:
            async with session.get(BINANCE_API_URL) as response:
                if response.status != 200:
                    # Log API error
                    logging.error(f'Binance API error in nickname update: Status {response.status}')
                    return
                data = await response.json()  # Parse JSON response
                price = float(data['lastPrice'])  # Get current spot price

        # Update nickname in all servers with formatted price
        new_nickname = f"${price:,.2f}"
        for server in client.guilds:
            try:
                bot_member = server.get_member(client.user.id)
                if bot_member:
                    await bot_member.edit(nick=new_nickname)
                    logging.info(f'Nickname set to {new_nickname}')
                else:
                    logging.error('Bot member not found in a server')
            except discord.errors.HTTPException as e:
                # Log errors without server-specific data
                logging.error(f'Failed to update nickname: {e}')
            except Exception as e:
                # Log unexpected errors
                logging.error(f'Error updating nickname: {e}')

    except Exception as e:
        # Log any errors during nickname update
        logging.error(f'Error in update_nickname: {e}')

# Task: Update bot's activity every 5 minutes
@tasks.loop(minutes=5)
async def update_activity():
    try:
        # Fetch crypto 24h change from Binance API
        async with aiohttp.ClientSession() as session:
            async with session.get(BINANCE_API_URL) as response:
                if response.status != 200:
                    # Log API error
                    logging.error(f'Binance API error in activity update: Status {response.status}')
                    return
                data = await response.json()  # Parse JSON response
                change_24h = float(data['priceChangePercent'])  # Get 24h % change

        # Clear current presence to avoid caching
        await client.change_presence(activity=None)
        await asyncio.sleep(0.5)  # Wait briefly to ensure clear
        # Set activity with 24h percentage change
        coin_symbol = TRADING_PAIR.replace('USDT', '')  # Extract coin symbol (e.g., BTC from BTCUSDT)
        sign = '+' if change_24h >= 0 else ''  # Determine sign for percentage
        activity = discord.CustomActivity(name=f"{sign}{change_24h:.2f}% {coin_symbol}USD")
        await client.change_presence(activity=activity)
        # Log activity update
        logging.info(f'Activity set to: {sign}{change_24h:.2f}% {coin_symbol}USD')

    except Exception as e:
        # Log any errors during activity update
        logging.error(f'Error in update_activity: {e}')

# Ensure tasks wait for bot to be ready
@update_nickname.before_loop
@update_activity.before_loop
async def before_tasks():
    await client.wait_until_ready()  # Wait until bot is connected

# Run the bot
if __name__ == '__main__':
    try:
        client.run(BOT_TOKEN)  # Start bot with token
    except Exception as e:
        # Log any errors running the bot
        logging.error(f'Error running bot: {e}')
