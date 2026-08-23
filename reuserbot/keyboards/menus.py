"""
╔═══════════════════════════════════════════════════════════╗
║  keyboards/menus.py — Ultra-Modern Inline Keyboards (UI)  ║
║  Main Menu, Userbot Control, Admin Panel, OTP Pad         ║
╚═══════════════════════════════════════════════════════════╝
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from language import get_text

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. LANGUAGE SELECTION KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"),
            InlineKeyboardButton(text="🇮🇳 Hinglish", callback_data="set_lang_hinglish")
        ]
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. FORCE SUB KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def fsub_kb(channels: list) -> InlineKeyboardMarkup:
    kb = []
    for ch in channels:
        name = ch.get('channel_name') or ch.get('name') or "📢 Join Official Channel"
        link = ch.get('channel_link') or ch.get('link') or "https://t.me"
        kb.append([InlineKeyboardButton(text=name, url=link)])
    
    kb.append([InlineKeyboardButton(text="✅ I Joined / Proceed", callback_data="check_fsub")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. MAIN MENU KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_menu_kb(lang: str, is_admin: bool = False, is_logged_in: bool = False) -> InlineKeyboardMarkup:
    """Main Menu layout with interactive userbot controls"""
    host_btn_text = "📱 Manage My Userbot" if is_logged_in else get_text(lang, "btn_host")
    host_callback = "my_userbot_status" if is_logged_in else "host_start"
    
    kb = [
        [InlineKeyboardButton(text=host_btn_text, callback_data=host_callback)],
        [
            InlineKeyboardButton(text=get_text(lang, "btn_about"), callback_data="menu_about"),
            InlineKeyboardButton(text=get_text(lang, "btn_owner"), callback_data="menu_owner")
        ],
        [
            InlineKeyboardButton(text=get_text(lang, "btn_guide"), callback_data="menu_guide"),
            InlineKeyboardButton(text=get_text(lang, "btn_support"), callback_data="menu_support")
        ],
        [
            InlineKeyboardButton(text=get_text(lang, "btn_help"), callback_data="menu_help"),
            InlineKeyboardButton(text=get_text(lang, "btn_donate"), callback_data="menu_donate")
        ]
    ]
    
    if is_admin:
        kb.append([
            InlineKeyboardButton(text="🛡️ Admin Panel", callback_data="admin_panel"),
            InlineKeyboardButton(text="🖥️ SSH Dashboard", callback_data="admin_ssh_dashboard")
        ])
        
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. USERBOT PERSONAL CONTROL KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def userbot_control_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Restart Userbot", callback_data="userbot_restart"),
            InlineKeyboardButton(text="⚡ Test Ping", callback_data="userbot_ping_test")
        ],
        [
            InlineKeyboardButton(text="🛑 Logout / Disconnect", callback_data="userbot_logout")
        ],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu_main")]
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. BACK BUTTON KEYBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def back_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu_main")]
    ])

def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    return back_kb(lang)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. ADMIN PANEL KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🖥 SSH Dashboard", callback_data="admin_ssh_dashboard"),
            InlineKeyboardButton(text="📊 Bot Stats", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="👥 Logged Users", callback_data="sp_view_users")
        ],
        [
            InlineKeyboardButton(text="🔄 Ping All Servers", callback_data="ssh_refresh_all"),
            InlineKeyboardButton(text="❌ Close Panel", callback_data="admin_close")
        ]
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. OTP PAD KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def otp_pad_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="otp_1"), 
            InlineKeyboardButton(text="2", callback_data="otp_2"), 
            InlineKeyboardButton(text="3", callback_data="otp_3")
        ],
        [
            InlineKeyboardButton(text="4", callback_data="otp_4"), 
            InlineKeyboardButton(text="5", callback_data="otp_5"), 
            InlineKeyboardButton(text="6", callback_data="otp_6")
        ],
        [
            InlineKeyboardButton(text="7", callback_data="otp_7"), 
            InlineKeyboardButton(text="8", callback_data="otp_8"), 
            InlineKeyboardButton(text="9", callback_data="otp_9")
        ],
        [
            InlineKeyboardButton(text="⌫ Del", callback_data="otp_del"),
            InlineKeyboardButton(text="0", callback_data="otp_0"), 
            InlineKeyboardButton(text="🔄 Resend", callback_data="otp_resend")
        ],
        [InlineKeyboardButton(text="✅ Submit OTP", callback_data="otp_submit")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_main")]
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. HELP CATEGORIES KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def help_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ Core", callback_data="help_cat_core"),
            InlineKeyboardButton(text="🎬 Animations", callback_data="help_cat_animations"),
            InlineKeyboardButton(text="🤖 AI & Draw", callback_data="help_cat_ai")
        ],
        [
            InlineKeyboardButton(text="🎵 Music Studio", callback_data="help_cat_music"),
            InlineKeyboardButton(text="🛡️ Security", callback_data="help_cat_security"),
            InlineKeyboardButton(text="🎮 Games Arcade", callback_data="help_cat_games")
        ],
        [
            InlineKeyboardButton(text="🛡️ PM Guard", callback_data="help_cat_pm"),
            InlineKeyboardButton(text="🏷️ Tagall", callback_data="help_cat_tagall"),
            InlineKeyboardButton(text="🎭 Profile Vault", callback_data="help_cat_profile")
        ],
        [
            InlineKeyboardButton(text="🔥 Raid & Spam", callback_data="help_cat_raid"),
            InlineKeyboardButton(text="👮 Admin Tools", callback_data="help_cat_admin"),
            InlineKeyboardButton(text="📸 Media & AFK", callback_data="help_cat_media")
        ],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu_main")]
    ])
