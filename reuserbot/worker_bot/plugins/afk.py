"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/afk.py — Smart AFK Mode & Mention Logger         ║
║  Features:                                               ║
║    • .afk [reason] (Activate AFK mode)                   ║
║    • Auto-reply to PMs and group mentions with time      ║
║    • Logs all mentions and DMs in Saved Messages         ║
║    • Auto-disables on master message with summary        ║
╚═══════════════════════════════════════════════════════════╝
"""

import time
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
import worker_globals

logger = logging.getLogger(__name__)

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    time_list.reverse()
    return ":".join(time_list) or "0s"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SET AFK (.afk [reason])
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("afk", prefixes=".") & filters.me)
async def set_afk(client: Client, message: Message):
    reason = "Busy / Away from keyboard"
    parts = message.text.split(" ", 1)
    if len(parts) > 1:
        reason = parts[1].strip()
        
    worker_globals.AFK_DATA = {
        "is_afk": True,
        "reason": reason,
        "time": time.time(),
        "mentions": []
    }
    
    await message.edit_text(
        f"💤 <b>AFK Mode Activated!</b>\n\n"
        f"<b>Reason:</b> <i>{reason}</i>\n"
        f"<i>I will notify anyone who mentions or DMs you.</i>"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. TURN OFF AFK (.unafk)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("unafk", prefixes=".") & filters.me)
async def unafk_cmd(client: Client, message: Message):
    if not worker_globals.AFK_DATA.get("is_afk"):
        return await message.edit_text("ℹ️ You are not currently AFK.")
        
    afk_duration = get_readable_time(int(time.time() - worker_globals.AFK_DATA.get("time", time.time())))
    pings_count = len(worker_globals.AFK_DATA.get("mentions", []))
    
    worker_globals.AFK_DATA["is_afk"] = False
    
    await message.edit_text(
        f"✨ <b>Welcome Back! AFK Mode Disabled.</b>\n\n"
        f"⏳ <b>AFK Duration:</b> <code>{afk_duration}</code>\n"
        f"🔔 <b>Total Pings:</b> <code>{pings_count}</code>"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. WATCHER: Auto-Disable AFK on Master's Message
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.me & ~filters.command(["afk", "unafk"], prefixes="."), group=3)
async def auto_unafk_watcher(client: Client, message: Message):
    if worker_globals.AFK_DATA.get("is_afk"):
        afk_duration = get_readable_time(int(time.time() - worker_globals.AFK_DATA.get("time", time.time())))
        pings_count = len(worker_globals.AFK_DATA.get("mentions", []))
        worker_globals.AFK_DATA["is_afk"] = False
        
        try:
            status_msg = await client.send_message(
                message.chat.id,
                f"✨ <i>I am back online! Was AFK for {afk_duration} ({pings_count} pings received).</i>"
            )
            await asyncio.sleep(4)
            await status_msg.delete()
        except Exception:
            pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. WATCHER: Auto-Reply to Incoming Pings & DMs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message((filters.private | filters.mentioned) & ~filters.me, group=2)
async def afk_reply_watcher(client: Client, message: Message):
    if not worker_globals.AFK_DATA.get("is_afk"):
        return
        
    afk_time = worker_globals.AFK_DATA.get("time", time.time())
    afk_reason = worker_globals.AFK_DATA.get("reason", "Busy")
    elapsed = get_readable_time(int(time.time() - afk_time))
    
    sender_name = message.from_user.first_name if message.from_user else "Someone"
    sender_id = message.from_user.id if message.from_user else 0
    chat_title = message.chat.title if message.chat.title else "Private Message"
    
    # Auto-reply notice
    reply_text = (
        f"💤 <b>My Master is currently AFK!</b>\n\n"
        f"⏳ <b>AFK Since:</b> <code>{elapsed}</code>\n"
        f"📝 <b>Reason:</b> <i>{afk_reason}</i>\n\n"
        f"<i>Please leave your message, master will reply soon.</i>"
    )
    
    try:
        await message.reply_text(reply_text)
    except Exception:
        pass
        
    # Log mention to Saved Messages
    mention_entry = {
        "user": sender_name,
        "user_id": sender_id,
        "chat": chat_title,
        "text": message.text or message.caption or "Media Message",
        "time": elapsed
    }
    worker_globals.AFK_DATA["mentions"].append(mention_entry)
    
    try:
        log_msg = (
            f"🔔 <b>AFK Ping Notification</b>\n\n"
            f"👤 <b>From:</b> {sender_name} (<code>{sender_id}</code>)\n"
            f"💬 <b>Chat:</b> {chat_title}\n"
            f"📩 <b>Message:</b> <i>{mention_entry['text']}</i>\n"
            f"🕒 <b>While AFK for:</b> {elapsed}"
        )
        await client.send_message("me", log_msg)
    except Exception:
        pass
