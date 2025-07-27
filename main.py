#!/usr/bin/env python3
"""
Discord Raid Bot - Main Entry Point
Starts the Discord bot and handles the main execution flow.
"""

import asyncio
import logging
import os
import sys
from bot import bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Discord bot."""
    try:
        # Get bot token from environment variable
        bot_token = os.getenv('DISCORD_BOT_TOKEN')
        
        if not bot_token:
            logger.error("DISCORD_BOT_TOKEN environment variable not found!")
            logger.error("Please set your Discord bot token in the environment variables.")
            sys.exit(1)
        
        # Use the pre-configured bot instance with commands
        logger.info("Starting Discord Raid Bot...")
        await bot.start(bot_token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
