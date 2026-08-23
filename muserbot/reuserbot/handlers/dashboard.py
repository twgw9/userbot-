"""
╔═══════════════════════════════════════════════════════════╗
║  handlers/dashboard.py — Advanced SSH Cluster Control     ║
║  Features:                                               ║
║    • Beautiful High-Tech Dashboard UI                    ║
║    • Parallel Server Health Pinging                      ║
║    • Decrypted Userbot Process Killer                    ║
║    • Dynamic Cluster Node Management                     ║
╚══════════════════════════════════━━━━━━━━━━━━━━━━━━━━━━━━╝
"""

import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import database
import ssh_manager
from config import ADMIN_IDS, SPECIAL_ADMIN_ID
from encryption import decrypt_data

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id == SPECIAL_ADMIN_ID

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. MAIN DASHBOARD VIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("dashboard"))
@router.callback_query(F.data == "admin_ssh_dashboard")
async def ssh_dashboard(event):
    user_id = event.from_user.id
    if not is_admin(user_id):
        if isinstance(event, CallbackQuery):
            return await event.answer("❌ Not Authorized!", show_alert=True)
        return
        
    servers = await database.get_ssh_servers()
    
    if not servers:
        text = (
            "🖥 <b>SSH Cluster Dashboard</b>\n\n"
            "⚠️ No servers configured yet.\n"
            "Use /addssh to add your first Alwaysdata or VPS node."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add SSH Server", callback_data="admin_panel")],
            [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_panel")]
        ])
    else:
        total_bots = sum(s['active_userbots'] for s in servers)
        online_count = sum(1 for s in servers if s['is_online'])
        text = (
            "🖥 <b>SSH Cluster Dashboard</b>\n\n"
            f"⚡ <b>Total Nodes:</b> <code>{len(servers)}</code> | <b>Online:</b> <code>{online_count}</code>\n"
            f"🤖 <b>Running Userbots:</b> <code>{total_bots}</code>\n\n"
            "Select a cluster server below to manage:"
        )
        kb = []
        for srv in servers:
            status_icon = "🟢" if srv['is_online'] else "🔴"
            btn_text = f"{status_icon} Node #{srv['id']} ({srv['host']}) [{srv['active_userbots']}/{srv['max_userbots']}]"
            kb.append([InlineKeyboardButton(text=btn_text, callback_data=f"ssh_view_{srv['id']}")])
            
        kb.append([
            InlineKeyboardButton(text="🔄 Ping All Nodes", callback_data="ssh_refresh_all"),
            InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_panel")
        ])
    
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        except TelegramBadRequest:
            await event.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        await event.answer()
    else:
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. VIEW SPECIFIC SERVER (Manage Node)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data.startswith("ssh_view_"))
async def ssh_view_server(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Not Authorized!", show_alert=True)
        
    server_id = int(callback.data.split("_")[2])
    server = await database.get_ssh_server(server_id)
    
    if not server:
        await callback.answer("Server node not found!", show_alert=True)
        await ssh_dashboard(callback)
        return
        
    status_icon = "🟢 Online" if server['is_online'] else "🔴 Offline"
    text = (
        f"🖥 <b>SSH Node Details — Server #{server['id']}</b>\n\n"
        f"🌐 <b>Host:</b> <code>{server['host']}</code>\n"
        f"👤 <b>Username:</b> <code>{server['username']}</code>\n"
        f"🔌 <b>Port:</b> <code>{server['port']}</code>\n"
        f"⚡ <b>Status:</b> {status_icon}\n\n"
        f"🤖 <b>Hosted Userbots:</b> <code>{server['active_userbots']} / {server['max_userbots']}</code>"
    )
    
    kb = [
        [
            InlineKeyboardButton(text="🔄 Ping Node", callback_data=f"ssh_refresh_{server['id']}"),
            InlineKeyboardButton(text="🛑 Kill All Bots", callback_data=f"ssh_kill_all_{server['id']}")
        ],
        [
            InlineKeyboardButton(text="❌ Delete Server Node", callback_data=f"ssh_delete_{server['id']}")
        ],
        [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="admin_ssh_dashboard")]
    ]
    
    try:
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. REFRESH SERVER STATUS (Single & All)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data.startswith("ssh_refresh_"))
async def ssh_refresh_server(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Not Authorized!", show_alert=True)
        
    if callback.data == "ssh_refresh_all":
        await callback.answer("Pinging all cluster nodes...")
        await ssh_manager.check_all_servers_status()
        await ssh_dashboard(callback)
        return
        
    server_id = int(callback.data.split("_")[2])
    await callback.answer("Pinging node...")
    
    is_online = await ssh_manager.ping_ssh_server(server_id)
    status = "Online 🟢" if is_online else "Offline 🔴"
    await callback.answer(f"Server #{server_id} is {status}", show_alert=True)
    
    callback.data = f"ssh_view_{server_id}"
    await ssh_view_server(callback)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. KILL ALL USERBOTS ON SERVER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data.startswith("ssh_kill_all_"))
async def ssh_kill_all_bots(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Not Authorized!", show_alert=True)
        
    server_id = int(callback.data.split("_")[3])
    server = await database.get_ssh_server(server_id)
    
    if not server:
        return await callback.answer("Server node not found!", show_alert=True)
        
    await callback.answer("Stopping active userbots on this server...", show_alert=False)
    
    users = await database.get_all_users()
    killed_count = 0
    
    for user in users:
        if user.get('ssh_server_id') == server_id and user.get('is_logged_in'):
            real_phone = decrypt_data(user['phone']) if user.get('phone') else ""
            if real_phone:
                success, _ = await ssh_manager.kill_userbot(server_id, real_phone, user['user_id'])
                if success:
                    killed_count += 1
                    
    db = await database.get_db()
    await db.execute("UPDATE ssh_servers SET active_userbots = 0 WHERE id = ?", (server_id,))
    await db.commit()
    
    await callback.answer(f"✅ Stopped {killed_count} userbot instances on this node.", show_alert=True)
    
    callback.data = f"ssh_view_{server_id}"
    await ssh_view_server(callback)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. DELETE SSH SERVER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data.startswith("ssh_delete_"))
async def ssh_delete_server(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Not Authorized!", show_alert=True)
        
    server_id = int(callback.data.split("_")[2])
    await database.delete_ssh_server(server_id)
    await callback.answer("🗑️ Cluster node removed successfully!", show_alert=True)
    await ssh_dashboard(callback)
