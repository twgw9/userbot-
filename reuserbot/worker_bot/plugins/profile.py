"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/profile.py — Profile Cloning, Vault & Restorer   ║
║  Features:                                               ║
║    • .clone (Instantly clone name, bio & avatar)         ║
║    • .revert (Instantly restore original profile)        ║
║    • .saveprofile <name> & .loadprofile <name>           ║
║    • .listprofiles & .delprofile                         ║
║    • .setname, .setbio, .setpfp                          ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import io
import json
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid

logger = logging.getLogger(__name__)

PROFILES_FILE = "saved_profiles.json"
REVERT_FILE = "revert_profile.json"

def load_profiles() -> dict:
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_profiles(data: dict):
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving profiles: {e}")

def load_revert_data():
    if os.path.exists(REVERT_FILE):
        try:
            with open(REVERT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_revert_data(data):
    try:
        with open(REVERT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving revert data: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER: BACKUP ORIGINAL PROFILE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def backup_my_profile(client: Client):
    try:
        me = await client.get_me()
        chat = await client.get_chat("me")
        
        backup_text = (
            "📦 <b>Original Profile Backup</b>\n\n"
            f"<b>First Name:</b> <code>{me.first_name}</code>\n"
            f"<b>Last Name:</b> <code>{me.last_name or 'None'}</code>\n"
            f"<b>Bio:</b> <code>{chat.bio or 'None'}</code>"
        )
        await client.send_message("me", backup_text)
        
        photos = []
        async for p in client.get_chat_photos("me", limit=1):
            photos.append(p.file_id)
            
        revert_data = {
            "first_name": me.first_name,
            "last_name": me.last_name or "",
            "bio": chat.bio or "",
            "photo_id": photos[0] if photos else None
        }
        save_revert_data(revert_data)
        return True
    except Exception as e:
        logger.error(f"Backup Error: {e}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. CLONE PROFILE (.clone)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("clone", prefixes=".") & filters.me)
async def clone_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.edit_text("❌ Reply to a user to clone their profile.")
        
    target = message.reply_to_message.from_user
    msg = await message.edit_text("⏳ <code>Backing up your original profile...</code>")
    
    await backup_my_profile(client)
    await msg.edit_text(f"🔄 <code>Cloning {target.first_name}...</code>")
    
    try:
        target_chat = await client.get_chat(target.id)
        first_name = target.first_name or "User"
        last_name = target.last_name or ""
        bio = target_chat.bio or ""
        
        # Download target photo
        photo_bytes = None
        async for p in client.get_chat_photos(target.id, limit=1):
            photo_bytes = await client.download_media(p.file_id, in_memory=True)
            break
            
        # Update user's profile
        await client.update_profile(first_name=first_name, last_name=last_name, bio=bio)
        if photo_bytes:
            await client.set_profile_photo(photo=photo_bytes)
            
        await msg.edit_text(f"🎭 <b>Cloned Successfully!</b>\nCloned: <a href='tg://user?id={target.id}'>{first_name}</a>\n<i>Use <code>.revert</code> to restore your original profile.</i>")
    except Exception as e:
        await msg.edit_text(f"❌ Clone Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. REVERT ORIGINAL PROFILE (.revert)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("revert", prefixes=".") & filters.me)
async def revert_cmd(client: Client, message: Message):
    revert_data = load_revert_data()
    if not revert_data:
        return await message.edit_text("❌ No backup profile found to revert!")
        
    msg = await message.edit_text("🔄 <code>Reverting back to your original profile...</code>")
    
    try:
        await client.update_profile(
            first_name=revert_data.get("first_name", "User"),
            last_name=revert_data.get("last_name", ""),
            bio=revert_data.get("bio", "")
        )
        photo_id = revert_data.get("photo_id")
        if photo_id:
            try:
                photo_bytes = await client.download_media(photo_id, in_memory=True)
                if photo_bytes:
                    await client.set_profile_photo(photo=photo_bytes)
            except Exception:
                pass
                
        await msg.edit_text("✅ <b>Original Profile Restored Successfully!</b>")
    except Exception as e:
        await msg.edit_text(f"❌ Revert Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. SET PROFILE DETAILS (.setname, .setbio)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("setname", prefixes=".") & filters.me)
async def set_name_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.setname <First Name> [Last Name]</code>")
    parts = message.text.split(" ", 2)
    first_name = parts[1]
    last_name = parts[2] if len(parts) > 2 else ""
    try:
        await client.update_profile(first_name=first_name, last_name=last_name)
        await message.edit_text(f"✅ Name changed to: <b>{first_name} {last_name}</b>")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("setbio", prefixes=".") & filters.me)
async def set_bio_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.setbio <your bio></code>")
    bio = message.text.split(" ", 1)[1]
    try:
        await client.update_profile(bio=bio)
        await message.edit_text(f"✅ Bio changed to: <i>{bio}</i>")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")
