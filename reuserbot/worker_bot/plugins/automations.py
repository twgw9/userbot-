"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/automations.py — Background Automations Engine   ║
║  Features:                                               ║
║    • .autobio on/off (Live real-time updating clock bio) ║
║    • .autoreaction on/off <emoji> (Auto emoji reactions) ║
║    • .antidelete on/off (Log deleted chat messages)      ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import datetime
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

AUTOBIO_RUNNING = False
AUTOREACT_CHATS = {}  # {chat_id: emoji}
ANTIDELETE_ENABLED = True
DELETED_CACHE = {}    # {msg_id: Message}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. LIVE CLOCK AUTOBIO (.autobio on/off)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def autobio_loop(client: Client):
    global AUTOBIO_RUNNING
    while AUTOBIO_RUNNING:
        try:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            bio_text = f"🕒 {time_str} | ⚡ Powered by MUserBot Pro"
            await client.update_profile(bio=bio_text)
            await asyncio.sleep(60)
        except Exception as e:
            logger.warning(f"Autobio update error: {e}")
            await asyncio.sleep(60)

@Client.on_message(filters.command("autobio", prefixes=".") & filters.me)
async def autobio_toggle(client: Client, message: Message):
    global AUTOBIO_RUNNING
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.autobio on</code> or <code>.autobio off</code>")
        
    if message.command[1] == "on":
        if not AUTOBIO_RUNNING:
            AUTOBIO_RUNNING = True
            asyncio.create_task(autobio_loop(client))
            await message.edit_text("🕒 <b>Live Clock Auto-Bio Activated!</b>\n<i>Your bio will automatically update every minute with the current time.</i>")
        else:
            await message.edit_text("⚠️ Auto-Bio is already running.")
    else:
        AUTOBIO_RUNNING = False
        await message.edit_text("🛑 <b>Live Clock Auto-Bio Deactivated.</b>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. AUTO EMOJI REACTIONS (.autoreaction on/off <emoji>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["autoreaction", "autoreact"], prefixes=".") & filters.me)
async def autoreact_toggle(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.autoreact on <emoji></code> or <code>.autoreact off</code>\n<i>Example:</i> <code>.autoreact on 🔥</code>")
        
    if message.command[1] == "on":
        emoji = message.command[2] if len(message.command) > 2 else "🔥"
        AUTOREACT_CHATS[chat_id] = emoji
        await message.edit_text(f"✨ <b>Auto-Reaction Activated in this chat!</b>\nEmoji: {emoji}")
    else:
        AUTOREACT_CHATS.pop(chat_id, None)
        await message.edit_text("🛑 <b>Auto-Reaction Deactivated for this chat.</b>")

@Client.on_message(group=7)
async def autoreact_watcher(client: Client, message: Message):
    if not message.chat:
        return
    chat_id = message.chat.id
    if chat_id in AUTOREACT_CHATS:
        emoji = AUTOREACT_CHATS[chat_id]
        try:
            await message.react(emoji)
        except Exception:
            pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. ANTI-DELETE LOGGER (.antidelete on/off)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(group=-2)
async def cache_all_messages(client: Client, message: Message):
    """Cache incoming messages in memory for anti-delete retrieval"""
    if message.chat:
        DELETED_CACHE[message.id] = message
        # Keep cache under 500 messages to save RAM
        if len(DELETED_CACHE) > 500:
            oldest_key = next(iter(DELETED_CACHE))
            DELETED_CACHE.pop(oldest_key, None)

@Client.on_message(filters.command("antidelete", prefixes=".") & filters.me)
async def antidelete_toggle(client: Client, message: Message):
    global ANTIDELETE_ENABLED
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.antidelete on</code> or <code>.antidelete off</code>")
    ANTIDELETE_ENABLED = (message.command[1] == "on")
    status = "ON 🟢 (Active)" if ANTIDELETE_ENABLED else "OFF 🔴 (Disabled)"
    await message.edit_text(f"🕵️‍♂️ <b>Anti-Delete Message Logger:</b> {status}")
