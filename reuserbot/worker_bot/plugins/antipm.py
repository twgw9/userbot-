"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/antipm.py — PM Guard v2 (Anti-Spam Security)     ║
║  Features:                                               ║
║    • .pmguard on/off (Toggle private chat security)       ║
║    • .a / .allow (Approve user to message in PM)         ║
║    • .da / .deny (Block user & remove approval)          ║
║    • .setpmmsg, .setblockmsg, .setlimit                  ║
║    • .pmlist (View currently approved user IDs)          ║
║    • Zero-Crash Exception Handling & Auto Whitelist      ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import json
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError

logger = logging.getLogger(__name__)

PMGUARD_FILE = "pmguard_data.json"

def load_pm_data() -> dict:
    default_data = {
        "enabled": False,
        "pm_message": "🛡️ <b>MUserBot PM Security</b>\n\nHello! My master is currently busy. Please state your query clearly and wait for master to approve.",
        "block_message": "🚫 <b>Blocked!</b>\nYou have exceeded the allowed warning limit and were automatically blocked.",
        "warn_limit": 3,
        "warned_users": {},
        "allowed_users": []
    }
    if os.path.exists(PMGUARD_FILE):
        try:
            with open(PMGUARD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                default_data.update(data)
                return default_data
        except Exception:
            return default_data
    return default_data

def save_pm_data(data: dict):
    try:
        with open(PMGUARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving PM guard data: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. TURN PMGUARD ON/OFF (.pmguard on/off)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("pmguard", prefixes=".") & filters.me)
async def pmguard_toggle(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1] not in ["on", "off"]:
        return await message.edit_text("❌ <b>Usage:</b> <code>.pmguard on</code> or <code>.pmguard off</code>")
        
    data = load_pm_data()
    data["enabled"] = (message.command[1] == "on")
    save_pm_data(data)
    
    status = "ON 🟢 (Active)" if data["enabled"] else "OFF 🔴 (Disabled)"
    await message.edit_text(f"🛡️ <b>PM Guard Protection:</b> {status}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. SET CUSTOM PM MESSAGE (.setpmmsg <text>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("setpmmsg", prefixes=".") & filters.me)
async def set_pm_msg(client: Client, message: Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.setpmmsg <your custom warning text></code>")
        
    data = load_pm_data()
    data["pm_message"] = parts[1].strip()
    save_pm_data(data)
    await message.edit_text("✅ <b>PM Guard Warning Message Updated!</b>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. SET BLOCK MESSAGE (.setblockmsg <text>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("setblockmsg", prefixes=".") & filters.me)
async def set_block_msg(client: Client, message: Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.setblockmsg <your custom block text></code>")
        
    data = load_pm_data()
    data["block_message"] = parts[1].strip()
    save_pm_data(data)
    await message.edit_text("✅ <b>PM Block Message Updated!</b>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. SET WARNING LIMIT (.setlimit <number>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("setlimit", prefixes=".") & filters.me)
async def set_limit(client: Client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.edit_text("❌ <b>Usage:</b> <code>.setlimit <1-10></code>")
        
    limit = max(1, min(10, int(message.command[1])))
    data = load_pm_data()
    data["warn_limit"] = limit
    save_pm_data(data)
    await message.edit_text(f"✅ <b>PM Warn Limit Set To:</b> <code>{limit}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. ALLOW & DENY COMMANDS (.a, .allow, .da, .deny)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def resolve_target_user_id(client: Client, message: Message):
    if message.chat.type.value == "private":
        return message.chat.id
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    parts = message.text.split()
    if len(parts) >= 2:
        try:
            user = await client.get_users(parts[1])
            return user.id
        except Exception:
            return None
    return None

@Client.on_message(filters.command(["allow", "a", "approve"], prefixes=".") & filters.me)
async def allow_user(client: Client, message: Message):
    user_id = await resolve_target_user_id(client, message)
    if not user_id:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
        
    data = load_pm_data()
    if user_id not in data["allowed_users"]:
        data["allowed_users"].append(user_id)
    if str(user_id) in data["warned_users"]:
        del data["warned_users"][str(user_id)]
    save_pm_data(data)
    
    await message.edit_text(f"✅ <b>User Approved!</b>\n<code>User ID: {user_id}</code> is now allowed to message.")

@Client.on_message(filters.command(["deny", "da", "disapprove"], prefixes=".") & filters.me)
async def deny_user(client: Client, message: Message):
    user_id = await resolve_target_user_id(client, message)
    if not user_id:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
        
    data = load_pm_data()
    if user_id in data["allowed_users"]:
        data["allowed_users"].remove(user_id)
    save_pm_data(data)
    
    try:
        await client.block_user(user_id)
        await message.edit_text(f"🚫 <b>User Denied & Blocked!</b>\n<code>User ID: {user_id}</code>")
    except Exception as e:
        await message.edit_text(f"⚠️ User removed from whitelist. Block error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. LIST APPROVED USERS (.pmlist)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("pmlist", prefixes=".") & filters.me)
async def list_pm_users(client: Client, message: Message):
    data = load_pm_data()
    allowed = data.get("allowed_users", [])
    if not allowed:
        return await message.edit_text("ℹ️ No users are currently in the PM whitelist.")
        
    text = f"📋 <b>PM Guard Whitelisted Users ({len(allowed)}):</b>\n\n"
    for uid in allowed[:30]:
        text += f"• <code>{uid}</code>\n"
    await message.edit_text(text)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. BACKGROUND PM WATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.private & ~filters.me & ~filters.bot & ~filters.service, group=1)
async def pm_watcher(client: Client, message: Message):
    data = load_pm_data()
    
    # If PM guard is turned off or user is whitelisted, ignore
    if not data.get("enabled"):
        return
        
    user_id = message.from_user.id if message.from_user else message.chat.id
    if user_id in data.get("allowed_users", []):
        return
        
    warned_users = data.setdefault("warned_users", {})
    limit = data.get("warn_limit", 3)
    
    # Increment counter
    current_count = warned_users.get(str(user_id), 0) + 1
    warned_users[str(user_id)] = current_count
    save_pm_data(data)
    
    # If warn threshold exceeded, block target
    if current_count >= limit:
        try:
            await message.reply_text(data.get("block_message", "You have been blocked."))
        except Exception:
            pass
            
        try:
            await client.block_user(user_id)
        except Exception as e:
            logger.warning(f"Error blocking PM spammer {user_id}: {e}")
            
        if str(user_id) in warned_users:
            del warned_users[str(user_id)]
            save_pm_data(data)
    else:
        # Send warning counter
        warning_badge = f"{data.get('pm_message', '')}\n\n⚠️ <b>Warning [{current_count}/{limit}]</b>\n<i>Please do not spam or send consecutive messages.</i>"
        try:
            await message.reply_text(warning_badge)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_text(warning_badge)
            except Exception:
                pass
        except Exception:
            pass
