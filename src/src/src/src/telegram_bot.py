import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from src.arbitrage import ArbitrageEngine
from src.config import Config

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.arbitrage_engine = ArbitrageEngine()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
🤖 Hello {user.first_name}!

Welcome to Crypto Arbitrage Bot!

I can help you find arbitrage opportunities across multiple exchanges.

📊 **Available Commands:**
/start - Show this welcome message
/scan - Scan BTC/USDT for arbitrage
/scan_all - Scan all trading pairs
/status - Check exchange status
/help - Show help information

🔍 **Monitoring:** {len(Config.TRADING_PAIRS)} trading pairs
💱 **Exchanges:** {', '.join(self.arbitrage_engine.exchanges.keys())}

Ready to find profitable opportunities! 🚀
        """
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when the command /help is issued."""
        help_text = """
📖 **Crypto Arbitrage Bot Help**

**Commands:**
/scan - Find arbitrage opportunities for BTC/USDT
/scan_all - Scan all configured trading pairs
/status - Check connectivity with all exchanges
/help - Show this help message

**How it works:**
1. Fetches prices from multiple exchanges
2. Identifies price differences
3. Shows profitable arbitrage opportunities
4. Updates in real-time

**Exchanges Supported:**
• Binance • KuCoin • Huobi • OKX

**Minimum Profit Threshold:** 0.1%
        """
        await update.message.reply_text(help_text)
    
    async def scan_arbitrage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan for arbitrage opportunities in BTC/USDT"""
        await update.message.reply_text("🔍 Scanning BTC/USDT for arbitrage opportunities...")
        
        try:
            opportunities = await self.arbitrage_engine.scan_pair('BTC/USDT')
            
            if not opportunities:
                await update.message.reply_text("❌ No arbitrage opportunities found for BTC/USDT at the moment.")
                return
            
            message = "💰 **BTC/USDT Arbitrage Opportunities:**\n\n"
            for opp in opportunities:
                message += f"""
📈 **Symbol:** {opp['symbol']}
🛒 **Buy at:** {opp['buy_exchange']} - ${opp['buy_price']:.2f}
🛍️ **Sell at:** {opp['sell_exchange']} - ${opp['sell_price']:.2f}
💸 **Profit:** {opp['profit_percent']:.3f}%
💰 **Spread:** ${opp['spread']:.4f}
────────────────────
                """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            error_msg = f"❌ Error scanning arbitrage: {str(e)}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
    
    async def scan_all_pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan all trading pairs for arbitrage opportunities"""
        await update.message.reply_text("🔍 Scanning all trading pairs for arbitrage...")
        
        try:
            opportunities = await self.arbitrage_engine.scan_all_pairs()
            
            if not opportunities:
                await update.message.reply_text("❌ No arbitrage opportunities found across all pairs.")
                return
            
            message = "💰 **Top Arbitrage Opportunities:**\n\n"
            for i, opp in enumerate(opportunities[:10], 1):  # Show top 10
                message += f"""
{i}. **{opp['symbol']}**
   📥 Buy: {opp['buy_exchange']} (${opp['buy_price']:.4f})
   📤 Sell: {opp['sell_exchange']} (${opp['sell_price']:.4f})
   💰 Profit: {opp['profit_percent']:.3f}%
                """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            error_msg = f"❌ Error scanning all pairs: {str(e)}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
    
    async def check_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check the status of all exchanges"""
        await update.message.reply_text("🔄 Checking exchange status...")
        
        try:
            status = self.arbitrage_engine.get_exchange_status()
            
            message = "🏪 **Exchange Status:**\n\n"
            for exchange, info in status.items():
                message += f"**{exchange.capitalize()}:** {info['status']}\n"
            
            message += f"\n📊 **Monitoring {len(Config.TRADING_PAIRS)} pairs**"
            message += f"\n🤖 **Bot Status:** ✅ Running"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            error_msg = f"❌ Error checking status: {str(e)}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
    
    def setup_handlers(self):
        """Setup command handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("scan", self.scan_arbitrage))
        self.application.add_handler(CommandHandler("scan_all", self.scan_all_pairs))
        self.application.add_handler(CommandHandler("status", self.check_status))
    
    async def run(self):
        """Run the bot"""
        if not Config.TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
            return
        
        # Create Application
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start the Bot
        logger.info("🤖 Starting Telegram Bot...")
        await self.application.run_polling()
