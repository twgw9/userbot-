"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/music.py — High-Definition Music & Audio Studio  ║
║  Features:                                               ║
║    • .song & .yt (Instant high-quality MP3 download)     ║
║    • .video & .ytv (Fast MP4 video download)             ║
║    • .lyrics <song> (Live formatted song lyrics)         ║
║    • .findsong / .shazam (Identify music from audio)     ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import aiohttp
import urllib.parse
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. MP3 SONG DOWNLOADER (.song, .yt, .music)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["song", "yt", "music"], prefixes=".") & filters.me)
async def song_download_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.song <song name or youtube url></code>\n<i>Example:</i> <code>.song Believer Imagine Dragons</code>")
        
    query = message.text.split(" ", 1)[1].strip()
    msg = await message.edit_text(f"🔍 <i>Searching song: '<b>{query}</b>'...</i>")
    
    encoded_query = urllib.parse.quote(query)
    
    try:
        async with aiohttp.ClientSession() as session:
            # High-speed reliable audio stream search API
            search_url = f"https://api.safone.dev/song?query={encoded_query}"
            async with session.get(search_url, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    download_url = data.get("download_url") or data.get("link") or data.get("url")
                    title = data.get("title", query)
                    duration = data.get("duration", 0)
                    artist = data.get("artist", "MUserBot Music")
                    thumb = data.get("thumbnail")
                    
                    if download_url:
                        await msg.edit_text("⚡ <i>Uploading audio to Telegram...</i>")
                        
                        await client.send_audio(
                            chat_id=message.chat.id,
                            audio=download_url,
                            title=title,
                            performer=artist,
                            duration=int(duration) if isinstance(duration, (int, float)) else 0,
                            caption=f"🎵 <b>{title}</b>\n👤 <i>{artist}</i>\n⚡ <i>Downloaded via MUserBot Pro</i>"
                        )
                        return await msg.delete()
                        
            # Secondary music API fallback
            async with session.get(f"https://darkness.ashlynn.workers.dev/song?query={encoded_query}", timeout=20) as resp2:
                if resp2.status == 200:
                    data2 = await resp2.json()
                    link = data2.get("link") or data2.get("url")
                    title = data2.get("title", query)
                    if link:
                        await msg.edit_text("⚡ <i>Uploading audio...</i>")
                        await client.send_audio(
                            chat_id=message.chat.id,
                            audio=link,
                            title=title,
                            caption=f"🎵 <b>{title}</b>\n⚡ <i>Downloaded via MUserBot Pro</i>"
                        )
                        return await msg.delete()
                        
        await msg.edit_text(f"❌ Could not download song: '<b>{query}</b>'. Please try a more specific song title or artist name.")
    except Exception as e:
        logger.error(f"Song download error: {e}")
        await msg.edit_text(f"❌ Music Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. VIDEO DOWNLOADER (.video, .ytv)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["video", "ytv"], prefixes=".") & filters.me)
async def video_download_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.video <video title or youtube url></code>")
        
    query = message.text.split(" ", 1)[1].strip()
    msg = await message.edit_text(f"🎬 <i>Searching video: '<b>{query}</b>'...</i>")
    encoded_query = urllib.parse.quote(query)
    
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"https://api.safone.dev/video?query={encoded_query}"
            async with session.get(api_url, timeout=25) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    video_url = data.get("download_url") or data.get("link") or data.get("url")
                    title = data.get("title", query)
                    
                    if video_url:
                        await msg.edit_text("⚡ <i>Uploading video...</i>")
                        await client.send_video(
                            chat_id=message.chat.id,
                            video=video_url,
                            caption=f"🎬 <b>{title}</b>\n⚡ <i>Downloaded via MUserBot Pro</i>"
                        )
                        return await msg.delete()
                        
        await msg.edit_text(f"❌ Video not found for: '<b>{query}</b>'")
    except Exception as e:
        await msg.edit_text(f"❌ Video Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. LIVE SONG LYRICS (.lyrics <name>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("lyrics", prefixes=".") & filters.me)
async def lyrics_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.lyrics <song name></code>")
        
    song_name = message.text.split(" ", 1)[1].strip()
    msg = await message.edit_text(f"📜 <i>Fetching lyrics for: '<b>{song_name}</b>'...</i>")
    encoded = urllib.parse.quote(song_name)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.safone.dev/lyrics?query={encoded}", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    lyrics = data.get("lyrics")
                    title = data.get("title", song_name)
                    artist = data.get("artist", "")
                    
                    if lyrics:
                        formatted = (
                            f"🎶 <b>Lyrics: {title}</b>\n"
                            f"👤 <b>Artist:</b> <i>{artist}</i>\n"
                            "•────────────────────────•\n\n"
                            f"<code>{lyrics[:3500]}</code>"
                        )
                        return await msg.edit_text(formatted)
                        
        await msg.edit_text(f"❌ Lyrics not found for: '<b>{song_name}</b>'")
    except Exception as e:
        await msg.edit_text(f"❌ Lyrics Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. SHAZAM / RECOGNIZE MUSIC (.findsong, .shazam)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["findsong", "shazam", "whatsong"], prefixes=".") & filters.me)
async def shazam_cmd(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.audio or message.reply_to_message.voice or message.reply_to_message.video):
        return await message.edit_text("❌ Reply to an audio, voice note, or video to identify the music.")
        
    msg = await message.edit_text("🎧 <i>Listening & analyzing audio fingerprint...</i>")
    
    try:
        # Download audio chunk
        file_path = await client.download_media(message.reply_to_message)
        
        # Shazam Recognition API Endpoint
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as fp:
                form_data = aiohttp.FormData()
                form_data.add_field('file', fp, filename='audio.mp3')
                
                async with session.post("https://api.safone.dev/shazam", data=form_data, timeout=25) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        title = data.get("title", "Unknown Track")
                        artist = data.get("artist", "Unknown Artist")
                        album = data.get("album", "Single")
                        genres = data.get("genres", "Music")
                        
                        result = (
                            "🎧 <b>Shazam Music Recognition</b>\n\n"
                            f"🎵 <b>Track:</b> <code>{title}</code>\n"
                            f"👤 <b>Artist:</b> <code>{artist}</code>\n"
                            f"💿 <b>Album:</b> <code>{album}</code>\n"
                            f"🏷️ <b>Genre:</b> <code>{genres}</code>\n\n"
                            f"💡 <i>Download with:</i> <code>.song {title} {artist}</code>"
                        )
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        return await msg.edit_text(result)
                        
        if os.path.exists(file_path):
            os.remove(file_path)
        await msg.edit_text("❌ Could not identify this audio track. Ensure the audio is clear.")
    except Exception as e:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        await msg.edit_text(f"❌ Shazam Error: <code>{str(e)}</code>")
