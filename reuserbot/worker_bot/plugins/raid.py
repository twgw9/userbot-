"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/raid.py — Ultimate Raid & Roast Engine           ║
║  Features:                                               ║
║    • .raid, .hiraid, .mraid (High-speed roast raids)     ║
║    • .rraid (Auto-Reply target raid)                     ║
║    • .flirt, .shayari, .roast (Fun lines)                ║
║    • Custom raid library (.setraid, .delraid, .showraid) ║
║    • Instant .stop task cancellation                     ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import json
import random
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import worker_globals

logger = logging.getLogger(__name__)

RAID_TEXTS_FILE = "raid_texts.json"
REPLY_RAID_ACTIVE = {}  # {chat_id: target_user_id}

# Pre-built Rich Libraries
HINDI_RAID = [
    "Abe tere jaisa namuna maine aaj tak nahi dekha! 😂",
    "Beta baap ke aage bakchodi nahi karte! 🔥",
    "Tu wahi hai na jisko group se laat maar ke nikaala tha? 🤣",
    "Aukat me reh le beta, varna screenshot leke meme bana dunga! 💀",
    "Akal ghaas charne gayi hai kya teri? 🤡",
    "Kitna vella hai re tu, 24 ghante Telegram pe pada rehta hai! 🥱",
    "Tere se behtar dimaag toh mere wifi router ka hai! 📡",
    "Sun be chapri, apna gyaan apne paas rakh! 🤫",
    "Shakal dekh ke lagta hai subah mirchi kha ke utha tha! 🌶️",
    "Beta group me aane ki aukaat nahi, baatein aisi jaise Ambani ka beta ho! 💸"
]

ROAST_TEXTS = [
    "You bring everyone so much joy when you leave the chat! 🚀",
    "I'd agree with you, but then we’d both be wrong. 🤡",
    "I'm not insulting you, I'm just describing you accurately. 💀",
    "Your secrets are always safe with me. I don't even listen to you. 😴",
    "You are proof that evolution can go in reverse. 🦖",
    "If laughter is the best medicine, your face must be curing the world! 😂",
    "I thought of you today. It reminded me to take out the trash. 🗑️"
]

FLIRT_TEXTS = [
    "Are you a magician? Because whenever I look at you, everyone else disappears. ✨",
    "Is your name Google? Because you have everything I’ve been searching for. 💖",
    "Are you a parking ticket? Because you’ve got 'FINE' written all over you. 😉",
    "Do you have a map? I keep getting lost in your eyes. 🌹",
    "If you were a vegetable, you'd be a cute-cumber! 🥒❤️"
]

SHAYARI_TEXTS = [
    "Khamoshi me bhi ek shor hota hai, har kisi ka apna ek daur hota hai! 🌹",
    "Zindagi ke safar me dhoop toh hogi, jo chal sako toh chalo! ✨",
    "Hum wahan khade hote hain jahan matter bade hote hain! 🔥",
    "Waqt aane pe bata denge tujhe ae aasmaan, hum abhi se kya batayein kya hamare dil me hai! 👑"
]

