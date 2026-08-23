"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/admin.py — Group Administration & Moderation     ║
║  Features:                                               ║
║    • .ban, .unban, .kick, .mute, .unmute                 ║
║    • .promote, .fullpromote, .demote                     ║
║    • .pin, .unpin, .del, .purge, .purgeme                ║
║    • .lock, .unlock, .antiraid                           ║
║    • .zombies (Clean deleted accounts)                   ║
║    • .setgtitle, .setgpic                                ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import (
    FloodWait, 
    UserAdminInvalid, 
    ChatAdminRequired, 
    RPCError,
    PeerIdInvalid
)

logger = logging.getLogger(__name__)

ANTI_RAID_CHATS = {}

async def get_target_user(client: Client, message: Message):
    """Extract target user from reply or arguments"""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = message.text.split()
    if len(parts) >= 2:
        try:
            return await client.get_users(parts[1])
        except Exception:
            return None
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. BAN / UNBAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("ban", prefixes=".") & filters.me)
async def ban_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.edit_text(f"🚫 <b>Banned:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> (<code>{user.id}</code>)")
    except UserAdminInvalid:
        await message.edit_text("❌ Cannot ban an administrator.")
    except ChatAdminRequired:
        await message.edit_text("❌ I require ban administrator permissions in this chat.")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("unban", prefixes=".") & filters.me)
async def unban_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    try:
        await client.unban_chat_member(message.chat.id, user.id)
        await message.edit_text(f"✅ <b>Unbanned:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. KICK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("kick", prefixes=".") & filters.me)
async def kick_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await asyncio.sleep(0.5)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.edit_text(f"👢 <b>Kicked:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>")
    except UserAdminInvalid:
        await message.edit_text("❌ Cannot kick an administrator.")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. MUTE / UNMUTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("mute", prefixes=".") & filters.me)
async def mute_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    try:
        permissions = ChatPermissions(can_send_messages=False)
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        await message.edit_text(f"🔇 <b>Muted:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("unmute", prefixes=".") & filters.me)
async def unmute_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    try:
        permissions = ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True
        )
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        await message.edit_text(f"🔊 <b>Unmuted:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. PROMOTE / DEMOTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["promote", "fullpromote"], prefixes=".") & filters.me)
async def promote_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    is_full = message.command[0] == "fullpromote"
    
    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            can_change_info=is_full,
            can_post_messages=is_full,
            can_edit_messages=is_full,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=is_full
        )
        title = "Full Administrator 👑" if is_full else "Administrator 🛡️"
        await message.edit_text(f"⬆️ <b>Promoted:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> as {title}")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("demote", prefixes=".") & filters.me)
async def demote_cmd(client: Client, message: Message):
    user = await get_target_user(client, message)
    if not user:
        return await message.edit_text("❌ Reply to a user or provide username/ID.")
    
    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            can_change_info=False, can_post_messages=False, can_edit_messages=False,
            can_delete_messages=False, can_restrict_members=False, can_invite_users=False,
            can_pin_messages=False, can_manage_video_chats=False
        )
        await message.edit_text(f"⬇️ <b>Demoted:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> to regular member.")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. PIN / UNPIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("pin", prefixes=".") & filters.me)
async def pin_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("❌ Reply to a message to pin it.")
    try:
        await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.edit_text("📌 <b>Message Pinned Successfully!</b>")
    except Exception as e:
        await message.edit_text(f"❌ Pin Error: <code>{e}</code>")

@Client.on_message(filters.command("unpin", prefixes=".") & filters.me)
async def unpin_cmd(client: Client, message: Message):
    try:
        msg_id = message.reply_to_message.id if message.reply_to_message else None
        await client.unpin_chat_message(message.chat.id, msg_id)
        await message.edit_text("📍 <b>Message Unpinned!</b>")
    except Exception as e:
        await message.edit_text(f"❌ Unpin Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. DEL / PURGE / PURGEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("del", prefixes=".") & filters.me)
async def del_cmd(client: Client, message: Message):
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception:
            pass

@Client.on_message(filters.command("purge", prefixes=".") & filters.me)
async def purge_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("❌ Reply to a message to begin purging from that point.")
        
    start_id = message.reply_to_message.id
    chat_id = message.chat.id
    await message.delete()
    
    message_ids = []
    try:
        async for msg in client.get_chat_history(chat_id):
            if msg.id < start_id:
                break
            message_ids.append(msg.id)
            if len(message_ids) >= 100:
                await client.delete_messages(chat_id, message_ids)
                message_ids.clear()
                await asyncio.sleep(0.3)
                
        if message_ids:
            await client.delete_messages(chat_id, message_ids)
            
        status = await client.send_message(chat_id, "🧹 <b>Purge Completed Successfully!</b>")
        await asyncio.sleep(3)
        await status.delete()
    except Exception as e:
        logger.error(f"Purge Error: {e}")

@Client.on_message(filters.command("purgeme", prefixes=".") & filters.me)
async def purgeme_cmd(client: Client, message: Message):
    count = 10
    if len(message.command) >= 2 and message.command[1].isdigit():
        count = int(message.command[1])
        
    chat_id = message.chat.id
    my_id = (await client.get_me()).id
    message_ids = []
    
    try:
        async for msg in client.get_chat_history(chat_id, limit=count * 3):
            if msg.from_user and msg.from_user.id == my_id:
                message_ids.append(msg.id)
                if len(message_ids) >= count:
                    break
                    
        if message_ids:
            await client.delete_messages(chat_id, message_ids)
            status = await client.send_message(chat_id, f"🧹 Deleted <code>{len(message_ids)}</code> of your messages.")
            await asyncio.sleep(3)
            await status.delete()
    except Exception as e:
        logger.error(f"Purgeme Error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. ZOMBIES CLEANER (.zombies)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("zombies", prefixes=".") & filters.me)
async def clean_zombies(client: Client, message: Message):
    chat_id = message.chat.id
    await message.edit_text("🧟 <code>Scanning for deleted accounts...</code>")
    
    deleted_count = 0
    kicked_count = 0
    
    try:
        async for member in client.get_chat_members(chat_id):
            if member.user.is_deleted:
                deleted_count += 1
                try:
                    await client.ban_chat_member(chat_id, member.user.id)
                    await client.unban_chat_member(chat_id, member.user.id)
                    kicked_count += 1
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
                    
        await message.edit_text(
            f"🧟 <b>Cleaned Zombies:</b>\n\n"
            f"• <b>Found:</b> <code>{deleted_count}</code> deleted accounts\n"
            f"• <b>Removed:</b> <code>{kicked_count}</code> successfully"
        )
    except Exception as e:
        await message.edit_text(f"❌ Zombies Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. GROUP TITLE & PIC (.setgtitle, .setgpic)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("setgtitle", prefixes=".") & filters.me)
async def set_group_title(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ Provide title: <code>.setgtitle <new_title></code>")
    title = message.text.split(" ", 1)[1]
    try:
        await client.set_chat_title(message.chat.id, title)
        await message.edit_text(f"✅ Group title updated to: <b>{title}</b>")
    except Exception as e:
        await message.edit_text(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("setgpic", prefixes=".") & filters.me)
async def set_group_photo(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.edit_text("❌ Reply to a photo to set group avatar.")
    msg = await message.edit_text("⏳ <code>Updating group avatar...</code>")
    try:
        photo = await client.download_media(message.reply_to_message.photo.file_id)
        await client.set_chat_photo(message.chat.id, photo=photo)
        await msg.edit_text("✅ <b>Group photo updated successfully!</b>")
    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{e}</code>")
