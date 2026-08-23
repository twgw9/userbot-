"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/security.py — Group Security & Anti-Virus System ║
║  Features:                                               ║
║    • .antispam & .anticaps (Flood & CAPS protection)     ║
║    • .antiforward (Prevent channel forwarding)           ║
║    • .blacklist <word> (Forbidden words auto-delete)     ║
║    • .warn, .unwarn, .warns (3-Strike Auto-Ban System)   ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import json
import time
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

logger = logging.getLogger(__name__)

SECURITY_SETTINGS_FILE = "security_settings.json"
USER_WARNS_FILE = "user_warns.json"

# In-memory flood tracker: {chat_id: {user_id: [timestamps]}}
FLOOD_TRACKER = {}

def load_sec_settings() -> dict:
    if os.path.exists(SECURITY_SETTINGS_FILE):
        try:
            with open(SECURITY_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_sec_settings(data: dict):
    try:
        with open(SECURITY_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving security settings: {e}")

def load_warns() -> dict:
    if os.path.exists(USER_WARNS_FILE):
        try:
            with open(USER_WARNS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_warns(data: dict):
    try:
        with open(USER_WARNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving warns: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SECURITY TOGGLES (.antispam, .anticaps, .antiforward)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("antispam", prefixes=".") & filters.me)
async def antispam_toggle(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.antispam on</code> or <code>.antispam off</code>")
    chat_id = str(message.chat.id)
    settings = load_sec_settings()
    chat_cfg = settings.setdefault(chat_id, {})
    chat_cfg["antispam"] = (message.command[1] == "on")
    save_sec_settings(settings)
    status = "ENABLED 🟢" if chat_cfg["antispam"] else "DISABLED 🔴"
    await message.edit_text(f"🛡️ <b>Anti-Spam Flood Protection:</b> {status}")

@Client.on_message(filters.command("anticaps", prefixes=".") & filters.me)
async def anticaps_toggle(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.anticaps on</code> or <code>.anticaps off</code>")
    chat_id = str(message.chat.id)
    settings = load_sec_settings()
    chat_cfg = settings.setdefault(chat_id, {})
    chat_cfg["anticaps"] = (message.command[1] == "on")
    save_sec_settings(settings)
    status = "ENABLED 🟢" if chat_cfg["anticaps"] else "DISABLED 🔴"
    await message.edit_text(f"🔠 <b>Anti-CAPS Yelling Protection:</b> {status}")

@Client.on_message(filters.command("antiforward", prefixes=".") & filters.me)
async def antiforward_toggle(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.antiforward on</code> or <code>.antiforward off</code>")
    chat_id = str(message.chat.id)
    settings = load_sec_settings()
    chat_cfg = settings.setdefault(chat_id, {})
    chat_cfg["antiforward"] = (message.command[1] == "on")
    save_sec_settings(settings)
    status = "ENABLED 🟢" if chat_cfg["antiforward"] else "DISABLED 🔴"
    await message.edit_text(f"🚫 <b>Anti-Forward Channel Protection:</b> {status}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. BLACKLIST WORDS (.blacklist, .unblacklist, .blacklists)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("blacklist", prefixes=".") & filters.me)
async def add_blacklist_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.blacklist <forbidden_word></code>")
    word = message.command[1].lower().strip()
    chat_id = str(message.chat.id)
    settings = load_sec_settings()
    chat_cfg = settings.setdefault(chat_id, {})
    b_words = chat_cfg.setdefault("blacklisted_words", [])
    if word not in b_words:
        b_words.append(word)
        save_sec_settings(settings)
        await message.edit_text(f"🚫 Word <code>'{word}'</code> added to chat blacklist filter!")
    else:
        await message.edit_text(f"⚠️ Word <code>'{word}'</code> is already in blacklist.")

@Client.on_message(filters.command("unblacklist", prefixes=".") & filters.me)
async def remove_blacklist_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.unblacklist <word></code>")
    word = message.command[1].lower().strip()
    chat_id = str(message.chat.id)
    settings = load_sec_settings()
    chat_cfg = settings.setdefault(chat_id, {})
    b_words = chat_cfg.setdefault("blacklisted_words", [])
    if word in b_words:
        b_words.remove(word)
        save_sec_settings(settings)
        await message.edit_text(f"✅ Word <code>'{word}'</code> removed from blacklist.")
    else:
        await message.edit_text(f"❌ Word <code>'{word}'</code> not found in blacklist.")

@Client.on_message(filters.command("blacklists", prefixes=".") & filters.me)
async def list_blacklist_words(client: Client, message: Message):
    chat_id = str(message.chat.id)
    settings = load_sec_settings()
    b_words = settings.get(chat_id, {}).get("blacklisted_words", [])
    if not b_words:
        return await message.edit_text("ℹ️ No blacklisted words configured in this chat.")
    await message.edit_text(f"🚫 <b>Blacklisted Words ({len(b_words)}):</b>\n\n" + ", ".join(f"<code>{w}</code>" for w in b_words))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 3-STRIKE WARN & AUTO-BAN SYSTEM (.warn, .unwarn, .warns)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("warn", prefixes=".") & filters.me)
async def warn_user_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.edit_text("❌ Reply to a user with <code>.warn [reason]</code>")
        
    target = message.reply_to_message.from_user
    chat_id = str(message.chat.id)
    reason = message.text.split(" ", 1)[1] if len(message.command) > 1 else "Violation of chat rules"
    
    warns_db = load_warns()
    chat_warns = warns_db.setdefault(chat_id, {})
    user_warn_count = chat_warns.get(str(target.id), 0) + 1
    chat_warns[str(target.id)] = user_warn_count
    save_warns(warns_db)
    
    if user_warn_count >= 3:
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            del chat_warns[str(target.id)]
            save_warns(warns_db)
            return await message.edit_text(
                f"🚫 <b>3/3 WARNS REACHED! AUTO-BANNED!</b>\n\n"
                f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target.first_name}</a>\n"
                f"📝 <b>Final Reason:</b> <i>{reason}</i>"
            )
        except Exception as e:
            return await message.edit_text(f"⚠️ User reached 3/3 warns but failed to ban: <code>{e}</code>")
            
    await message.edit_text(
        f"⚠️ <b>Warning Issued [{user_warn_count}/3]</b>\n\n"
        f"👤 <b>Target:</b> <a href='tg://user?id={target.id}'>{target.first_name}</a>\n"
        f"📝 <b>Reason:</b> <i>{reason}</i>\n\n"
        f"<i>3 warnings will result in an automatic ban!</i>"
    )

@Client.on_message(filters.command("unwarn", prefixes=".") & filters.me)
async def unwarn_user_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.edit_text("❌ Reply to a user with <code>.unwarn</code>")
    target = message.reply_to_message.from_user
    chat_id = str(message.chat.id)
    warns_db = load_warns()
    chat_warns = warns_db.setdefault(chat_id, {})
    if str(target.id) in chat_warns:
        del chat_warns[str(target.id)]
        save_warns(warns_db)
        await message.edit_text(f"✅ Warnings cleared for <a href='tg://user?id={target.id}'>{target.first_name}</a>.")
    else:
        await message.edit_text(f"ℹ️ <a href='tg://user?id={target.id}'>{target.first_name}</a> has no active warnings.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. BACKGROUND SECURITY WATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.group & ~filters.me, group=6)
async def group_security_watcher(client: Client, message: Message):
    if not message.from_user:
        return
        
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
    settings = load_sec_settings().get(chat_id, {})
    
    # 1. Anti-Forward Check
    if settings.get("antiforward") and message.forward_from_chat:
        try:
            await message.delete()
            return
        except Exception:
            pass
            
    # 2. Anti-Caps Check
    if settings.get("anticaps") and message.text and len(message.text) > 12:
        uppercase_chars = sum(1 for c in message.text if c.isupper())
        if (uppercase_chars / len(message.text)) > 0.75:
            try:
                await message.delete()
                return
            except Exception:
                pass
                
    # 3. Blacklist Filter Check
    b_words = settings.get("blacklisted_words", [])
    if b_words and message.text:
        text_lower = message.text.lower()
        if any(w in text_lower for w in b_words):
            try:
                await message.delete()
                return
            except Exception:
                pass
                
    # 4. Anti-Spam Flood Check (Max 5 msgs in 3 seconds)
    if settings.get("antispam"):
        now = time.time()
        chat_floods = FLOOD_TRACKER.setdefault(chat_id, {})
        user_timestamps = chat_floods.setdefault(user_id, [])
        # Keep timestamps within last 3.5 seconds
        user_timestamps = [t for t in user_timestamps if now - t < 3.5]
        user_timestamps.append(now)
        chat_floods[user_id] = user_timestamps
        
        if len(user_timestamps) >= 5:
            try:
                # Mute for 10 minutes
                until = int(now + 600)
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until
                )
                await client.send_message(
                    message.chat.id,
                    f"🔇 <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> has been auto-muted for 10m (Flood Protection)."
                )
                chat_floods[user_id] = []
            except Exception:
                pass
