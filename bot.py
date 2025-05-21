# Import libraries needed for the Discord bot
import discord           # Discord API library
import aiohttp          # For making HTTP requests to Coinbase API
import asyncio         # For For handling asynchronous tasks
import logging         # For logging bot activity and errors
from dotenv import load_dotenv  # To load environment variables from .env
import os              # To access environment variables
from discord.ext import tasks  # For scheduling repeated tasks

# Load environment variables from .env file
load_dotenv()

# Bot configuration using environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Discord bot token
# Crypto trading pair (e.g., BTC-USD, ETH-USD, SOL-USD).
# Ensure this matches the format expected by Coinbase Advanced Trade API.
# Converting to uppercase to ensure consistency with API requirements.
TRADING_PAIR = os.getenv('TRADING_PAIR').upper()

# Coinbase Advanced Trade API URL for product details including price and 24h change.
# The product_id is case-sensitive and uses a hyphen (e.g., BTC-USD).
COINBASE_API_URL = f'https://api.coinbase.com/api/v3/brokerage/market/products/{TRADING_PAIR}'

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
        # Fetch crypto price from Coinbase API
        async with aiohttp.ClientSession() as session:
            async with session.get(COINBASE_API_URL) as response:
                if response.status != 200:
                    error_data = await response.json()
                    logging.error(f'Coinbase API error in nickname update: Status {response.status}. '
                                  f'Response: {error_data}. '
                                  f'Please check if TRADING_PAIR="{TRADING_PAIR}" is a valid product_id '
                                  f'on Coinbase Advanced Trade (e.g., BTC-USD).')
                    return

                data = await response.json()  # Parse JSON response
                try:
                    # The Coinbase Advanced Trade API response directly contains 'price' at the root level
                    price = float(data['price'])  # Get current spot price
                except KeyError:
                    logging.error(f"KeyError: 'price' not found in Coinbase API response for nickname update. "
                                  f"Full response: {data}. "
                                  f"Ensure TRADING_PAIR='{TRADING_PAIR}' is correct and the API is returning expected data.")
                    return # Exit if 'price' key is missing

        # Update nickname in all servers with formatted price
        new_nickname = f"${price:,.2f}"
        for server in client.guilds:
            try:
                bot_member = server.get_member(client.user.id)
                if bot_member:
                    await bot_member.edit(nick=new_nickname)
                    # Log that the nickname was set, without mentioning the specific server name
                    logging.info(f'Nickname set to {new_nickname}')
                else:
                    logging.warning(f'Bot member not found in server: {server.name}')
            except discord.errors.HTTPException as e:
                # Log Discord API specific errors (e.g., permissions)
                logging.error(f'Failed to update nickname in server {server.name}: {e}')
            except Exception as e:
                # Log any other unexpected errors during nickname update for a specific server
                logging.error(f'Error updating nickname in server {server.name}: {e}')

    except Exception as e:
        # Log any errors during the overall nickname update process
        logging.error(f'Error in update_nickname task: {e}')

# Task: Update bot's activity every 5 minutes
@tasks.loop(minutes=5)
async def update_activity():
    try:
        # Fetch crypto 24h change from Coinbase API
        async with aiohttp.ClientSession() as session:
            async with session.get(COINBASE_API_URL) as response:
                if response.status != 200:
                    error_data = await response.json()
                    logging.error(f'Coinbase API error in activity update: Status {response.status}. '
                                  f'Response: {error_data}. '
                                  f'Please check if TRADING_PAIR="{TRADING_PAIR}" is a valid product_id '
                                  f'on Coinbase Advanced Trade (e.g., BTC-USD).')
                    return

                data = await response.json()  # Parse JSON response
                try:
                    # Extract 'price_percentage_change_24h' directly from the root level
                    change_24h = float(data['price_percentage_change_24h'])  # Get 24h % change
                except KeyError:
                    logging.error(f"KeyError: 'price_percentage_change_24h' not found in Coinbase API response for activity update. "
                                  f"Full response: {data}. "
                                  f"Ensure TRADING_PAIR='{TRADING_PAIR}' is correct and the API is returning expected data.")
                    return # Exit if 'price_percentage_change_24h' key is missing

        # Clear current presence to avoid caching issues with Discord
        await client.change_presence(activity=None)
        await asyncio.sleep(0.5)  # Wait briefly to ensure the presence clears

        # Set activity with 24h percentage change
        # Assuming TRADING_PAIR is like "BTC-USD", split by '-' to get the coin symbol
        coin_symbol = TRADING_PAIR.split('-')[0]
        sign = '+' if change_24h >= 0 else ''  # Determine if the change is positive or negative
        activity = discord.CustomActivity(name=f"{sign}{change_24h:.2f}% | {coin_symbol}-USD on Coinbase.")
        await client.change_presence(activity=activity)
        # Log the successful activity update
        logging.info(f'Activity set to: {sign}{change_24h:.2f}% | {coin_symbol}-USD on Coinbase.')

    except Exception as e:
        # Log any errors during the overall activity update process
        logging.error(f'Error in update_activity task: {e}')

# Ensure tasks wait for bot to be ready before starting their loops
@update_nickname.before_loop
@update_activity.before_loop
async def before_tasks():
    await client.wait_until_ready()  # Wait until the bot is connected to Discord

# Run the bot
if __name__ == '__main__':
    try:
        client.run(BOT_TOKEN)  # Start the Discord bot with the provided token
    except Exception as e:
        # Log any critical errors that prevent the bot from running
        logging.error(f'Error running bot: {e}')
