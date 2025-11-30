import ccxt
import asyncio
import logging
from typing import List, Dict, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    def __init__(self):
        self.exchanges = {}
        self.setup_exchanges()
    
    def setup_exchanges(self):
        """Initialize exchanges with proper configuration"""
        exchange_configs = {
            'binance': {
                'enableRateLimit': True,
                'timeout': 30000,
                'rateLimit': 1000,
            },
            'kucoin': {
                'enableRateLimit': True,
                'timeout': 30000,
            },
            'huobi': {
                'enableRateLimit': True,
                'timeout': 30000,
            },
            'okx': {
                'enableRateLimit': True,
                'timeout': 30000,
            }
        }
        
        for exchange_id, config in exchange_configs.items():
            try:
                exchange_class = getattr(ccxt, exchange_id)
                self.exchanges[exchange_id] = exchange_class(config)
                logger.info(f"✅ Initialized {exchange_id}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {exchange_id}: {e}")
    
    async def fetch_ticker(self, exchange, symbol: str) -> Optional[Dict]:
        """Fetch ticker data from exchange with error handling"""
        try:
            ticker = exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'exchange': exchange.id,
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'last': ticker.get('last'),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch {symbol} from {exchange.id}: {e}")
            return None
    
    async def scan_pair(self, symbol: str) -> List[Dict]:
        """Scan for arbitrage opportunities for a specific pair"""
        opportunities = []
        
        # Fetch prices from all exchanges
        tasks = []
        for exchange in self.exchanges.values():
            tasks.append(self.fetch_ticker(exchange, symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        prices = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        if len(prices) < 2:
            return opportunities
        
        # Find best bid and ask
        best_ask = min(prices, key=lambda x: x['ask'] if x['ask'] else float('inf'))
        best_bid = max(prices, key=lambda x: x['bid'] if x['bid'] else 0)
        
        # Check if we have valid prices
        if (best_ask['ask'] and best_bid['bid'] and 
            best_ask['ask'] > 0 and best_bid['bid'] > best_ask['ask']):
            
            profit_percent = ((best_bid['bid'] - best_ask['ask']) / best_ask['ask']) * 100
            
            if profit_percent >= Config.MIN_PROFIT_PERCENT:
                opportunity = {
                    'symbol': symbol,
                    'buy_exchange': best_ask['exchange'],
                    'sell_exchange': best_bid['exchange'],
                    'buy_price': best_ask['ask'],
                    'sell_price': best_bid['bid'],
                    'profit_percent': profit_percent,
                    'spread': best_bid['bid'] - best_ask['ask']
                }
                opportunities.append(opportunity)
                logger.info(f"💰 Found arbitrage: {symbol} - {profit_percent:.2f}%")
        
        return opportunities
    
    async def scan_all_pairs(self) -> List[Dict]:
        """Scan all trading pairs for arbitrage opportunities"""
        all_opportunities = []
        
        for symbol in Config.TRADING_PAIRS:
            try:
                opportunities = await self.scan_pair(symbol)
                all_opportunities.extend(opportunities)
                await asyncio.sleep(Config.REQUEST_DELAY)  # Rate limiting
            except Exception as e:
                logger.error(f"❌ Error scanning {symbol}: {e}")
        
        # Sort by profit percentage (highest first)
        all_opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        return all_opportunities
    
    def get_exchange_status(self) -> Dict:
        """Get status of all exchanges"""
        status = {}
        for name, exchange in self.exchanges.items():
            try:
                # Test connectivity
                exchange.fetch_ticker('BTC/USDT')
                status[name] = {
                    'status': '✅ Online',
                    'has': exchange.has,
                    'timeout': exchange.timeout
                }
            except Exception as e:
                status[name] = {
                    'status': '❌ Offline',
                    'error': str(e)
                }
        return status
