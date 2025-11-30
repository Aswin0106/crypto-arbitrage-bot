import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Exchange configuration
    EXCHANGES = {
        'binance': {'enable': True, 'timeout': 30000},
        'kucoin': {'enable': True, 'timeout': 30000},
        'huobi': {'enable': True, 'timeout': 30000},
        'okx': {'enable': True, 'timeout': 30000}
    }
    
    # Trading pairs to monitor
    TRADING_PAIRS = [
        'BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT',
        'LINK/USDT', 'MATIC/USDT', 'SOL/USDT', 'XRP/USDT'
    ]
    
    # Arbitrage settings
    MIN_PROFIT_PERCENT = 0.1
    REQUEST_DELAY = 1
