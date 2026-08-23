"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/vctools.py — Group Voice Chat Controller         ║
║  Features:                                               ║
║    • .joinvc & .leavevc (Voice chat joiner & leaver)     ║
║    • .vcmembers (List active voice chat listeners)       ║
║    • .vctitle (Set live voice chat title)                ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import GetGroupCall, EditGroupCallTitle

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. VC MEMBERS LIST (.vcmembers)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["vcmembers", "vclist"], prefixes=".") & filters.me)
async def vc_members_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    msg = await message.edit_text("🎙️ <code>Scanning active voice chat...</code>")
    
    try:
        full_chat = await client.invoke(GetFullChannel(channel=await client.resolve_peer(chat_id)))
        call = getattr(full_chat.full_chat, "call", None)
        
        if not call:
            return await msg.edit_text("❌ No active Voice Chat found in this group.")
            
        group_call = await client.invoke(GetGroupCall(call=call, limit=50))
        participants = group_call.participants
        
        text = f"🎙️ <b>Voice Chat Members ({len(participants)}):</b>\n\n"
        for p in participants[:30]:
            p_id = getattr(p.peer, "user_id", None) or getattr(p.peer, "channel_id", "Unknown")
            muted = "🔇 Muted" if p.muted else "🔊 Speaking"
            text += f"• <code>{p_id}</code> | {muted}\n"
            
        await msg.edit_text(text)
    except Exception as e:
        await msg.edit_text(f"❌ VC Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. VC TITLE CHANGER (.vctitle <name>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("vctitle", prefixes=".") & filters.me)
async def vc_title_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.vctitle <new_title></code>")
        
    title = message.text.split(" ", 1)[1]
    chat_id = message.chat.id
    msg = await message.edit_text("🎙️ <code>Updating Voice Chat title...</code>")
    
    try:
        full_chat = await client.invoke(GetFullChannel(channel=await client.resolve_peer(chat_id)))
        call = getattr(full_chat.full_chat, "call", None)
        if not call:
            return await msg.edit_text("❌ No active Voice Chat found in this group.")
            
        await client.invoke(EditGroupCallTitle(call=call, title=title))
        await msg.edit_text(f"✅ <b>Voice Chat title set to:</b> <code>{title}</code>")
    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{e}</code>")
