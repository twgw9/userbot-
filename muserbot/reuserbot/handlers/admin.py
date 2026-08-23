"""
╔═══════════════════════════════════════════════════════════╗
║  handlers/admin.py — Admin Panel & Configuration          ║
║  Features:                                               ║
║    • SSH Add/Delete/Monitor                              ║
║    • Safe Broadcast System with progress                 ║
║    • Set Welcome Text/Photo, Donate QR, Support Link     ║
║    • Dynamic Force Subscribe Channel Management          ║
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
from config import ADMIN_IDS, SPECIAL_ADMIN_ID
from language import get_text
from states import AddSSHStates, FsubStates, SettingStates
from keyboards.menus import admin_panel_keyboard

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id == SPECIAL_ADMIN_ID

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. ADMIN PANEL OPENER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("admin"))
@router.callback_query(F.data == "admin_panel")
async def open_admin_panel(event):
    user_id = event.from_user.id
    if not is_admin(user_id):
        if isinstance(event, CallbackQuery):
            return await event.answer("❌ Not Authorized!", show_alert=True)
        else:
            return await event.reply("❌ You are not authorized to use the Admin Panel.")
    
    text = (
        "🛡️ <b>MUserBot Pro — Admin Control Panel</b>\n\n"
        "Welcome Admin! Select an action from the options below:"
    )
    kb = admin_panel_keyboard()
    
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb)
        except TelegramBadRequest:
            await event.message.answer(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)

@router.callback_query(F.data == "admin_close")
async def close_admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Not Authorized!")
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Admin Panel Closed")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. SSH SERVER MANAGEMENT (ADD - FSM)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("addssh"))
async def cmd_add_ssh(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🖥 <b>Add New SSH Server</b>\n\nPlease send the SSH Host (e.g., <code>ssh-username.alwaysdata.net</code> or <code>192.168.1.1</code>):")
    await state.set_state(AddSSHStates.waiting_for_host)

@router.message(AddSSHStates.waiting_for_host)
async def ssh_get_host(message: Message, state: FSMContext):
    host = message.text.strip()
    await state.update_data(host=host)
    await message.answer("👤 Now send the SSH <b>Username</b>:")
    await state.set_state(AddSSHStates.waiting_for_username)

@router.message(AddSSHStates.waiting_for_username)
async def ssh_get_user(message: Message, state: FSMContext):
    username = message.text.strip()
    await state.update_data(username=username)
    await message.answer("🔑 Now send the SSH <b>Password</b>:")
    await state.set_state(AddSSHStates.waiting_for_password)

@router.message(AddSSHStates.waiting_for_password)
async def ssh_get_pass(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    host = data['host']
    username = data['username']
    
    # Delete password message for safety
    try:
        await message.delete()
    except Exception:
        pass
        
    status_msg = await message.answer("⏳ <b>Verifying SSH Connection...</b>\nPlease wait a few seconds.")
    
    success, msg = await ssh_manager.verify_and_add_ssh(
        host=host, 
        username=username, 
        password=password, 
        port=22, 
        admin_id=message.from_user.id
    )
    
    if not success:
        await status_msg.edit_text(f"❌ <b>Verification Failed!</b>\n\nError: <code>{msg}</code>\n\nServer was not saved. Try again with /addssh.")
        await state.clear()
        return
    
    await status_msg.edit_text(f"✅ <b>Server Added Successfully!</b>\n\nHost: <code>{host}</code>\n{msg}\n\nIt is now ready for auto-deploying userbots.")
    await state.clear()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. BROADCAST SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("broadcast"))
@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(event, state: FSMContext):
    user_id = event.from_user.id
    if not is_admin(user_id):
        if isinstance(event, CallbackQuery):
            return await event.answer("❌ Not Authorized!", show_alert=True)
        return
        
    msg_text = "📢 <b>Broadcast Announcement System</b>\n\nPlease send or forward the message/photo you want to broadcast to all registered bot users."
    if isinstance(event, CallbackQuery):
        await event.message.answer(msg_text)
        await event.answer()
    else:
        await event.answer(msg_text)
        
    await state.set_state(SettingStates.waiting_for_broadcast_msg)

@router.message(SettingStates.waiting_for_broadcast_msg)
async def send_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
        
    status_msg = await message.answer("⏳ Starting broadcast to all users...")
    user_ids = await database.get_all_user_ids()
    success = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            await message.copy_to(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.04) # Throttled to prevent Telegram flood limits
        except Exception:
            failed += 1
            
    await status_msg.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"📤 <b>Delivered:</b> {success}\n"
        f"❌ <b>Failed / Blocked:</b> {failed}\n"
        f"👥 <b>Total Targets:</b> {len(user_ids)}"
    )
    await state.clear()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. SETTINGS COMMANDS (Welcome, QR, Owner, Support, Fsub)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("setwelcome"))
async def set_welcome(message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message:
        return await message.answer("❌ Please reply to a message with /setwelcome to set it as Welcome Text.")
    await database.set_setting("welcome_text", message.reply_to_message.html_text or message.reply_to_message.text)
    await message.reply("✅ Welcome Text updated successfully!")

@router.message(Command("setwelcomephoto"))
async def set_welcome_photo(message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.answer("❌ Please reply to a photo with /setwelcomephoto to set it.")
    file_id = message.reply_to_message.photo[-1].file_id
    await database.set_setting("welcome_photo", file_id)
    await message.reply("✅ Welcome Photo updated successfully!")

@router.message(Command("setdqr"))
async def set_donate_qr(message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.answer("❌ Please reply to a QR Code photo with /setdqr to set it.")
    file_id = message.reply_to_message.photo[-1].file_id
    await database.set_setting("donate_qr", file_id)
    await message.reply("✅ Donate QR Code updated successfully!")

@router.message(Command("setdonatetext"))
async def set_donate_text(message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message:
        return await message.answer("❌ Please reply to a message with /setdonatetext to set it.")
    await database.set_setting("donate_text", message.reply_to_message.html_text or message.reply_to_message.text)
    await message.reply("✅ Donate Text updated successfully!")

@router.message(Command("setowner"))
async def set_owner(message: Message):
    if not is_admin(message.from_user.id): return
    if len(message.command) < 2:
        return await message.answer("Usage: <code>/setowner @username</code>")
    username = message.command[1]
    await database.set_setting("owner_username", username)
    await message.answer(f"✅ Owner username set to: {username}")

@router.message(Command("setsupport"))
async def set_support(message: Message):
    if not is_admin(message.from_user.id): return
    if len(message.command) < 2:
        return await message.answer("Usage: <code>/setsupport https://t.me/yourgrouplink</code>")
    link = message.command[1]
    await database.set_setting("support_link", link)
    await message.answer(f"✅ Support link set to: {link}")

# Force Subscribe Channels
@router.message(Command("fjoinchannel"))
async def add_fsub_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    if len(message.command) >= 2:
        link = message.command[1].strip()
        await database.add_fsub_channel(link)
        return await message.answer(f"✅ Force Sub Channel added successfully!\nLink: {link}")
        
    await message.answer("📢 Please send the channel link (e.g., https://t.me/mychannel) to add for Force Subscribe.\n\nMake sure the Bot is Administrator in that channel!")
    await state.set_state(FsubStates.waiting_for_channel_link)

@router.message(FsubStates.waiting_for_channel_link)
async def save_fsub_channel(message: Message, state: FSMContext):
    link = message.text.strip()
    if "t.me/" not in link and not link.startswith("@"):
        await message.answer("❌ Invalid link. Please send a valid Telegram link (e.g., https://t.me/channel).")
        return
        
    await database.add_fsub_channel(link)
    await message.answer(f"✅ Force Sub Channel added successfully!\nLink: {link}")
    await state.clear()

@router.message(Command("listfsub"))
async def list_fsub_channels(message: Message):
    if not is_admin(message.from_user.id): return
    channels = await database.get_fsub_channels()
    if not channels:
        return await message.answer("ℹ️ No Force Subscribe channels are currently configured.")
    text = "📢 <b>Configured FSub Channels:</b>\n\n"
    for c in channels:
        text += f"• <b>ID:</b> <code>{c['id']}</code> | {c['channel_link']}\n"
    await message.answer(text)

@router.message(Command("delfsub"))
async def del_fsub_channel(message: Message):
    if not is_admin(message.from_user.id): return
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.answer("Usage: <code>/delfsub &lt;channel_id&gt;</code>\nUse /listfsub to see channel IDs.")
    cid = int(message.command[1])
    await database.remove_fsub_channel(cid)
    await message.answer(f"🗑️ FSub channel ID <code>{cid}</code> removed successfully.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. STATS COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("stats"))
@router.callback_query(F.data == "admin_stats")
@router.callback_query(F.data == "sp_stats")
async def show_stats(event):
    user_id = event.from_user.id
    if not is_admin(user_id):
        if isinstance(event, CallbackQuery):
            return await event.answer("❌ Not Authorized!", show_alert=True)
        return
        
    stats = await database.get_stats()
    text = (
        "📊 <b>MUserBot Pro — System Statistics</b>\n\n"
        f"👥 <b>Total Users:</b> <code>{stats['total_users']}</code>\n"
        f"🟢 <b>Logged In Users:</b> <code>{stats['logged_in_users']}</code>\n"
        f"⚡ <b>Active (Last 24h):</b> <code>{stats['active_24h']}</code>\n\n"
        f"🖥 <b>SSH Cluster Servers:</b> <code>{stats['total_ssh_servers']}</code> ({stats['online_ssh_servers']} Online)\n"
        f"🤖 <b>Active Running Userbots:</b> <code>{stats['active_userbots']}</code>\n"
        f"📢 <b>Fsub Channels:</b> <code>{stats['fsub_channels']}</code>\n\n"
        f"🟢 <b>Core Status:</b> Operational & High Speed"
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(text)
        await event.answer()
    else:
        await event.answer(text)
