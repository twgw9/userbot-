import random

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ASCII ART & DECORATORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_ascii_header(text: str) -> str:
    """Text ke upar aur niche border lagane ke liye"""
    border = "╔" + "═" * (len(text) + 2) + "╗"
    middle = f"║ {text} ║"
    end = "╚" + "═" * (len(text) + 2) + "╝"
    return f"<code>{border}\n{middle}\n{end}</code>"

def get_random_ascii_rose() -> str:
    """Raid ya flirt ke liye random rose art"""
    roses = [
        "✿━━━━━━━━━━━━━━━━✿\n      🥀  🌹  🌸  \n✿━━━━━━━━━━━━━━━━✿",
        "🌹🌹🌹🌹🌹🌹🌹🌹\n  𝓗𝓪𝓹𝓹𝔂 𝓡𝓪𝓲𝓭  \n🌹🌹🌹🌹🌹🌹🌹🌹",
        "💖━━━━━━━━━━━━━━━💖\n     𝓛𝓸𝓿𝓮 𝓨𝓸𝓾    \n💖━━━━━━━━━━━━━━━💖"
    ]
    return random.choice(roses)

def format_userbot_help() -> str:
    """Pyrogram Worker Bot ke .help command ka premium layout"""
    return (
        "┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞★\n"
        "┆◍ ʜᴇʏ, ɪ ᴀᴍ : <b>Free Userbot</b>\n"
        "┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !\n"
        "└────────────────────────•\n\n"
        "➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴜsᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
        "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n"
        "❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ ғᴜɴ ʀᴀɪᴅ sᴘᴀᴍ.\n"
        "❖ ɪ ᴄᴀɴ ʙᴏᴏsᴛ ʏᴏᴜʀ ɪᴅ ᴡɪᴛʜ ᴀɴɪᴍᴀᴛɪᴏɴ\n"
        "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n\n"
        "𝗛𝗲𝗹𝗽 𝗠𝗲𝗻𝘂:\n"
        "➥ <code>.help spam</code> - Sᴘᴀᴍ ᴄᴏᴍᴍᴀɴᴅs\n"
        "➥ <code>.help raid</code> - Rᴀɪᴅ ᴄᴏᴍᴍᴀɴᴅs\n"
        "➥ <code>.help tag</code> - Tᴀɢᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs\n"
        "➥ <code>.help admin</code> - Aᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs\n"
    )

def get_ascii_middle_finger() -> str:
    """.fuck command ke liye ASCII art"""
    return (
        "╭━━━━━━━━━━━━━━━╮\n"
        "┃  ＥＡＴ ＴＨＩＳ  ┃\n"
        "┃      🖕      ┃\n"
        "╰━━━━━━━━━━━━━━━╯"
    )

def get_loading_animation() -> str:
    """Hack ya background process ke liye loading dots"""
    return "⏳ [█▒▒▒▒▒▒▒▒▒] 10%..."

# Aap aur bhi ASCII arts yahan add kar sakte hain