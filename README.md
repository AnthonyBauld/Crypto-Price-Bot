# Crypto Price Discord Bot

This Discord bot updates its nickname every 1.5 minutes to the current price of a chosen cryptocurrency (e.g., "$67,123.45" for Bitcoin) and its activity every 5 minutes to the 24-hour percentage change (e.g., "+1.25% BTCUSD"). It uses the Coinbase API to fetch real-time price data and can be configured to track any cryptocurrency supported by Coinbase.

![alt text](https://media.discordapp.net/attachments/1041966384428634162/1373847406512308295/Screenshot_2025-05-18_at_10.17.41_PM.png?ex=682be69a&is=682a951a&hm=01bc7f2a74bddf99704cc5cbea20ff89ab5995e2416732965b9d00002f0958a9&=&format=webp&quality=lossless&width=856&height=344 "Example")

## Features
- **Nickname Updates**: Displays the crypto’s USD price as the bot’s nickname in all servers (requires "Change Nickname" permission).
- **Activity Updates**: Shows the 24-hour percentage change as the bot’s activity status.
- **Configurable Crypto**: Easily change the cryptocurrency by updating the `TRADING_PAIR` in `.env` (e.g., `BTCUSDT`, `ETHUSDT`, `SOLUSDT`).
- **Console-Only Logging**: Logs updates and errors to the console without saving data to disk.
- **No Guild References**: Uses "server" instead of "guild" in logs and comments for clarity.

## Setup Instructions

### Prerequisites
- **Python 3.8+**: Ensure Python is installed (`python --version` or `python3 --version`).
- **Discord Bot Token**: Create a bot at [Discord Developer Portal](https://discord.com/developers/applications).
- **GitHub Repository**: Clone or download this repository to your local machine.

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/crypto-price-discord-bot.git
   cd crypto-price-discord-bot
   ```

2. **Create and Configure `.env`**
   - Create a `.env` file in the project root.
   - Add your Discord bot token and desired trading pair:
     ```env
     BOT_TOKEN=your_discord_bot_token
     TRADING_PAIR=BTCUSDT
     ```
   - Replace `your_discord_bot_token` with your bot’s token from the Discord Developer Portal.
   - Set `TRADING_PAIR` to your chosen cryptocurrency (e.g., `ETHUSDT` for Ethereum, `SOLUSDT` for Solana). See [Changing the Cryptocurrency](#changing-the-cryptocurrency) for details.

3. **Install Dependencies**
   ```bash
   pip install discord.py aiohttp python-dotenv
   ```
   - Ensure `pip` matches your Python version (try `pip3` or `python3 -m pip` if needed).

4. **Run the Bot**
   ```bash
   python bot.py
   ```
   - Or use `python3 bot.py` if required.
   - The bot will log in and start updating its nickname and activity.

5. **Invite the Bot to Servers**
   - In the Discord Developer Portal, go to **OAuth2 > URL Generator**.
   - Select `bot` scope and the **Change Nickname** permission.
   - Copy the generated URL and use it to invite the bot to your servers.
   - Ensure the bot has “Change Nickname” permission in each server.

6. **Verify Bot Behavior**
   - Check console logs for updates like:
     ```
     2025-05-18 21:45:12,123 - INFO - Bot is ready as CryptoBot#1234
     2025-05-18 21:46:42,456 - INFO - Nickname set to $67,123.45
     2025-05-18 21:50:12,457 - INFO - Activity set to: +1.25% BTCUSD
     ```
   - In Discord, confirm the bot’s nickname updates every 1.5 minutes (e.g., “$67,123.45”).
   - Check the bot’s activity updates every 5 minutes (e.g., “+1.25% BTCUSD”).

## Changing the Cryptocurrency

To track a different cryptocurrency, update the `TRADING_PAIR` in the `.env` file. The bot uses Coinbase’s API, which supports many trading pairs (e.g., `BTCUSDT`, `ETHUSDT`, `SOLUSDT`).

### Steps
1. **Find the Trading Pair**
   - Visit [Coinbase’s Exchange](https://www.Coinbase.com/en/trade) or API docs (`https://api.Coinbase.com/api/v3/ticker/24hr`).
   - Identify the trading pair for your cryptocurrency, typically in the format `<COIN>USDT` (e.g., `ETHUSDT` for Ethereum, `ADAUSDT` for Cardano).
   - Test the pair with:
     ```bash
     curl https://api.Coinbase.com/api/v3/ticker/24hr?symbol=ETHUSDT
     ```
     Ensure it returns data like `{"symbol":"ETHUSDT","lastPrice":"3456.78","priceChangePercent":"1.25"}`.

2. **Update `.env`**
   - Edit `.env` and change `TRADING_PAIR`:
     ```env
     BOT_TOKEN=your_discord_bot_token
     TRADING_PAIR=ETHUSDT
     ```
   - Save the file.

3. **Restart the Bot**
   ```bash
   python bot.py
   ```
   - The bot will now track the new cryptocurrency (e.g., nickname: “$3,456.78”, activity: “+1.25% ETHUSD”).

### Supported Cryptocurrencies
- **Common Pairs**: `BTCUSDT` (Bitcoin), `ETHUSDT` (Ethereum), `SOLUSDT` (Solana), `ADAUSDT` (Cardano), `XRPUSDT` (Ripple), `BNBUSDT` (Coinbase Coin).
- **Others**: Check Coinbase’s API or exchange for available `<COIN>USDT` pairs.
- **Note**: Ensure the pair ends with `USDT` for USD-based pricing. Other pairs (e.g., `BTCBUSD`) may work but require code adjustments.

## Troubleshooting
- **Bot Doesn’t Start**
  - Check `.env` for correct `BOT_TOKEN` and `TRADING_PAIR`.
  - Verify dependencies: `pip install discord.py aiohttp python-dotenv`.
  - Ensure Python 3.8+: `python --version`.
  - Look for logs like “Error running bot: Invalid token”.

- **Nickname Doesn’t Update**
  - Check logs for “Bot member not found in a server” (bot not in server) or “Failed to update nickname” (e.g., missing permissions).
  - Ensure bot has “Change Nickname” permission in each server.
  - Verify bot is invited to servers.
  - Check for rate limit errors: “429 Too Many Requests”.

- **Activity Doesn’t Update**
  - Confirm logs show “Activity set to: +X.XX% <COIN>USD” every 5 minutes.
  - Refresh Discord (Ctrl+R) or check on mobile.

- **Coinbase API Issues**
  - Test the API:
    ```bash
    curl https://api.Coinbase.com/api/v3/ticker/24hr?symbol=<TRADING_PAIR>
    ```
  - Ensure `TRADING_PAIR` is valid (e.g., `BTCUSDT`, not `BTC`).
  - Check for “Coinbase API error” in logs.

- **Logs**
  - All logs are console-only and use “server” (not “guild”).
  - Example errors: “Error in update_nickname: ...”, “Failed to update nickname: 403 Forbidden”.

## Contributing
- Fork the repository and submit pull requests for improvements.
- Suggest new features (e.g., multiple crypto tracking, alternative APIs).

## License
MIT License. See [LICENSE](LICENSE) for details.
