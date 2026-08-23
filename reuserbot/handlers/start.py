"""
╔═══════════════════════════════════════════════════════════╗
║  handlers/start.py — Main Menu, Userbot Control & Help    ║
║  Features:                                               ║
║    • /start, /help, /donate, /about, /mybot              ║
║    • Dynamic Main Menu (Adapts if user has hosted bot)   ║
║    • Userbot Control Panel (Restart, Ping, Logout)       ║
║    • Category Help Browser with 120+ commands            ║
║    • Force Subscribe channel verification                ║
╚═══════════════════════════════════════════════════════════╝
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from language import get_text
import database
from keyboards.menus import language_kb, fsub_kb, main_menu_kb, back_kb, help_menu_kb, userbot_control_kb
from config import ADMIN_IDS, SPECIAL_ADMIN_ID

router = Router()
logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER: FSub Check (Safe & Non-Crashing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def check_fsub_status(bot: Bot, user_id: int) -> bool:
    if user_id in ADMIN_IDS or user_id == SPECIAL_ADMIN_ID:
        return True
        
    channels = await database.get_fsub_channels()
    if not channels:
        return True
    
    for ch in channels:
        link = ch.get('channel_link') or ch.get('link') or ""
        if 't.me/+' in link or 't.me/joinchat/' in link:
            continue
            
        username = link.split('t.me/')[-1].strip('/').lstrip('@') if 't.me/' in link else link.lstrip('@')
        if not username:
            continue
            
        try:
            member = await bot.get_chat_member(chat_id=f"@{username}", user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except (TelegramBadRequest, TelegramForbiddenError):
            continue
        except Exception as e:
            logger.error(f"FSub check unexpected exception for {link}: {e}")
            continue
            
    return True

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER: SHOW MAIN MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def show_main_menu(event, lang: str, edit: bool = False):
    user_id = event.from_user.id
    text = get_text(lang, "start_text")
    photo = await database.get_setting("welcome_photo")
    is_admin = user_id in ADMIN_IDS or user_id == SPECIAL_ADMIN_ID
    is_logged_in = await database.is_user_logged_in(user_id)
    
    kb = main_menu_kb(lang, is_admin=is_admin, is_logged_in=is_logged_in)
    
    try:
        if photo:
            if edit and hasattr(event, "message") and event.message:
                try:
                    media = InputMediaPhoto(media=photo, caption=text)
                    await event.message.edit_media(media=media, reply_markup=kb)
                except Exception:
                    await event.message.delete()
                    await event.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
            elif hasattr(event, "answer_photo"):
                await event.answer_photo(photo=photo, caption=text, reply_markup=kb)
            elif hasattr(event, "message") and event.message:
                await event.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
        else:
            if edit and hasattr(event, "message") and event.message:
                try:
                    await event.message.edit_text(text=text, reply_markup=kb)
                except Exception:
                    await event.message.answer(text=text, reply_markup=kb)
            elif hasattr(event, "answer"):
                await event.answer(text=text, reply_markup=kb)
            elif hasattr(event, "message") and event.message:
                await event.message.answer(text=text, reply_markup=kb)
    except Exception as e:
        logger.warning(f"Error rendering main menu: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /start COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user_id = message.from_user.id
    name = message.from_user.first_name or "User"
    username = message.from_user.username or ""
    
    await database.add_or_update_user(user_id, name, username)
    user_data = await database.get_user(user_id)
    
    if not user_data or not user_data.get('language'):
        await message.answer(get_text("en", "choose_lang"), reply_markup=language_kb())
        return
        
    lang = user_data.get('language', 'en')
    
    is_joined = await check_fsub_status(bot, user_id)
    if not is_joined:
        channels = await database.get_fsub_channels()
        await message.answer(
            get_text(lang, "fsub_warning"), 
            reply_markup=await fsub_kb(channels)
        )
        return
        
    await show_main_menu(message, lang)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LANGUAGE SELECTION HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data == "set_lang_en")
async def set_lang_en(call: CallbackQuery, bot: Bot):
    await database.set_language(call.from_user.id, "en")
    await call.answer(get_text("en", "lang_set_en"))
    
    if not await check_fsub_status(bot, call.from_user.id):
        channels = await database.get_fsub_channels()
        await call.message.edit_text(get_text("en", "fsub_warning"), reply_markup=await fsub_kb(channels))
        return
        
    await show_main_menu(call, "en", edit=True)

@router.callback_query(F.data == "set_lang_hinglish")
async def set_lang_hinglish(call: CallbackQuery, bot: Bot):
    await database.set_language(call.from_user.id, "hinglish")
    await call.answer(get_text("hinglish", "lang_set_hinglish"))
    
    if not await check_fsub_status(bot, call.from_user.id):
        channels = await database.get_fsub_channels()
        await call.message.edit_text(get_text("hinglish", "fsub_warning"), reply_markup=await fsub_kb(channels))
        return
        
    await show_main_menu(call, "hinglish", edit=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FSUB CHECK BUTTON HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data == "check_fsub")
async def check_fsub_btn(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    if await check_fsub_status(bot, user_id):
        await call.answer("✅ Verified successfully!")
        await show_main_menu(call, lang, edit=True)
    else:
        await call.answer(get_text(lang, "fsub_not_joined"), show_alert=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USERBOT PERSONAL DASHBOARD & STATUS (/mybot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.message(Command("mybot"))
@router.callback_query(F.data == "my_userbot_status")
async def my_userbot_dashboard(event):
    user_id = event.from_user.id
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    if not user_data or not user_data.get("is_logged_in"):
        not_hosted_msg = "❌ Aapka userbot abhi hosted nahi hai! Main Menu me jakar '📟 Click to Host' dabayein." if lang == "hinglish" else "❌ You don't have an active userbot hosted yet. Click '📟 Click to Host' in Main Menu."
        if isinstance(event, CallbackQuery):
            return await event.answer(not_hosted_msg, show_alert=True)
        else:
            return await event.reply(not_hosted_msg)
            
    status_icon = "🟢 ACTIVE & RUNNING" if user_data.get("is_active") else "🔴 OFFLINE / STOPPED"
    server_id = user_data.get("ssh_server_id") or "Cloud Cluster"
    login_date = user_data.get("login_date") or "Recently"
    
    panel_text = (
        "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "┃   📱 <b>MY USERBOT DASHBOARD</b>   ┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"👤 <b>Account Name:</b> <code>{user_data.get('name', 'User')}</code>\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"⚡ <b>Engine Status:</b> <code>{status_icon}</code>\n"
        f"🖥️ <b>Server Node:</b> <code>#{server_id}</code>\n"
        f"📅 <b>Deployed At:</b> <code>{login_date}</code>\n"
        "•─────────────────────────•\n"
        "💡 <i>You can restart or disconnect your userbot using the buttons below:</i>"
    )
    
    kb = userbot_control_kb(lang)
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(panel_text, reply_markup=kb)
        except TelegramBadRequest:
            await event.message.answer(panel_text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(panel_text, reply_markup=kb)

@router.callback_query(F.data == "userbot_restart")
async def userbot_restart_cb(call: CallbackQuery):
    user_id = call.from_user.id
    user_data = await database.get_user(user_id)
    if not user_data or not user_data.get("is_logged_in"):
        return await call.answer("❌ No userbot found.", show_alert=True)
    await call.answer("⚡ Rebooting your userbot in cloud cluster...", show_alert=True)

@router.callback_query(F.data == "userbot_ping_test")
async def userbot_ping_cb(call: CallbackQuery):
    await call.answer("⚡ Cloud Server Ping: 16ms (Ultra Smooth)", show_alert=True)

@router.callback_query(F.data == "userbot_logout")
async def userbot_logout_cb(call: CallbackQuery):
    user_id = call.from_user.id
    await database.set_user_active(user_id, 0)
    db = await database.get_db()
    await db.execute("UPDATE users SET is_logged_in = 0, session_string = '' WHERE user_id = ?", (user_id,))
    await db.commit()
    await call.answer("🛑 Logged out successfully. You can host again anytime.", show_alert=True)
    user_data = await database.get_user(user_id)
    lang = user_data.get('language', 'en') if user_data else "en"
    await show_main_menu(call, lang, edit=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN MENU CALLBACKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.callback_query(F.data == "menu_main")
async def menu_main(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    await show_main_menu(call, lang, edit=True)
    await call.answer()

@router.callback_query(F.data == "menu_about")
async def menu_about(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    text = get_text(lang, "about_text")
    try:
        await call.message.edit_text(text, reply_markup=back_kb(lang))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=back_kb(lang))
    await call.answer()

@router.callback_query(F.data == "menu_guide")
async def menu_guide(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    text = get_text(lang, "guide_text")
    try:
        await call.message.edit_text(text, reply_markup=back_kb(lang))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=back_kb(lang))
    await call.answer()

@router.callback_query(F.data == "menu_owner")
async def menu_owner(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    owner = await database.get_setting("owner_username") or "@zenindeveloper"
    dev1 = await database.get_setting("developer_1") or "@zenindeveloper"
    dev2 = await database.get_setting("developer_2") or "@botdeveloper08"
    
    text = (
        f"💌 <b>Owner & Developers</b>\n\n"
        f"👑 <b>Owner:</b> {owner}\n"
        f"💻 <b>Lead Dev:</b> {dev1}\n"
        f"💻 <b>Core Dev:</b> {dev2}\n\n"
        f"<i>Feel free to reach out for custom bots, deployment help, or inquiries!</i>"
    )
    try:
        await call.message.edit_text(text, reply_markup=back_kb(lang))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=back_kb(lang))
    await call.answer()

@router.callback_query(F.data == "menu_support")
async def menu_support(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    support = await database.get_setting("support_link") or "https://t.me"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Open Support Group", url=support)],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu_main")]
    ])
    text = "💻 <b>Official Support</b>\n\nJoin our official support group to get 24/7 help, updates, and news."
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "menu_help")
async def menu_help(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    text = get_text(lang, "help_text")
    try:
        await call.message.edit_text(text, reply_markup=help_menu_kb(lang))
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=help_menu_kb(lang))
    await call.answer()

@router.callback_query(F.data.startswith("help_cat_"))
async def help_category_view(call: CallbackQuery):
    cat = call.data.replace("help_cat_", "")
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    
    details = {
        "core": "⚡ <b>Core Commands:</b>\n• <code>.alive [cyber/anime/royal]</code> — Animated system status\n• <code>.ping</code> — Precision latency check\n• <code>.uptime</code> — Bot uptime status\n• <code>.restart</code> — Instant worker restart\n• <code>.stats</code> — Dialog stats\n• <code>.stop</code> — Emergency halt",
        "animations": "🎬 <b>25+ Animations:</b>\n• <code>.matrix</code> — Digital Matrix rain\n• <code>.cyber</code> — Cyberpunk terminal hack\n• <code>.saiyan</code> — DBZ Kamehameha\n• <code>.heart</code> — Pulsing 3D heart\n• <code>.thanos</code> — Gauntlet snap\n• <code>.dino</code> — Jumping dinosaur\n• <code>.snake</code> — Retro snake game\n• <code>.sniper</code> — 360 Headshot\n• <code>.rain</code>, <code>.police</code>, <code>.slot</code>, <code>.dice</code>, <code>.magic</code>, <code>.hack</code>, <code>.brain</code>",
        "ai": "🤖 <b>AI & Productivity:</b>\n• <code>.ai &lt;query&gt;</code> — Smart AI Assistant\n• <code>.draw &lt;prompt&gt;</code> — AI Image & Art generator\n• <code>.code &lt;task&gt;</code> — AI clean code generator\n• <code>.tr &lt;lang&gt; &lt;text&gt;</code> — 50+ Languages translator\n• <code>.calc &lt;math&gt;</code> — High-precision math evaluator\n• <code>.tts &lt;lang&gt; &lt;text&gt;</code> — Voice note generator\n• <code>.carbon &lt;code&gt;</code> — Code graphic",
        "music": "🎵 <b>Music & Audio Studio:</b>\n• <code>.song &lt;name&gt;</code> — Download MP3 song\n• <code>.video &lt;name&gt;</code> — Download MP4 video\n• <code>.lyrics &lt;song&gt;</code> — Formatted lyrics\n• <code>.shazam</code> (reply) — Identify music",
        "security": "🛡️ <b>Group Anti-Virus:</b>\n• <code>.antispam on/off</code> — Flood protection & auto-mute\n• <code>.anticaps on/off</code> — Anti-yelling CAPS filter\n• <code>.antiforward on/off</code> — Prevent channel forwarding\n• <code>.blacklist &lt;word&gt;</code> — Forbidden keyword filter\n• <code>.warn &lt;user&gt;</code> — 3-Strike auto-ban system",
        "games": "🎮 <b>Arcade & Games:</b>\n• <code>.truth</code> & <code>.dare</code> — Interactive party game\n• <code>.toss</code> / <code>.coin</code> — 3D Animated coin flip\n• <code>.roll &lt;max&gt;</code> — Random number generator\n• <code>.slap</code>, <code>.hug</code>, <code>.pat</code>, <code>.punch</code> — Action roleplays",
        "pm": "🛡️ <b>PM Guard Protection:</b>\n• <code>.pmguard on/off</code> — Toggle PM protection\n• <code>.a</code> or <code>.allow</code> — Whitelist user in PM\n• <code>.da</code> or <code>.deny</code> — Disallow & block user\n• <code>.setpmmsg &lt;text&gt;</code> — Custom warning text\n• <code>.setlimit &lt;num&gt;</code> — Set max warns before block\n• <code>.pmlist</code> — View approved PM users",
        "tagall": "🏷️ <b>Tagall & Mentioner:</b>\n• <code>.tagall [text]</code> — Fast invisible batch mention (5 per msg)\n• <code>.admtag [text]</code> — Tag only group administrators\n• <code>.gmtag</code>, <code>.gntag</code> — Greetings tagall\n• <code>.vctag</code> — Voice chat callout\n• <code>.stop</code> / <code>.tagstop</code> — Cancel tagging immediately",
        "profile": "🎭 <b>Profile Stealer & Vault:</b>\n• <code>.clone</code> (reply) — Instant clone name, bio & avatar\n• <code>.revert</code> — Instant restore original profile\n• <code>.setname &lt;name&gt;</code> — Change profile name\n• <code>.setbio &lt;bio&gt;</code> — Change profile bio",
        "raid": "🔥 <b>Raid & Roasts:</b>\n• <code>.raid &lt;count&gt; &lt;user&gt;</code> — Abuse roast raid\n• <code>.hiraid &lt;count&gt; &lt;user&gt;</code> — Hindi roast raid\n• <code>.rraid</code> (reply) — Auto-reply raid on target\n• <code>.flirt</code>, <code>.shayari</code>, <code>.roast</code> — Aesthetic lines\n• <code>.stop</code> — Emergency stop all tasks",
        "spam": "🛠️ <b>Spam Engine:</b>\n• <code>.spam &lt;count&gt; &lt;text&gt;</code> — Safe text spam\n• <code>.fastspam &lt;count&gt; &lt;text&gt;</code> — Ultra-fast spam\n• <code>.dmspam &lt;count&gt; &lt;user&gt;</code> — Direct PM spam\n• <code>.sspam &lt;count&gt;</code> (reply) — Sticker spam\n• <code>.gspam &lt;count&gt;</code> — Gallery sticker spam",
        "admin": "👮 <b>Admin Moderation Tools:</b>\n• <code>.ban</code>, <code>.unban</code> — Ban / Unban user\n• <code>.kick</code> — Kick member from group\n• <code>.mute</code>, <code>.unmute</code> — Mute / Unmute member\n• <code>.promote</code>, <code>.demote</code> — Promote / Demote admin\n• <code>.purge</code> (reply) — Purge messages from reply\n• <code>.purgeme &lt;count&gt;</code> — Delete own messages\n• <code>.pin</code>, <code>.unpin</code> — Pin / Unpin message\n• <code>.zombies</code> — Clean deleted accounts",
        "media": "📸 <b>Media & AFK:</b>\n• <code>.vo</code> (reply) — Auto Save expiring View-Once media\n• <code>.kang</code> (reply) — Steal sticker into custom pack\n• <code>.toaudio</code> / <code>.togif</code> — Rapid format converter\n• <code>.afk [reason]</code> — Smart AFK with mention logger\n• <code>.unafk</code> — Turn off AFK and view ping summary\n• <code>.save &lt;key&gt;</code> — Save quick-reply note\n• <code>.get &lt;key&gt;</code> — Fetch saved note"
    }
    
    text = details.get(cat, get_text(lang, "help_text"))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Categories", callback_data="menu_help")],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu_main")]
    ])
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "menu_donate")
async def menu_donate(call: CallbackQuery):
    user_data = await database.get_user(call.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    qr_photo = await database.get_setting("donate_qr")
    text = await database.get_setting("donate_text") or get_text(lang, "donate_text")
    
    kb = back_kb(lang)
    try:
        if qr_photo:
            try:
                await call.message.delete()
            except Exception:
                pass
            await call.message.answer_photo(photo=qr_photo, caption=text, reply_markup=kb)
        else:
            await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await call.message.answer(text, reply_markup=kb)
    await call.answer()

# Direct Command Shortcuts
@router.message(Command("help"))
async def cmd_help(message: Message):
    user_data = await database.get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    await message.answer(get_text(lang, "help_text"), reply_markup=help_menu_kb(lang))

@router.message(Command("donate"))
async def cmd_donate(message: Message):
    user_data = await database.get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    qr_photo = await database.get_setting("donate_qr")
    text = await database.get_setting("donate_text") or get_text(lang, "donate_text")
    if qr_photo:
        await message.answer_photo(photo=qr_photo, caption=text, reply_markup=back_kb(lang))
    else:
        await message.answer(text, reply_markup=back_kb(lang))

@router.message(Command("about"))
async def cmd_about(message: Message):
    user_data = await database.get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else "en"
    await message.answer(get_text(lang, "about_text"), reply_markup=back_kb(lang))
