"""
╔═══════════════════════════════════════════════════════════╗
║  languages.py / language.py — Multi-Language Dictionary  ║
║  Supports: English (en) & Hinglish (hinglish)             ║
║  Ultra-optimized with complete fallbacks                  ║
╚═══════════════════════════════════════════════════════════╝
"""

LANGUAGES = {
    "en": {
        # ─── START & LANGUAGE SELECTION ───────────────────
        "choose_lang": "🌐 <b>Please select your language.</b>\n<i>Choose a language to continue.</i>",
        "lang_set_en": "✅ Language set to <b>English</b>.",
        "lang_set_hinglish": "✅ Language set to <b>Hinglish</b>.",
        
        # ─── MAIN MENU TEXTS ──────────────────────────────
        "start_text": (
            "┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞★\n"
            "┆◍ ʜᴇʏ, ɪ ᴀᴍ : <b>MUserBot Pro</b>\n"
            "┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !\n"
            "└────────────────────────•\n\n"
            "➻ ᴀ ғᴀsᴛ, sᴍᴏᴏᴛʜ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴜsᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
            "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n"
            "❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ ғᴜɴ, ʀᴀɪᴅ, sᴘᴀᴍ, ᴀɪ & ᴍᴇᴅɪᴀ.\n"
            "❖ ɪ ᴄᴀɴ ʙᴏᴏsᴛ ʏᴏᴜʀ ɪᴅ ᴡɪᴛʜ ᴜʟᴛʀᴀ-sᴍᴏᴏᴛʜ ᴀɴɪᴍᴀᴛɪᴏɴs.\n"
            "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n\n"
            "๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."
        ),
        
        # ─── BUTTON LABELS ────────────────────────────────
        "btn_host": "📟 Click to Host",
        "btn_about": "📗 About",
        "btn_owner": "💌 Owner",
        "btn_guide": "💡 Guide",
        "btn_support": "💻 Support",
        "btn_help": "❓ Help & Commands",
        "btn_donate": "💰 Donate",
        "btn_back": "🔙 Back",
        "btn_refresh": "🔄 Refresh",
        "btn_admin_panel": "⚙️ Admin Panel",
        "btn_dashboard": "🖥️ Dashboard",
        "btn_stats": "📊 Bot Stats",
        
        # ─── HOSTING PROCESS ──────────────────────────────
        "host_prompt": "📱 <b>Send your phone number</b> in international format on which you want to host the bot.\n\n<i>Example: +919876543210</i>",
        "otp_prompt": "🔒 <b>Fill OTP</b> ____\n\nPlease enter the OTP sent to your Telegram account.",
        "twofa_prompt": "🔑 <b>Two Step Verification</b>\n\nYour account has 2FA enabled. Please send your Two-Step Verification password.",
        "host_success": "✅ <b>Secure data encrypted!</b>\n\n🎉 <b>Your userbot has been hosted and deployed successfully!</b>\nSend <code>.alive</code> or <code>.help</code> in any chat to get started.",
        "invalid_number": "❌ Invalid number! Please send a valid international format number (e.g. +919876543210).",
        "invalid_otp": "❌ Wrong OTP! Please try again and send the correct OTP.",
        "invalid_2fa": "❌ Wrong Password! Please send the correct Two-Step Verification password.",
        
        # ─── GUIDE & ABOUT ────────────────────────────────
        "guide_text": (
            "❖ <b>MUserBot Pro Quick Hosting Guide</b>\n\n"
            "1️⃣ Send /host or click <b>📟 Click to Host</b>\n"
            "2️⃣ Send your phone number in international format (e.g., <code>+919876543210</code>)\n"
            "3️⃣ Telegram will send an official login code to your Telegram app\n"
            "4️⃣ Enter the OTP digits using the interactive inline keypad\n"
            "5️⃣ If you have 2FA enabled, enter your 2FA password\n\n"
            "🚀 <b>Your Userbot will be deployed 24/7 instantly!</b>\n\n"
            "Commands to try after hosting:\n"
            "• <code>.alive</code> — Check status & system info\n"
            "• <code>.help</code> — View all 100+ commands\n"
            "• <code>.ping</code> — Check ultra-fast speed\n"
            "• <code>.matrix</code> — Smooth digital rain animation"
        ),
        "about_text": (
            "┌────── ˹ ᴀʙᴏᴜᴛ ᴍᴜsᴇʀʙᴏᴛ ˼ ⏤͟͟͞͞★\n"
            "┆◍ <b>Version:</b> <code>v2.5.0 Ultra Pro</code>\n"
            "┆● <b>Engine:</b> Pyrogram Async Core\n"
            "┆◍ <b>Security:</b> Fernet AES-128-CBC + PBKDF2\n"
            "┆● <b>Developer:</b> @zenindeveloper | @botdeveloper08\n"
            "┆◍ <b>Support:</b> Click Support Button\n"
            "┆● <b>Languages:</b> English & Hinglish\n"
            "└────────────────────────•"
        ),
        "help_text": (
            "📖 <b>MUserBot Pro Command Center</b>\n\n"
            "Here is the list of powerful command categories available on your userbot:\n\n"
            "⚡ <b>Core:</b> <code>.alive</code>, <code>.ping</code>, <code>.uptime</code>, <code>.restart</code>, <code>.stats</code>\n"
            "🎬 <b>Animations:</b> <code>.matrix</code>, <code>.cyber</code>, <code>.saiyan</code>, <code>.heart</code>, <code>.thanos</code>, <code>.dino</code>, <code>.hack</code>\n"
            "🤖 <b>AI & Tools:</b> <code>.ai</code>, <code>.gpt</code>, <code>.tr</code>, <code>.calc</code>, <code>.tts</code>, <code>.quote</code>, <code>.carbon</code>\n"
            "🛡️ <b>PM Guard:</b> <code>.pmguard on/off</code>, <code>.a</code>, <code>.da</code>, <code>.setpmmsg</code>, <code>.setlimit</code>\n"
            "🏷️ <b>Tagall:</b> <code>.tagall</code>, <code>.admtag</code>, <code>.gmtag</code>, <code>.vctag</code>, <code>.stop</code>\n"
            "🎭 <b>Profile:</b> <code>.clone</code>, <code>.revert</code>, <code>.saveprofile</code>, <code>.loadprofile</code>\n"
            "🔥 <b>Raid & Fun:</b> <code>.raid</code>, <code>.hiraid</code>, <code>.rraid</code>, <code>.spam</code>, <code>.dmspam</code>, <code>.stop</code>\n"
            "👮 <b>Admin:</b> <code>.ban</code>, <code>.kick</code>, <code>.mute</code>, <code>.purge</code>, <code>.purgeme</code>, <code>.pin</code>\n"
            "💤 <b>AFK:</b> <code>.afk [reason]</code>, <code>.unafk</code>\n"
            "📝 <b>Notes:</b> <code>.save</code>, <code>.get</code>, <code>.delnote</code>, <code>.notes</code>\n"
            "📸 <b>Media:</b> <code>.vo</code> (Auto View-Once Saver), <code>.kang</code>, <code>.toaudio</code>\n\n"
            "💡 Type <code>.help <category></code> in any chat using your userbot for in-depth details!"
        ),
        
        # ─── FORCE SUB ─────────────────────────────────────
        "fsub_warning": "🔒 <b>Join Required!</b>\n\nPlease join our official channel(s) to use this bot. After joining, click the button below.",
        "fsub_joined_btn": "✅ I Joined",
        "fsub_not_joined": "❌ You haven't joined all channels yet! Please join them first.",
        
        # ─── DONATE ────────────────────────────────────────
        "donate_text": (
            "💝 <b>Support MUserBot Development</b>\n\n"
            "We value every single donation, whether it's ₹1 or ₹1000. "
            "Your contribution helps us keep this bot free, optimized, and running 24/7 "
            "for everyone in the community.\n\n"
            "🤝 <i>Every contribution keeps our high-speed servers alive!</i>\n\n"
            "Scan the QR code below or contact the Owner to donate:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        
        # ─── ERRORS ────────────────────────────────────────
        "error_occured": "⚠️ An error occurred. Please try again later.",
        "not_admin": "❌ You are not authorized to use this command.",
        "no_ssh_servers": "❌ No SSH servers available right now. Please try again later.",
    },

    "hinglish": {
        # ─── START & LANGUAGE SELECTION ───────────────────
        "choose_lang": "🌐 <b>Kripya apni bhasha select karein.</b>\n<i>Continue karne ke liye ek bhasha chunein.</i>",
        "lang_set_en": "✅ Bhasha <b>English</b> set kar di gayi hai.",
        "lang_set_hinglish": "✅ Bhasha <b>Hinglish</b> set kar di gayi hai.",
        
        # ─── MAIN MENU TEXTS ──────────────────────────────
        "start_text": (
            "┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞★\n"
            "┆◍ ʜᴇʏ, ɪ ᴀᴍ : <b>MUserBot Pro</b>\n"
            "┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !\n"
            "└────────────────────────•\n\n"
            "➻ ᴀ ғᴀsᴛ, sᴍᴏᴏᴛʜ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴜsᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
            "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n"
            "❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ ғᴜɴ, ʀᴀɪᴅ, sᴘᴀᴍ, ᴀɪ & ᴍᴇᴅɪᴀ.\n"
            "❖ ɪ ᴄᴀɴ ʙᴏᴏsᴛ ʏᴏᴜʀ ɪᴅ ᴡɪᴛʜ ᴜʟᴛʀᴀ-sᴍᴏᴏᴛʜ ᴀɴɪᴍᴀᴛɪᴏɴs.\n"
            "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n\n"
            "๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."
        ),
        
        # ─── BUTTON LABELS ────────────────────────────────
        "btn_host": "📟 Click to Host",
        "btn_about": "📗 About",
        "btn_owner": "💌 Owner",
        "btn_guide": "💡 Guide",
        "btn_support": "💻 Support",
        "btn_help": "❓ Help & Commands",
        "btn_donate": "💰 Donate",
        "btn_back": "🔙 Back",
        "btn_refresh": "🔄 Refresh",
        "btn_admin_panel": "⚙️ Admin Panel",
        "btn_dashboard": "🖥️ Dashboard",
        "btn_stats": "📊 Bot Stats",
        
        # ─── HOSTING PROCESS ──────────────────────────────
        "host_prompt": "📱 <b>Apna phone number bhejein</b> international format me jispe aap bot host karna chahte ho.\n\n<i>Example: +919876543210</i>",
        "otp_prompt": "🔒 <b>OTP Bharo</b> ____\n\nAapke Telegram pe OTP bheja gaya hai. Kripya keypad se OTP dalein.",
        "twofa_prompt": "🔑 <b>Two Step Verification</b>\n\nAapke account me 2FA enabled hai. Apna Two-Step Verification password bhejein.",
        "host_success": "✅ <b>Secure data encrypted!</b>\n\n🎉 <b>Aapka userbot successfully host aur deploy ho gaya hai!</b>\nCheck karne ke liye kisi bhi chat me <code>.alive</code> ya <code>.help</code> bhejein.",
        "invalid_number": "❌ Galat number! Kripya sahi international format me number bhejein (e.g. +919876543210).",
        "invalid_otp": "❌ Galat OTP! Kripya dobara try karein aur sahi OTP dalein.",
        "invalid_2fa": "❌ Galat Password! Kripya sahi Two-Step Verification password bhejein.",
        
        # ─── GUIDE & ABOUT ────────────────────────────────
        "guide_text": (
            "❖ <b>MUserBot Pro Host Karne Ka Aasaan Guide</b>\n\n"
            "1️⃣ /host bhejo ya <b>📟 Click to Host</b> par click karo\n"
            "2️⃣ Apna phone number international format me bhejo (e.g., <code>+919876543210</code>)\n"
            "3️⃣ Telegram app pe official login OTP aayega\n"
            "4️⃣ Screen pe dikhe keypad se OTP enter karo aur Submit dabao\n"
            "5️⃣ Agar 2FA password laga rakha hai toh wo bhejo\n\n"
            "🚀 <b>Aapka Userbot 24/7 deploy ho jayega!</b>\n\n"
            "Host hone ke baad ye commands try karein:\n"
            "• <code>.alive</code> — Bot ka mast animated status dekho\n"
            "• <code>.help</code> — Saare 100+ commands ki list\n"
            "• <code>.ping</code> — Superfast speed check\n"
            "• <code>.matrix</code> — Awesome matrix animation"
        ),
        "about_text": (
            "┌────── ˹ ᴀʙᴏᴜᴛ ᴍᴜsᴇʀʙᴏᴛ ˼ ⏤͟͟͞͞★\n"
            "┆◍ <b>Version:</b> <code>v2.5.0 Ultra Pro</code>\n"
            "┆● <b>Engine:</b> Pyrogram Async Core\n"
            "┆◍ <b>Security:</b> Fernet AES-128-CBC + PBKDF2\n"
            "┆● <b>Developer:</b> @zenindeveloper | @botdeveloper08\n"
            "┆◍ <b>Support:</b> Click Support Button\n"
            "┆● <b>Language:</b> English & Hinglish\n"
            "└────────────────────────•"
        ),
        "help_text": (
            "📖 <b>MUserBot Pro Command Center</b>\n\n"
            "Aapke userbot ke sabhi tagde features aur categories:\n\n"
            "⚡ <b>Core:</b> <code>.alive</code>, <code>.ping</code>, <code>.uptime</code>, <code>.restart</code>, <code>.stats</code>\n"
            "🎬 <b>Animations:</b> <code>.matrix</code>, <code>.cyber</code>, <code>.saiyan</code>, <code>.heart</code>, <code>.thanos</code>, <code>.dino</code>, <code>.hack</code>\n"
            "🤖 <b>AI & Tools:</b> <code>.ai</code>, <code>.gpt</code>, <code>.tr</code>, <code>.calc</code>, <code>.tts</code>, <code>.quote</code>, <code>.carbon</code>\n"
            "🛡️ <b>PM Guard:</b> <code>.pmguard on/off</code>, <code>.a</code>, <code>.da</code>, <code>.setpmmsg</code>, <code>.setlimit</code>\n"
            "🏷️ <b>Tagall:</b> <code>.tagall</code>, <code>.admtag</code>, <code>.gmtag</code>, <code>.vctag</code>, <code>.stop</code>\n"
            "🎭 <b>Profile:</b> <code>.clone</code>, <code>.revert</code>, <code>.saveprofile</code>, <code>.loadprofile</code>\n"
            "🔥 <b>Raid & Fun:</b> <code>.raid</code>, <code>.hiraid</code>, <code>.rraid</code>, <code>.spam</code>, <code>.dmspam</code>, <code>.stop</code>\n"
            "👮 <b>Admin:</b> <code>.ban</code>, <code>.kick</code>, <code>.mute</code>, <code>.purge</code>, <code>.purgeme</code>, <code>.pin</code>\n"
            "💤 <b>AFK:</b> <code>.afk [reason]</code>, <code>.unafk</code>\n"
            "📝 <b>Notes:</b> <code>.save</code>, <code>.get</code>, <code>.delnote</code>, <code>.notes</code>\n"
            "📸 <b>Media:</b> <code>.vo</code> (Auto View-Once Saver), <code>.kang</code>, <code>.toaudio</code>\n\n"
            "💡 Userbot me kisi bhi category ki detail ke liye <code>.help <category></code> likhein!"
        ),
        
        # ─── FORCE SUB ─────────────────────────────────────
        "fsub_warning": "🔒 <b>Join Zaruri Hai!</b>\n\nBot use karne ke liye hamare official channels join karein. Join karne ke baad niche button par click karein.",
        "fsub_joined_btn": "✅ Main Join Kar Liya",
        "fsub_not_joined": "❌ Aap abhi tak saare channels join nahi kar paye! Kripya pehle unhe join karein.",
        
        # ─── DONATE ────────────────────────────────────────
        "donate_text": (
            "💝 <b>Support Our Mission</b>\n\n"
            "Hum har ek donation ki value karte hain, chahe wo ₹1 ho ya ₹1000. "
            "Aapka yogdaan humein is bot ko free aur 24/7 chalu rakhne me madad karta hai "
            "sabke liye.\n\n"
            "🤝 <i>Har rupya matter karta hai. Har dil count karta hai.</i>\n\n"
            "Donate karne ke liye niche QR code scan karein:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        
        # ─── ERRORS ────────────────────────────────────────
        "error_occured": "⚠️ Kuch error aa gaya hai. Kripya thodi der baad try karein.",
        "not_admin": "❌ Aap is command ko use karne ke authorized nahi hain.",
        "no_ssh_servers": "❌ Abhi koi SSH server available nahi hai. Kripya thodi der baad try karein.",
    }
}

def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Get translated text for a specific language and key with safe fallback.
    """
    lang_dict = LANGUAGES.get(lang, LANGUAGES["en"])
    text = lang_dict.get(key, LANGUAGES["en"].get(key, f"❌ {key}"))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    
    return text