def load_raid_texts() -> list:
    if os.path.exists(RAID_TEXTS_FILE):
        try:
            with open(RAID_TEXTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_raid_texts(texts: list):
    try:
        with open(RAID_TEXTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(texts, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving raid texts: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. RAID COMMANDS (.raid, .hiraid, .roast, .flirt, .shayari)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def execute_raid(client: Client, message: Message, texts: list, default_count: int = 5):
    parts = message.text.split()
    count = default_count
    target = ""
    
    if len(parts) >= 2 and parts[1].isdigit():
        count = int(parts[1])
        if len(parts) >= 3:
            target = parts[2]
    elif len(parts) >= 2:
        target = parts[1]
        
    chat_id = message.chat.id
    await message.delete()
    worker_globals.start_task(chat_id)
    
    for i in range(count):
        if not worker_globals.is_task_active(chat_id):
            break
        text = random.choice(texts)
        if target:
            text = f"{target} {text}"
        try:
            await client.send_message(chat_id, text)
            await asyncio.sleep(0.6)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            
    worker_globals.stop_task(chat_id)

@Client.on_message(filters.command("hiraid", prefixes=".") & filters.me)
async def hindi_raid_cmd(client: Client, message: Message):
    custom = load_raid_texts()
    pool = custom + HINDI_RAID if custom else HINDI_RAID
    await execute_raid(client, message, pool)

@Client.on_message(filters.command(["raid", "mraid"], prefixes=".") & filters.me)
async def general_raid_cmd(client: Client, message: Message):
    await execute_raid(client, message, ROAST_TEXTS)

@Client.on_message(filters.command("flirt", prefixes=".") & filters.me)
async def flirt_cmd(client: Client, message: Message):
    await execute_raid(client, message, FLIRT_TEXTS, default_count=1)

@Client.on_message(filters.command("shayari", prefixes=".") & filters.me)
async def shayari_cmd(client: Client, message: Message):
    await execute_raid(client, message, SHAYARI_TEXTS, default_count=1)

@Client.on_message(filters.command("roast", prefixes=".") & filters.me)
async def roast_cmd(client: Client, message: Message):
    await execute_raid(client, message, ROAST_TEXTS, default_count=1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. REPLY RAID (.rraid on/off)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("rraid", prefixes=".") & filters.me)
async def toggle_reply_raid(client: Client, message: Message):
    chat_id = message.chat.id
    
    if len(message.command) >= 2 and message.command[1].lower() in ["off", "stop"]:
        REPLY_RAID_ACTIVE.pop(chat_id, None)
        return await message.edit_text("🛑 <b>Reply Raid Deactivated in this chat!</b>")
        
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.edit_text("❌ Reply to target user with <code>.rraid</code> to activate Reply Raid.")
        
    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    REPLY_RAID_ACTIVE[chat_id] = target_id
    
    await message.edit_text(f"🔥 <b>Reply Raid Activated!</b>\nTarget: <a href='tg://user?id={target_id}'>{target_name}</a>\n<i>I will auto-roast whenever they send a message.</i>")

@Client.on_message(~filters.me & filters.group, group=4)
async def reply_raid_watcher(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in REPLY_RAID_ACTIVE:
        return
        
    target_id = REPLY_RAID_ACTIVE[chat_id]
    if message.from_user and message.from_user.id == target_id:
        custom = load_raid_texts()
        pool = custom + HINDI_RAID if custom else HINDI_RAID
        roast = random.choice(pool)
        try:
            await message.reply_text(roast)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. CUSTOM RAID TEXT MANAGEMENT (.setraid, .delraid, .showraid)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("setraid", prefixes=".") & filters.me)
async def set_custom_raid(client: Client, message: Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.setraid <your custom roast text></code>")
    text = parts[1].strip()
    texts = load_raid_texts()
    if text not in texts:
        texts.append(text)
        save_raid_texts(texts)
        await message.edit_text(f"✅ <b>Custom raid text added!</b> (Total: {len(texts)})")
    else:
        await message.edit_text("⚠️ This text is already saved in your library.")

@Client.on_message(filters.command("showraid", prefixes=".") & filters.me)
async def show_raid_texts(client: Client, message: Message):
    texts = load_raid_texts()
    if not texts:
        return await message.edit_text("ℹ️ No custom raid texts saved yet. Use <code>.setraid <text></code>.")
    msg = f"📜 <b>Custom Raid Texts ({len(texts)}):</b>\n\n"
    for i, t in enumerate(texts[:15], 1):
        msg += f"{i}. <i>{t}</i>\n"
    await message.edit_text(msg)

@Client.on_message(filters.command("delraid", prefixes=".") & filters.me)
async def del_raid_texts(client: Client, message: Message):
    save_raid_texts([])
    await message.edit_text("🗑️ <b>All custom raid texts cleared!</b>")
