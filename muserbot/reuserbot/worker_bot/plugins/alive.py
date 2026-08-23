"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/alive.py — Core Diagnostics, Themes & Help       ║
║  Features:                                               ║
║    • .alive [cyber/anime/minimal/royal] (Aesthetic themes)║
║    • .ping (Precision round-trip latency tester)         ║
║    • .uptime (Bot & System uptime tracker)               ║
║    • .stats (Telegram account statistics)                ║
║    • .help [category] (Interactive command catalog)      ║
║    • .restart (Graceful worker restart)                  ║
║    • .eval & .sh (Developer execution tools)             ║
╚═══════════════════════════════════════════════════════════╝
"""

import sys
import time
import os
import io
import asyncio
import logging
import platform
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__ as pyro_version
from pyrogram.types import Message
import worker_globals

logger = logging.getLogger(__name__)

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    time_list.reverse()
    return ":".join(time_list) or "0s"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. MULTI-THEME ALIVE COMMAND (.alive [theme])
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["alive", "bot"], prefixes=".") & filters.me)
async def alive_cmd(client: Client, message: Message):
    start = time.time()
    msg = await message.edit_text("⚡ <code>Checking system pulse...</code>")
    end = time.time()
    ping_ms = round((end - start) * 1000, 2)
    
    uptime = get_readable_time(int(time.time() - worker_globals.START_TIME))
    me = await client.get_me()
    
    theme = message.command[1].lower() if len(message.command) > 1 else "default"
    
    if theme in ["cyber", "hacker", "matrix"]:
        alive_text = (
            "<code>╔═════════════════════════════════╗\n"
            "║   ⚡ CYBERNETIC MUSERBOT v2.5   ║\n"
            "╠═════════════════════════════════╣\n"
            f"║ • ROOT: {me.first_name}\n"
            f"║ • PING: {ping_ms} ms [ULTRA FAST]\n"
            f"║ • UPTIME: {uptime}\n"
            f"║ • SYSTEM: ONLINE / SECURE\n"
            "╚═════════════════════════════════╝</code>\n\n"
            "⚡ <i>Neural Link Stable. Ready for commands.</i>"
        )
    elif theme in ["anime", "kawaii", "cute"]:
        alive_text = (
            "✨ <b>MUserBot Kawaii Edition</b> ✨\n"
            "🌸 ─────────────────────── 🌸\n"
            f"ฅ^•ﻌ•^ฅ <b>Master:</b> <a href='tg://user?id={me.id}'>{me.first_name}</a>\n"
            f"⚡ <b>Speed:</b> <code>{ping_ms} ms</code>\n"
            f"⏳ <b>Active For:</b> <code>{uptime}</code>\n"
            f"🎀 <b>Status:</b> <i>Super Happy & Ready!</i> (◕‿◕✿)\n"
            "🌸 ─────────────────────── 🌸"
        )
    elif theme in ["minimal", "clean"]:
        alive_text = (
            f"🟢 <b>MUserBot Pro</b> | <code>{ping_ms}ms</code>\n"
            f"👤 {me.first_name} | ⏳ <code>{uptime}</code> | 🚀 <code>Active</code>"
        )
    elif theme in ["royal", "gold", "king"]:
        alive_text = (
            "👑 <b>ROYAL MUSERBOT IMPERIAL EDITION</b> 👑\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Emperor:</b> <a href='tg://user?id={me.id}'>{me.first_name}</a>\n"
            f"⚡ <b>Imperial Latency:</b> <code>{ping_ms} ms</code>\n"
            f"⏳ <b>Reign Uptime:</b> <code>{uptime}</code>\n"
            f"🛡️ <b>Shield:</b> <code>AES-128 Encrypted & Invincible</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌟 <i>Long live the Emperor of Telegram!</i>"
        )
    else:
        # Default Cyberpunk Neon Theme
        alive_text = (
            "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃    ⚡ <b>ᴍᴜsᴇʀʙᴏᴛ ᴘʀᴏ ᴠ2.5</b> ⚡    ┃\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n"
            f"<b>• ᴍᴀsᴛᴇʀ :</b> <a href='tg://user?id={me.id}'>{me.first_name}</a>\n"
            f"<b>• sᴛᴀᴛᴜs :</b> 🟢 <code>ᴀᴄᴛɪᴠᴇ & sᴍᴏᴏᴛʜ</code>\n"
            f"<b>• ᴘɪɴɢ :</b> <code>{ping_ms} ms</code> ⚡\n"
            f"<b>• ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime}</code>\n"
            f"<b>• ᴘʏʀᴏɢʀᴀᴍ :</b> <code>v{pyro_version}</code>\n"
            f"<b>• ᴘʏᴛʜᴏɴ :</b> <code>v{platform.python_version()}</code>\n"
            f"<b>• ᴘʟᴀᴛғᴏʀᴍ :</b> <code>{platform.system()} {platform.release()}</code>\n"
            "•─────────────────────────•\n"
            "💡 <i>Themes:</i> <code>.alive cyber</code> | <code>.alive anime</code> | <code>.alive royal</code>"
        )
    
    await msg.edit_text(alive_text, disable_web_page_preview=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. PING COMMAND (.ping)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    msg = await message.edit_text("🏓 <code>Pinging...</code>")
    end = time.time()
    ping_ms = round((end - start) * 1000, 2)
    
    if ping_ms < 100:
        bar = "⚡ [██████████] ULTRA FAST"
    elif ping_ms < 250:
        bar = "⚡ [███████▒▒▒] FAST"
    elif ping_ms < 500:
        bar = "⚡ [████▒▒▒▒▒▒] MODERATE"
    else:
        bar = "⚡ [██▒▒▒▒▒▒▒▒] SLOW"
        
    await msg.edit_text(
        f"🏓 <b>Pong!</b> <code>{ping_ms} ms</code>\n"
        f"<code>{bar}</code>"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. UPTIME COMMAND (.uptime)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("uptime", prefixes=".") & filters.me)
async def uptime_cmd(client: Client, message: Message):
    uptime = get_readable_time(int(time.time() - worker_globals.START_TIME))
    await message.edit_text(f"⏳ <b>MUserBot Active Uptime:</b> <code>{uptime}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. STATS COMMAND (.stats)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("stats", prefixes=".") & filters.me)
async def stats_cmd(client: Client, message: Message):
    await message.edit_text("📊 <code>Scanning dialogs...</code>")
    
    groups = 0
    supergroups = 0
    channels = 0
    users = 0
    bots = 0
    
    async for dialog in client.get_dialogs():
        chat_type = dialog.chat.type.value
        if chat_type == "private":
            users += 1
        elif chat_type == "bot":
            bots += 1
        elif chat_type == "group":
            groups += 1
        elif chat_type == "supergroup":
            supergroups += 1
        elif chat_type == "channel":
            channels += 1
            
    stats_msg = (
        "📊 <b>Account Dialog Statistics</b>\n\n"
        f"💬 <b>Private Chats:</b> <code>{users}</code>\n"
        f"🤖 <b>Bots:</b> <code>{bots}</code>\n"
        f"👥 <b>Basic Groups:</b> <code>{groups}</code>\n"
        f"👥 <b>Supergroups:</b> <code>{supergroups}</code>\n"
        f"📢 <b>Channels:</b> <code>{channels}</code>\n"
        f"📁 <b>Total Dialogs:</b> <code>{users + bots + groups + supergroups + channels}</code>"
    )
    await message.edit_text(stats_msg)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. RESTART COMMAND (.restart)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("restart", prefixes=".") & filters.me)
async def restart_cmd(client: Client, message: Message):
    await message.edit_text("🔄 <b>Rebooting MUserBot Pro Engine...</b>\n<i>Please wait a few seconds.</i>")
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        await message.edit_text(f"❌ Restart Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. HELP COMMAND (.help [category])
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HELP_DATA = {
    "core": "⚡ <b>Core Module:</b>\n• <code>.alive [cyber/anime/royal]</code> — Animated status banner\n• <code>.ping</code> — Precision latency\n• <code>.uptime</code> — Bot uptime\n• <code>.stats</code> — Dialog counts\n• <code>.restart</code> — Reboot worker\n• <code>.stop</code> — Halt all active tasks",
    "animations": "🎬 <b>Animations:</b>\n• <code>.matrix</code> — Matrix code rain\n• <code>.cyber</code> — Cyberpunk terminal hack\n• <code>.saiyan</code> — DBZ power charge\n• <code>.heart</code> — Pulsing 3D heart\n• <code>.thanos</code> — Gauntlet snap\n• <code>.dino</code> — Jumping dinosaur\n• <code>.snake</code> — Retro snake game\n• <code>.sniper</code> — 360 Headshot\n• <code>.rain</code> — Storm and thunder\n• <code>.police</code> — Siren lights\n• <code>.slot</code> — Casino slot machine\n• <code>.dice</code> — 3D dice roll\n• <code>.magic</code>, <code>.hack</code>, <code>.brain</code>, <code>.kiss</code>, <code>.fuck</code>",
    "ai": "🤖 <b>AI & Tools:</b>\n• <code>.ai &lt;query&gt;</code> — Smart AI Assistant\n• <code>.draw &lt;prompt&gt;</code> — AI Image generator\n• <code>.code &lt;task&gt;</code> — AI Code writer\n• <code>.tr &lt;lang&gt; &lt;text&gt;</code> — 50+ Languages translator\n• <code>.calc &lt;math&gt;</code> — Math evaluator\n• <code>.tts &lt;lang&gt; &lt;text&gt;</code> — Voice note audio\n• <code>.carbon &lt;code&gt;</code> — Carbon code image\n• <code>.quote</code> — Quote sticker",
    "music": "🎵 <b>Music & Audio Studio:</b>\n• <code>.song &lt;name&gt;</code> — Download MP3 song\n• <code>.video &lt;name&gt;</code> — Download MP4 video\n• <code>.lyrics &lt;song&gt;</code> — Formatted song lyrics\n• <code>.shazam</code> (reply) — Identify music from audio",
    "security": "🛡️ <b>Group Anti-Virus:</b>\n• <code>.antispam on/off</code> — Auto flood muting\n• <code>.anticaps on/off</code> — Auto delete ALL-CAPS yelling\n• <code>.antiforward on/off</code> — Prevent channel forwarding\n• <code>.blacklist &lt;word&gt;</code> — Forbidden keyword auto-delete\n• <code>.warn &lt;user&gt;</code> — 3-Strike Auto-ban system",
    "games": "🎮 <b>Arcade & Games:</b>\n• <code>.truth</code> & <code>.dare</code> — Interactive party game\n• <code>.toss</code> / <code>.coin</code> — 3D Animated coin flip\n• <code>.roll &lt;max&gt;</code> — Random number generator\n• <code>.slap</code>, <code>.hug</code>, <code>.pat</code>, <code>.punch</code> — Action roleplays",
    "automations": "⚡ <b>Automations:</b>\n• <code>.autobio on/off</code> — Real-time live clock bio\n• <code>.autoreact on/off &lt;emoji&gt;</code> — Auto emoji reactions\n• <code>.antidelete on/off</code> — Log deleted messages",
    "pm": "🛡️ <b>PM Guard Protection:</b>\n• <code>.pmguard on/off</code> — Toggle protection\n• <code>.a</code> / <code>.allow</code> — Approve contact\n• <code>.da</code> / <code>.deny</code> — Block & remove\n• <code>.setpmmsg &lt;text&gt;</code> — Custom warning\n• <code>.setlimit &lt;num&gt;</code> — Block limit count\n• <code>.pmlist</code> — View approved list",
    "tagall": "🏷️ <b>Tagall & Mentioner:</b>\n• <code>.tagall [text]</code> — Fast 5-per-batch mention\n• <code>.admtag [text]</code> — Tag only group admins\n• <code>.gmtag</code>, <code>.gntag</code> — Morning/Night tags\n• <code>.vctag</code> — Voice chat call\n• <code>.stop</code> / <code>.tagstop</code> — Cancel tagging",
    "profile": "🎭 <b>Profile Stealer & Vault:</b>\n• <code>.clone</code> (reply) — Instant clone user\n• <code>.revert</code> — Restore original profile\n• <code>.setname &lt;name&gt;</code> — Change account name\n• <code>.setbio &lt;bio&gt;</code> — Change account bio",
    "raid": "🔥 <b>Raid & Roasts:</b>\n• <code>.raid &lt;count&gt; &lt;user&gt;</code> — Abuse raid\n• <code>.hiraid &lt;count&gt; &lt;user&gt;</code> — Hindi roast\n• <code>.rraid</code> (reply) — Auto-reply raid target\n• <code>.flirt</code>, <code>.shayari</code>, <code>.roast</code> — Fun lines\n• <code>.stop</code> — Emergency halt",
    "spam": "🛠️ <b>Spam Engine:</b>\n• <code>.spam &lt;count&gt; &lt;text&gt;</code> — Text spam\n• <code>.fastspam &lt;count&gt; &lt;text&gt;</code> — Ultra-fast spam\n• <code>.dmspam &lt;count&gt; &lt;user&gt; &lt;text&gt;</code> — PM spam\n• <code>.sspam</code> / <code>.gspam</code> — Sticker spam\n• <code>.stop</code> — Cancel spam",
    "admin": "👮 <b>Admin Moderation:</b>\n• <code>.ban</code>, <code>.unban</code>, <code>.kick</code> — Member actions\n• <code>.mute</code>, <code>.unmute</code> — Restrict user\n• <code>.promote</code>, <code>.demote</code> — Admin permissions\n• <code>.purge</code> (reply) — Bulk delete from reply\n• <code>.purgeme &lt;count&gt;</code> — Delete own messages\n• <code>.pin</code>, <code>.unpin</code> — Pin message\n• <code>.zombies</code> — Clean deleted accounts",
    "media": "📸 <b>Media & AFK:</b>\n• <code>.vo</code> (reply) — Auto View-Once Saver\n• <code>.kang</code> (reply) — Steal sticker\n• <code>.afk [reason]</code> — Smart AFK with logger\n• <code>.unafk</code> — Turn off AFK\n• <code>.save &lt;key&gt;</code> — Save quick-reply note\n• <code>.get &lt;key&gt;</code> — Send note\n• <code>.notes</code> — List notes"
}

@Client.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_cmd(client: Client, message: Message):
    parts = message.text.split(" ", 1)
    if len(parts) > 1:
        cat = parts[1].lower().strip()
        if cat in HELP_DATA:
            return await message.edit_text(HELP_DATA[cat])
            
    overview = (
        "┌────── ˹ ᴍᴜsᴇʀʙᴏᴛ ʜᴇʟᴘ ˼ ⏤͟͟͞͞★\n"
        "┆◍ ʜᴇʏ, ʜᴇʀᴇ ᴀʀᴇ ᴍʏ ᴄᴏᴍᴍᴀɴᴅ ᴍᴏᴅᴜʟᴇs:\n"
        "└────────────────────────•\n\n"
        "➥ <code>.help core</code> — <i>Core & Diagnostics</i>\n"
        "➥ <code>.help animations</code> — <i>25+ Smooth Animations</i>\n"
        "➥ <code>.help ai</code> — <i>AI, Drawing & Code</i>\n"
        "➥ <code>.help music</code> — <i>Music, Songs & Shazam</i>\n"
        "➥ <code>.help security</code> — <i>Group Anti-Virus & Warns</i>\n"
        "➥ <code>.help games</code> — <i>Arcade, Truth & Dare</i>\n"
        "➥ <code>.help automations</code> — <i>Auto-Bio & Reactions</i>\n"
        "➥ <code>.help pm</code> — <i>PM Guard Security</i>\n"
        "➥ <code>.help tagall</code> — <i>Batch & Single Mentioner</i>\n"
        "➥ <code>.help profile</code> — <i>Clone & Profile Vault</i>\n"
        "➥ <code>.help raid</code> — <i>Raid & Roast Engine</i>\n"
        "➥ <code>.help spam</code> — <i>Fast & Media Spam</i>\n"
        "➥ <code>.help admin</code> — <i>Group Moderation</i>\n"
        "➥ <code>.help media</code> — <i>View-Once & AFK</i>\n\n"
        "•────────────────────────•\n"
        "💡 <i>Example:</i> <code>.help music</code>"
    )
    await message.edit_text(overview)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. EVAL / EXEC / SHELL (Owner Debugging)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["eval", "e"], prefixes=".") & filters.me)
async def eval_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ Provide python code to evaluate.")
        
    code = message.text.split(" ", 1)[1]
    msg = await message.edit_text("⏳ <code>Evaluating...</code>")
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    redirected_error = io.StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error
    
    try:
        exec_locals = {}
        exec(f"async def __aexec(client, message): " + "".join(f"\n {l}" for l in code.split("\n")), {}, exec_locals)
        res = await exec_locals["__aexec"](client, message)
        out = redirected_output.getvalue() or redirected_error.getvalue() or str(res or "Executed successfully (No output).")
        await msg.edit_text(f"<b>Code:</b>\n<code>{code}</code>\n\n<b>Output:</b>\n<code>{out[:3000]}</code>")
    except Exception as e:
        await msg.edit_text(f"<b>Code:</b>\n<code>{code}</code>\n\n<b>Error:</b>\n<code>{str(e)}</code>")
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

@Client.on_message(filters.command(["sh", "terminal"], prefixes=".") & filters.me)
async def shell_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ Provide bash command to execute.")
        
    cmd = message.text.split(" ", 1)[1]
    msg = await message.edit_text("⏳ <code>Running shell command...</code>")
    
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        result = stdout.decode().strip() or stderr.decode().strip() or "Success (No Output)"
        await msg.edit_text(f"<b>Command:</b> <code>{cmd}</code>\n\n<b>Output:</b>\n<code>{result[:3000]}</code>")
    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{str(e)}</code>")
