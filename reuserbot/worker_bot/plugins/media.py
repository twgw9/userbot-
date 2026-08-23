"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/media.py — View-Once Saver & Media Supertools    ║
║  Features:                                               ║
║    • Automatic Background View-Once Photo/Video Saver     ║
║    • .vo & .viewonce (Manual View-Once Extractor)        ║
║    • .kang & .steal (Sticker stealer)                    ║
║    • .toaudio, .tovoice, .togif (Rapid media converter)  ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import io
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. AUTO VIEW-ONCE SAVER (Background Interceptor)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.private & ~filters.me, group=5)
async def auto_view_once_saver(client: Client, message: Message):
    # Check if incoming message is a view-once / ttl photo or video
    is_view_once = False
    if message.photo and getattr(message.photo, "ttl_seconds", None):
        is_view_once = True
    elif message.video and getattr(message.video, "ttl_seconds", None):
        is_view_once = True
        
    if is_view_once:
        sender_name = message.from_user.first_name if message.from_user else "User"
        sender_id = message.from_user.id if message.from_user else "Unknown"
        caption = (
            f"🕵️‍♂️ <b>Auto-Saved View-Once Media!</b>\n\n"
            f"👤 <b>Sender:</b> {sender_name} (<code>{sender_id}</code>)\n"
            f"🕒 <b>TTL:</b> <code>{getattr(message.photo or message.video, 'ttl_seconds', 'N/A')}s</code>\n"
            f"📝 <b>Caption:</b> <i>{message.caption or 'None'}</i>"
        )
        try:
            downloaded = await client.download_media(message, in_memory=True)
            if message.photo:
                await client.send_photo("me", photo=downloaded, caption=caption)
            elif message.video:
                await client.send_video("me", video=downloaded, caption=caption)
            logger.info(f"Successfully auto-saved View-Once media from {sender_id}")
        except Exception as e:
            logger.error(f"Error auto-saving view-once media: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. MANUAL VIEW-ONCE EXTRACTOR (.vo, .viewonce)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["vo", "viewonce"], prefixes=".") & filters.me)
async def manual_view_once(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("❌ Reply to a view-once media message to save it.")
        
    replied = message.reply_to_message
    if not (replied.photo or replied.video):
        return await message.edit_text("❌ Replied message does not contain photo or video.")
        
    msg = await message.edit_text("⏳ <code>Extracting View-Once media...</code>")
    
    try:
        downloaded = await client.download_media(replied, in_memory=True)
        caption = f"🕵️‍♂️ <b>Saved View-Once Media</b>\n\n<b>From:</b> <code>{replied.from_user.id if replied.from_user else 'Unknown'}</code>"
        
        if replied.photo:
            await client.send_photo("me", photo=downloaded, caption=caption)
            await client.send_photo(message.chat.id, photo=downloaded, caption="✅ <i>View-once extracted!</i>")
        elif replied.video:
            await client.send_video("me", video=downloaded, caption=caption)
            await client.send_video(message.chat.id, video=downloaded, caption="✅ <i>View-once extracted!</i>")
            
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Error extracting view-once: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. STICKER STEALER (.kang, .steal)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["kang", "steal"], prefixes=".") & filters.me)
async def kang_sticker(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("❌ Reply to a photo or sticker to steal it.")
        
    replied = message.reply_to_message
    msg = await message.edit_text("🎨 <code>Kanging sticker...</code>")
    
    try:
        if replied.sticker:
            file_bytes = await client.download_media(replied.sticker.file_id, in_memory=True)
            await client.send_sticker("me", sticker=file_bytes)
            await msg.edit_text("✅ <b>Sticker saved to your Saved Messages!</b>")
        elif replied.photo:
            file_bytes = await client.download_media(replied.photo.file_id, in_memory=True)
            await client.send_photo("me", photo=file_bytes, caption="🎨 <b>Saved Media</b>")
            await msg.edit_text("✅ <b>Photo saved to your Saved Messages!</b>")
        else:
            await msg.edit_text("❌ Unsupported media format to steal.")
    except Exception as e:
        await msg.edit_text(f"❌ Kang Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. CONVERT MEDIA TO VOICE / AUDIO / GIF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["toaudio", "tovoice"], prefixes=".") & filters.me)
async def to_audio_cmd(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.audio or message.reply_to_message.voice):
        return await message.edit_text("❌ Reply to a video or audio to convert to voice.")
        
    msg = await message.edit_text("🎵 <code>Converting to voice note...</code>")
    
    try:
        path = await client.download_media(message.reply_to_message)
        await client.send_voice(message.chat.id, voice=path)
        if os.path.exists(path):
            os.remove(path)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Conversion Error: <code>{e}</code>")

@Client.on_message(filters.command("togif", prefixes=".") & filters.me)
async def to_gif_cmd(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.animation):
        return await message.edit_text("❌ Reply to a video or animation to convert to GIF.")
        
    msg = await message.edit_text("🎞️ <code>Converting to GIF...</code>")
    try:
        path = await client.download_media(message.reply_to_message)
        await client.send_animation(message.chat.id, animation=path)
        if os.path.exists(path):
            os.remove(path)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ GIF Conversion Error: <code>{e}</code>")
