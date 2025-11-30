import logging
import asyncio
import sys
import os

# Add src to path so we can import from src folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.telegram_bot import TelegramBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    try:
        logger.info("🚀 Starting Crypto Arbitrage Bot...")
        
        # Initialize and run the bot
        bot = TelegramBot()
        await bot.run()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Check if we're running on Render
    if os.getenv('RENDER'):
        logger.info("🌐 Running on Render platform")
    
    # Run the bot
    asyncio.run(main())
