"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/info.py — User & Chat Intelligence Inspector     ║
║  Features:                                               ║
║    • .info (Comprehensive User Details & DC Inspector)   ║
║    • .id (Chat ID, Replied Message & User ID fetcher)    ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid, RPCError

logger = logging.getLogger(__name__)

async def get_target_user(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = message.text.split()
    if len(parts) >= 2:
        try:
            return await client.get_users(parts[1])
        except Exception:
            return None
    return await client.get_me()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. USER INFO (.info)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("info", prefixes=".") & filters.me)
async def info_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Target user not found.")
        
    msg = await message.edit_text("🔍 <code>Fetching user intel...</code>")
    
    try:
        chat = await client.get_chat(user.id)
        dc = getattr(user, 'dc_id', 'Unknown')
        status = "🟢 Online" if getattr(user, 'status', None) == "online" else "🔴 Offline"
        
        info_text = (
            "┌────── ˹ ᴜsᴇʀ ɪɴғᴏ ˼ ⏤͟͟͞͞★\n"
            f"┆◍ <b>First Name:</b> <code>{user.first_name}</code>\n"
            f"┆● <b>Last Name:</b> <code>{user.last_name or 'None'}</code>\n"
            f"┆◍ <b>User ID:</b> <code>{user.id}</code>\n"
            f"┆● <b>Username:</b> @{user.username if user.username else 'None'}\n"
            f"┆◍ <b>Data Center (DC):</b> <code>DC{dc}</code>\n"
            f"┆● <b>Status:</b> {status}\n"
            f"┆◍ <b>Bot Account:</b> {'Yes' if user.is_bot else 'No'}\n"
            f"┆● <b>Scam / Fake:</b> {'⚠️ Yes' if getattr(user, 'is_scam', False) else '✅ No'}\n"
            f"┆◍ <b>Bio:</b> <i>{chat.bio or 'None'}</i>\n"
            "└────────────────────────•"
        )
        await msg.edit_text(info_text)
    except Exception as e:
        await msg.edit_text(f"❌ Info Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. ID FETCHER (.id)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("id", prefixes=".") & filters.me)
async def id_cmd(client: Client, message: Message):
    chat = message.chat
    chat_type = str(chat.type.value).capitalize()
    
    text = (
        "┌────── ˹ ɪᴅ ɪɴғᴏ ˼ ⏤͟͟͞͞★\n"
        f"┆◍ <b>Chat Title:</b> <code>{chat.title or 'Private'}</code>\n"
        f"┆● <b>Chat ID:</b> <code>{chat.id}</code>\n"
        f"┆◍ <b>Chat Type:</b> <code>{chat_type}</code>\n"
    )
    
    if message.reply_to_message:
        replied = message.reply_to_message
        r_user = replied.from_user
        text += (
            f"┆● <b>Replied Msg ID:</b> <code>{replied.id}</code>\n"
            f"┆◍ <b>Replied User ID:</b> <code>{r_user.id if r_user else 'Channel'}</code>\n"
        )
    text += "└────────────────────────•"
    await message.edit_text(text)
