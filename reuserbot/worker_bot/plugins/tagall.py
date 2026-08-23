"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/tagall.py — Intelligent Batch & Single Mentioner ║
║  Features:                                               ║
║    • .tagall [text] (High-Speed 5x Batch Invisible Tag)   ║
║    • .admtag (Mention Group Administrators)              ║
║    • .onetag, .gmtag, .gntag, .shtag, .vctag             ║
║    • .randomtag, .emojitag                               ║
║    • .tagstop / .stop (Instant Task Cancellation)        ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChatAdminRequired
import worker_globals

logger = logging.getLogger(__name__)

ACTIVE_TAGS = {}

GMT_TEXTS = ["Good Morning ☀️", "Subah ho gayi uth jao! 🔥", "GM brothers & sisters! ✨", "Have a wonderful day! 🌸"]
GN_TEXTS = ["Good Night 🌙", "So jao ab sab 🛌", "Sweet dreams everyone 😴", "GN dosto! 🌌"]
SH_TEXTS = ["Zindagi ek safar hai suhana 🌹", "Mohabbat ek ibadat hai 🥀", "Waqt har zakhm ko bhar deta hai ✨"]
VC_TEXTS = ["VC pe aao sab jaldi! 🎙️", "Voice chat is live! Join up 🔊", "VC mahfil chalu hai ⚡"]
EMOJIS = ["🔥", "❤️", "😂", "👍", "🚀", "✨", "💎", "👑", "⚡", "🌟"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. BULK INVISIBLE TAG ALL (.tagall)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("tagall", prefixes=".") & filters.me)
async def tagall_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    if message.reply_to_message:
        tag_text = message.reply_to_message.text or message.reply_to_message.caption or "Attention everyone! 📢"
    else:
        parts = message.text.split(" ", 1)
        tag_text = parts[1] if len(parts) > 1 else "Attention everyone! 📢"
        
    await message.delete()
    ACTIVE_TAGS[chat_id] = "tagall"
    worker_globals.ACTIVE_TAGS[chat_id] = "tagall"
    
    status_msg = await client.send_message(chat_id, f"🚀 <b>Starting Tagall...</b>")
    
    try:
        count = 0
        batch_size = 5
        batch_mention = ""
        
        async for member in client.get_chat_members(chat_id):
            if ACTIVE_TAGS.get(chat_id) != "tagall":
                break
                
            if member.user.is_bot or member.user.is_deleted:
                continue
                
            # Invisible Zero-Width Mention
            mention = f"<a href='tg://user?id={member.user.id}'>\u2060</a>"
            batch_mention += f" {mention}"
            count += 1
            
            if count % batch_size == 0:
                try:
                    await client.send_message(chat_id, f"{tag_text}\n{batch_mention}")
                    batch_mention = ""
                    await asyncio.sleep(0.9)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    
        if batch_mention and ACTIVE_TAGS.get(chat_id) == "tagall":
            await client.send_message(chat_id, f"{tag_text}\n{batch_mention}")
            
        await status_msg.edit_text(f"✅ <b>Tagall Completed!</b> Tagged <code>{count}</code> members.")
    except ChatAdminRequired:
        await status_msg.edit_text("❌ Admin rights required to fetch member list.")
    except Exception as e:
        logger.error(f"Tagall Error: {e}")
    finally:
        ACTIVE_TAGS.pop(chat_id, None)
        worker_globals.ACTIVE_TAGS.pop(chat_id, None)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. ADMIN ONLY TAG (.admtag)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("admtag", prefixes=".") & filters.me)
async def admtag_command(client: Client, message: Message):
    chat_id = message.chat.id
    tag_text = message.text.split(" ", 1)[1] if len(message.command) > 1 else "Attention Admins! 🛡️"
    await message.delete()
    
    status_msg = await client.send_message(chat_id, "🛡️ <i>Mentioning administrators...</i>")
    
    try:
        count = 0
        mentions = ""
        async for member in client.get_chat_members(chat_id, filter=filters.ChatMembersFilter.ADMINISTRATORS):
            if member.user.is_bot or member.user.is_deleted:
                continue
            name = member.user.first_name or "Admin"
            mentions += f"• <a href='tg://user?id={member.user.id}'>{name}</a>\n"
            count += 1
            
        await status_msg.edit_text(f"🛡️ <b>{tag_text}</b>\n\n{mentions}")
    except Exception as e:
        await status_msg.edit_text(f"❌ Admin Tag Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. ONE-BY-ONE ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def onetag_engine(client: Client, message: Message, tag_type: str, texts: list = None):
    chat_id = message.chat.id
    ACTIVE_TAGS[chat_id] = tag_type
    worker_globals.ACTIVE_TAGS[chat_id] = tag_type
    
    await message.delete()
    status_msg = await client.send_message(chat_id, f"🚀 <i>Starting {tag_type}...</i>")
    
    try:
        count = 0
        async for member in client.get_chat_members(chat_id):
            if ACTIVE_TAGS.get(chat_id) != tag_type:
                break
            if member.user.is_bot or member.user.is_deleted:
                continue
                
            safe_name = member.user.first_name or "User"
            mention = f"<a href='tg://user?id={member.user.id}'>{safe_name}</a>"
            msg_text = random.choice(texts) if texts else ""
            
            try:
                await client.send_message(chat_id, f"{msg_text} {mention}")
                count += 1
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                
        await status_msg.edit_text(f"✅ <b>{tag_type} Completed!</b> Tagged <code>{count}</code> members.")
    except Exception as e:
        logger.error(f"OneTag Error: {e}")
    finally:
        ACTIVE_TAGS.pop(chat_id, None)
        worker_globals.ACTIVE_TAGS.pop(chat_id, None)

@Client.on_message(filters.command("onetag", prefixes=".") & filters.me)
async def onetag_cmd(client: Client, message: Message):
    await onetag_engine(client, message, "onetag")

@Client.on_message(filters.command("gmtag", prefixes=".") & filters.me)
async def gmtag_cmd(client: Client, message: Message):
    await onetag_engine(client, message, "gmtag", GMT_TEXTS)

@Client.on_message(filters.command("gntag", prefixes=".") & filters.me)
async def gntag_cmd(client: Client, message: Message):
    await onetag_engine(client, message, "gntag", GN_TEXTS)

@Client.on_message(filters.command("shtag", prefixes=".") & filters.me)
async def shtag_cmd(client: Client, message: Message):
    await onetag_engine(client, message, "shtag", SH_TEXTS)

@Client.on_message(filters.command("vctag", prefixes=".") & filters.me)
async def vctag_cmd(client: Client, message: Message):
    await onetag_engine(client, message, "vctag", VC_TEXTS)

@Client.on_message(filters.command(["randomtag", "emojitag"], prefixes=".") & filters.me)
async def randomtag_cmd(client: Client, message: Message):
    await onetag_engine(client, message, "emojitag", EMOJIS)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. STOP TAGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["tagstop", "canceltag", "rstop", "gnstop", "gmtop", "vcstop"], prefixes=".") & filters.me)
async def stop_tags_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in ACTIVE_TAGS:
        task = ACTIVE_TAGS.pop(chat_id, None)
        worker_globals.ACTIVE_TAGS.pop(chat_id, None)
        await message.edit_text(f"🛑 <b>{task} stopped successfully!</b>")
    else:
        await message.edit_text("ℹ️ No active tagging is running in this chat.")
