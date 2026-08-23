"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/spam.py — High-Performance Spam & Flooder Engine ║
║  Features:                                               ║
║    • .spam <count> [delay] <text> (Custom delay spam)    ║
║    • .fastspam / .uspam (Ultra-fast burst spam)          ║
║    • .dmspam <count> <user> <text> (Private chat spam)   ║
║    • .sspam (Sticker flipper spam)                       ║
║    • .gspam, .gset, .gclear (Gallery stickers)           ║
║    • .stop (Universal emergency halt)                    ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid
import worker_globals

logger = logging.getLogger(__name__)

def parse_spam_args(text: str):
    parts = text.split()
    if len(parts) < 3:
        return None, None, None
        
    if not parts[1].isdigit():
        return None, None, None
    count = int(parts[1])
    
    try:
        delay = float(parts[2])
        spam_text = " ".join(parts[3:])
        if not spam_text:
            return None, None, None
    except ValueError:
        delay = 0.5
        spam_text = " ".join(parts[2:])
        
    return count, delay, spam_text

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 0. UNIVERSAL STOP COMMAND (.stop)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["stop", "halt", "cancel"], prefixes=".") & filters.me)
async def stop_all_tasks(client: Client, message: Message):
    chat_id = message.chat.id
    worker_globals.stop_task(chat_id)
    worker_globals.stop_all_chat_tasks()
    await message.edit_text("🛑 <b>All Running Spam, Raid & Tagging Tasks Terminated!</b>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. NORMAL CUSTOM DELAY SPAM (.spam)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("spam", prefixes=".") & filters.me)
async def spam_command(client: Client, message: Message):
    count, delay, spam_text = parse_spam_args(message.text)
    if not count:
        return await message.edit_text(
            "❌ <b>Usage:</b> <code>.spam <count> <text></code> or <code>.spam <count> <delay> <text></code>\n"
            "<i>Example:</i> <code>.spam 10 Hello World</code>"
        )
        
    chat_id = message.chat.id
    await message.delete()
    worker_globals.start_task(chat_id)
    
    for _ in range(count):
        if not worker_globals.is_task_active(chat_id):
            break
        try:
            await client.send_message(chat_id, spam_text)
            if delay > 0:
                await asyncio.sleep(delay)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            break
            
    worker_globals.stop_task(chat_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. ULTRA FAST BURST SPAM (.fastspam, .uspam)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["fastspam", "uspam"], prefixes=".") & filters.me)
async def fast_spam_command(client: Client, message: Message):
    parts = message.text.split(" ", 2)
    if len(parts) < 3 or not parts[1].isdigit():
        return await message.edit_text("❌ <b>Usage:</b> <code>.fastspam <count> <text></code>")
        
    count = int(parts[1])
    spam_text = parts[2]
    chat_id = message.chat.id
    
    await message.delete()
    worker_globals.start_task(chat_id)
    
    for _ in range(count):
        if not worker_globals.is_task_active(chat_id):
            break
        try:
            await client.send_message(chat_id, spam_text)
            await asyncio.sleep(0.08)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            break
            
    worker_globals.stop_task(chat_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. DIRECT PRIVATE CHAT SPAM (.dmspam)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("dmspam", prefixes=".") & filters.me)
async def dm_spam_command(client: Client, message: Message):
    parts = message.text.split(" ", 3)
    if len(parts) < 4 or not parts[1].isdigit():
        return await message.edit_text("❌ <b>Usage:</b> <code>.dmspam <count> <@username/id> <text></code>")
        
    count = int(parts[1])
    target = parts[2]
    spam_text = parts[3]
    chat_id = message.chat.id
    
    await message.edit_text(f"🚀 <b>Starting DM Spam on {target}...</b>")
    worker_globals.start_task(chat_id)
    
    try:
        user = await client.get_users(target)
        target_id = user.id
    except Exception as e:
        return await message.edit_text(f"❌ User not found: <code>{e}</code>")
        
    for _ in range(count):
        if not worker_globals.is_task_active(chat_id):
            break
        try:
            await client.send_message(target_id, spam_text)
            await asyncio.sleep(0.4)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            break
            
    worker_globals.stop_task(chat_id)
    await message.edit_text("✅ <b>DM Spam Completed!</b>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. REPLIED STICKER SPAM (.sspam <count>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("sspam", prefixes=".") & filters.me)
async def sticker_spam_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.edit_text("❌ Reply to a sticker with <code>.sspam <count></code>")
        
    parts = message.text.split()
    count = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 5
    sticker_id = message.reply_to_message.sticker.file_id
    chat_id = message.chat.id
    
    await message.delete()
    worker_globals.start_task(chat_id)
    
    for _ in range(count):
        if not worker_globals.is_task_active(chat_id):
            break
        try:
            await client.send_sticker(chat_id, sticker_id)
            await asyncio.sleep(0.4)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            break
            
    worker_globals.stop_task(chat_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. GALLERY STICKER SPAM (.gspam, .gset, .gclear)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("gset", prefixes=".") & filters.me)
async def gset_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.edit_text("❌ Reply to a sticker to save it for <code>.gspam</code>")
        
    sid = message.reply_to_message.sticker.file_id
    if sid not in worker_globals.SAVED_STICKERS:
        worker_globals.SAVED_STICKERS.append(sid)
        await message.edit_text(f"✅ Sticker saved! (Total in pool: {len(worker_globals.SAVED_STICKERS)})")
    else:
        await message.edit_text("⚠️ Sticker is already in pool.")

@Client.on_message(filters.command("gclear", prefixes=".") & filters.me)
async def gclear_cmd(client: Client, message: Message):
    worker_globals.SAVED_STICKERS.clear()
    await message.edit_text("🗑️ <b>Saved sticker gallery cleared!</b>")

@Client.on_message(filters.command("gspam", prefixes=".") & filters.me)
async def gspam_cmd(client: Client, message: Message):
    if not worker_globals.SAVED_STICKERS:
        return await message.edit_text("❌ No stickers in gallery! Use <code>.gset</code> (replying to sticker) first.")
        
    parts = message.text.split()
    count = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 5
    chat_id = message.chat.id
    
    await message.delete()
    worker_globals.start_task(chat_id)
    
    for i in range(count):
        if not worker_globals.is_task_active(chat_id):
            break
        sid = worker_globals.SAVED_STICKERS[i % len(worker_globals.SAVED_STICKERS)]
        try:
            await client.send_sticker(chat_id, sid)
            await asyncio.sleep(0.4)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            break
            
    worker_globals.stop_task(chat_id)
