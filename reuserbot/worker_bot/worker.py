"""
╔═══════════════════════════════════════════════════════════╗
║  worker.py — Worker Userbot Engine Core                   ║
║  Pyrogram Engine with Auto Reconnect & Plugin Loader      ║
║  Supports CLI Args, Environment Variables & Config files  ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

# Setup paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

import worker_globals

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [MUSERBOT WORKER] - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("WorkerBot")

# Fetch credentials from either CLI args or Environment variables
API_ID = None
API_HASH = None
SESSION_STRING = None

if len(sys.argv) >= 4:
    try:
        API_ID = int(sys.argv[1])
        API_HASH = sys.argv[2]
        SESSION_STRING = sys.argv[3]
    except ValueError:
        logger.warning("Invalid API_ID in argv, checking environment variables...")

if not API_ID:
    env_api_id = os.getenv("API_ID")
    if env_api_id and env_api_id.isdigit():
        API_ID = int(env_api_id)

if not API_HASH:
    API_HASH = os.getenv("API_HASH")

if not SESSION_STRING:
    SESSION_STRING = os.getenv("SESSION_STRING") or os.getenv("SESSION")

if not API_ID or not API_HASH or not SESSION_STRING:
    logger.critical(
        "❌ Missing required Telegram credentials!\n"
        "Provide via CLI: python3 worker.py <api_id> <api_hash> <session_string>\n"
        "Or via Env: API_ID, API_HASH, SESSION_STRING"
    )
    sys.exit(1)

# Pyrogram Client Initialization
from pyrogram import Client, idle
from pyrogram.errors import FloodWait

PLUGINS_PATH = os.path.join(CURRENT_DIR, "plugins")
# Relative plugins directory name for Pyrogram
plugins_dict = dict(root="plugins") if os.path.isdir(PLUGINS_PATH) else None

app = Client(
    name="muserbot_worker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True,       # Pure memory session, no disk clutter
    workers=10,           # High concurrency for parallel spam, raid, animations
    plugins=plugins_dict
)

@app.on_message(group=-1)
async def global_tracker(client, message):
    """Update global reference variables"""
    if message.chat:
        worker_globals.LAST_CHAT_ID = message.chat.id

async def main():
    try:
        logger.info("🚀 Booting MUserBot Pro Worker Engine...")
        await app.start()
        me = await app.get_me()
        logger.info(f"✅ MUserBot Pro Online! User: {me.first_name} (@{me.username or 'NoUsername'}) [ID: {me.id}]")
        
        # Send startup greeting to Saved Messages
        try:
            startup_banner = (
                "⚡ <b>MUserBot Pro Started Successfully!</b>\n\n"
                f"👤 <b>User:</b> {me.first_name}\n"
                f"🆔 <b>ID:</b> <code>{me.id}</code>\n"
                f"🚀 <b>Engine:</b> Pyrogram Async v2.0+\n\n"
                "💡 Type <code>.alive</code> in any chat to test."
            )
            await app.send_message("me", startup_banner)
        except Exception:
            pass
            
        await idle()
        
    except FloodWait as e:
        logger.warning(f"⚠️ Telegram FloodWait: Sleeping for {e.value} seconds.")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.critical(f"❌ Worker Bot Fatal Error: {e}")
    finally:
        logger.info("🛑 Stopping MUserBot Worker Engine...")
        try:
            if app.is_connected:
                await app.stop()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker stopped manually.")
