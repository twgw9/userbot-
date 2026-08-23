"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/animations.py — Ultra-Smooth Dynamic Animations  ║
║  25+ High-FPS, Aesthetic & Adaptive Visual Animations     ║
║  Auto FloodWait handler, Smooth frame transitions         ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified

logger = logging.getLogger(__name__)

async def animate(message: Message, frames: list, delay: float = 0.6, delete_after: bool = False):
    """Safe, non-blocking high-speed animation engine"""
    try:
        current_msg = message
        # Use initial frame
        await current_msg.edit_text(frames[0])
        await asyncio.sleep(delay)
        
        for frame in frames[1:]:
            try:
                await current_msg.edit_text(frame)
                await asyncio.sleep(delay)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await current_msg.edit_text(frame)
            except MessageNotModified:
                pass
            except Exception:
                break
                
        if delete_after:
            await asyncio.sleep(1.2)
            await current_msg.delete()
            
    except Exception as e:
        logger.error(f"Animation execution exception: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. MATRIX DIGITAL RAIN (.matrix)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("matrix", prefixes=".") & filters.me)
async def matrix_anim(client: Client, message: Message):
    frames = [
        "<code>0 1 0 0 1 0 1</code>",
        "<code>1 0 1 1 0 1 0\n0 1 0 0 1 0 1</code>",
        "<code>0 1 1 0 1 0 0\n1 0 1 1 0 1 0\n0 1 0 0 1 0 1</code>",
        "<code>1 0 0 1 0 1 1\n0 1 1 0 1 0 0\n1 0 1 1 0 1 0</code>",
        "<code>🟢 MATRIX SYSTEM BREACHED...\n0 1 1 0 1 0 0 1 0 1 0 1\n1 0 0 1 0 1 1 0 1 0 1 0</code>",
        "<code>⚡ ACCESS GRANTED: ROOT USER ⚡</code>"
    ]
    await animate(message, frames, delay=0.5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. CYBERPUNK TERMINAL HACK (.cyber)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["cyber", "cyberpunk"], prefixes=".") & filters.me)
async def cyber_anim(client: Client, message: Message):
    frames = [
        "🌐 <code>[CYBERNETIC CORE] Booting up neural link...</code>",
        "🌐 <code>[CYBERNETIC CORE] Injecting quantum payload...</code>",
        "🔒 <code>Bypassing Sub-Orbital Firewall... [░░░░░░░░░░] 0%</code>",
        "🔒 <code>Bypassing Sub-Orbital Firewall... [████░░░░░░] 40%</code>",
        "🔓 <code>Bypassing Sub-Orbital Firewall... [████████░░] 80%</code>",
        "🔓 <code>Bypassing Sub-Orbital Firewall... [██████████] 100%</code>",
        "⚡ <code>DECRYPTING TARGET TELECOM DATA...</code>",
        "💎 <b>CYBERPUNK MAINFRAME OVERRIDDEN!</b>\n<code>City systems under master control.</code>"
    ]
    await animate(message, frames, delay=0.7)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. SUPER SAIYAN POWER CHARGE (.saiyan, .dbz)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["saiyan", "dbz", "goku"], prefixes=".") & filters.me)
async def saiyan_anim(client: Client, message: Message):
    frames = [
        "😡 <i>Haaaaa....</i>",
        "😠 <i>HAAAAAAA.......</i>",
        "⚡ <b>HAAAAAAAAAA.........!</b> ⚡",
        "⚡🔥 <b>KA... ME...</b> 🔥⚡",
        "⚡🔥 <b>HA... ME...</b> 🔥⚡",
        "⚡🔥💥 <b>HAAAAAAA !!!!!!!</b> 💥🔥⚡\n\n═════════════💥💥💥💥💥",
        "✨ <b>SUPER SAIYAN POWER LEVEL: OVER 9000!</b> ✨"
    ]
    await animate(message, frames, delay=0.6)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 3D PULSATING HEART (.heart, .love)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["heart", "love"], prefixes=".") & filters.me)
async def heart_anim(client: Client, message: Message):
    frames = [
        "🤍",
        "🤎",
        "💜",
        "💙",
        "💚",
        "💛",
        "🧡",
        "❤️",
        "💖 <i>Lub...</i>",
        "💓 <i>Dub...</i>",
        "💗 <i>Lub-Dub...</i>",
        "💘 <b>I LOVE YOU TO THE MOON & BACK!</b> 💝"
    ]
    await animate(message, frames, delay=0.4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. THANOS GAUNTLET SNAP (.thanos, .snap)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["thanos", "snap"], prefixes=".") & filters.me)
async def thanos_anim(client: Client, message: Message):
    frames = [
        "🧤 <i>Gathering the 6 Infinity Stones...</i>",
        "🧤💎 Power Stone [OK]",
        "🧤💎💎 Space & Reality Stones [OK]",
        "🧤💎💎💎 Soul, Time & Mind Stones [OK]",
        "✨ <b>I am... Inevitable.</b>",
        "💥 <b>*SNAP*</b> 🫰",
        "💨 . . : : : : : : : :",
        "💨 . . . . . . . . . .",
        "✨ <i>Half of the universe disintegrated into dust.</i>"
    ]
    await animate(message, frames, delay=0.8)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. RETRO SNAKE GAME (.snake)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("snake", prefixes=".") & filters.me)
async def snake_anim(client: Client, message: Message):
    frames = [
        "<code>[ 🐍  ◽  ◽  🍎 ]</code>",
        "<code>[ ◽  🐍  ◽  🍎 ]</code>",
        "<code>[ ◽  ◽  🐍  🍎 ]</code>",
        "<code>[ ◽  ◽  ◽  🐍💥 ]</code>",
        "<code>[ ◽  ◽  ◽  🐍✨ ] SCORE: +100</code>"
    ]
    await animate(message, frames, delay=0.5, delete_after=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. SNIPER 360 NO-SCOPE (.sniper, .kill, .shoot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["sniper", "kill", "shoot"], prefixes=".") & filters.me)
async def sniper_anim(client: Client, message: Message):
    frames = [
        "🎯 <i>Locking on target...</i>",
        "🎯 <b>Target Spotted: 800m away</b>",
        "🎯 <i>Adjusting for wind velocity...</i>",
        "🔫 <b>3... 2... 1...</b>",
        "💥 <b>BOOOOOM! HEADSHOT!</b> 🩸",
        "☠️ <b>Target Neutralized!</b>"
    ]
    await animate(message, frames, delay=0.6)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. RAINSTORM & LIGHTNING (.rain, .storm)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["rain", "storm"], prefixes=".") & filters.me)
async def storm_anim(client: Client, message: Message):
    frames = [
        "☁️ <i>Clouds rolling in...</i>",
        "☁️☁️ <i>Sky turns dark...</i>",
        "🌧️ <i>Drizzle starts falling...</i>",
        "🌧️🌧️ <i>Heavy downpour!</i>",
        "⛈️ <b>*THUNDER ROARS*</b> ⚡⚡",
        "⚡⚡💥 <b>CRACCCCK! LIGHTNING STRIKE!</b> 💥⚡⚡",
        "🌈 <i>Storm passes... Rainbow appears.</i> 🌤️"
    ]
    await animate(message, frames, delay=0.7)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. POLICE SIREN ALERT (.police, .siren)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["police", "siren"], prefixes=".") & filters.me)
async def police_anim(client: Client, message: Message):
    frames = [
        "🔴 <b>WEE</b> 🔵 <b>WOO</b> 🔴 <b>WEE</b> 🔵 <b>WOO</b>",
        "🔵 <b>WEE</b> 🔴 <b>WOO</b> 🔵 <b>WEE</b> 🔴 <b>WOO</b>",
        "🔴 <b>WEE</b> 🔵 <b>WOO</b> 🔴 <b>WEE</b> 🔵 <b>WOO</b>",
        "🚓 <b>PULL OVER! TELEGRAM POLICE ON THE SCENE!</b> 🚨",
        "👮‍♂️ <i>You are under arrest for being too awesome!</i>"
    ]
    await animate(message, frames, delay=0.5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. CASINO 777 SLOT MACHINE (.slot, .jackpot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["slot", "jackpot"], prefixes=".") & filters.me)
async def slot_anim(client: Client, message: Message):
    frames = [
        "🎰 <b>[ 🍇 | 🍋 | 🔔 ]</b> <i>Spinning...</i>",
        "🎰 <b>[ 🍒 | 🍒 | 🍇 ]</b> <i>Spinning...</i>",
        "🎰 <b>[ 💎 | 7️⃣ | 🍒 ]</b> <i>Spinning...</i>",
        "🎰 <b>[ 7️⃣ | 7️⃣ | 7️⃣ ]</b> 🔥🔥🔥",
        "🎉💰 <b>JACKPOT! YOU WON 1,000,000 TELEGRAM COINS!</b> 💰🎉"
    ]
    await animate(message, frames, delay=0.5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. 3D DICE ROLL (.dice)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("dice", prefixes=".") & filters.me)
async def dice_anim(client: Client, message: Message):
    frames = ["🎲 <i>Shaking dice cup...</i>", "🎲 ⚀", "🎲 ⚂", "🎲 ⚄", "🎲 ⚅", "🎯 <b>LUCKY ROLL: 6!</b> 🏆"]
    await animate(message, frames, delay=0.4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. JUMPING DINO GAME (.dino)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("dino", prefixes=".") & filters.me)
async def dino_anim(client: Client, message: Message):
    frames = [
        "🦖\n\n          🌵",
        "🦖\n\n      🌵",
        "   🦖 (JUMP!)\n\n  🌵",
        "🦖\n\n  🌵",
        "🦖\n\n      🌵",
        "🦖 🏆 <b>STAGE CLEARED!</b>"
    ]
    await animate(message, frames, delay=0.5, delete_after=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 13. WIZARD MAGIC SPELL (.magic, .spell)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["magic", "spell"], prefixes=".") & filters.me)
async def magic_anim(client: Client, message: Message):
    frames = [
        "🪄 <i>Casting Ancient Spell...</i>",
        "🪄✨ <i>Sparkles glowing...</i>",
        "🪄✨🌟 <i>Mana charging to max...</i>",
        "🪄🔮💥 <b>ABRACADABRA ALAKAZAM!</b> 💥🔮🪄",
        "🕊️ <i>Poof! Everything is magical now.</i> ✨"
    ]
    await animate(message, frames, delay=0.6)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 14. HACK SEQUENCE (.hack)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("hack", prefixes=".") & filters.me)
async def hack_anim(client: Client, message: Message):
    frames = [
        "🟢 <b>Initializing Infiltration Protocol...</b>",
        "⏳ <code>Connecting to Telegram Main Server...</code>",
        "⏳ <code>Cracking 2FA Multi-Factor Tokens...</code>",
        "⏳ <code>Extracting Encrypted Database...</code>",
        "⏳ [█▒▒▒▒▒▒▒▒▒] 10%",
        "⏳ [████▒▒▒▒▒▒] 45%",
        "⏳ [████████▒▒] 80%",
        "⏳ [██████████] 100%",
        "✅ <b>HACK SUCCESSFUL!</b>\n<code>User data routed to Saved Messages.</code>"
    ]
    await animate(message, frames, delay=0.8)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 15. BRAIN SCANNER (.brain)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("brain", prefixes=".") & filters.me)
async def brain_anim(client: Client, message: Message):
    frames = [
        "🧠 <b>Initializing Neural Scan...</b>",
        "🧠 <code>Processing Quantum Thought Vectors...</code>",
        "🧠 <code>Analyzing IQ Level...</code>",
        "❌ <b>Error 404: Brain Not Found in Target!</b>",
        "🤖 <i>Defaulting to automated robot responses.</i>"
    ]
    await animate(message, frames, delay=0.8)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 16. KISS (.kiss), FUCK (.fuck), ROCKET (.rocket), HELICOPTER (.helikopter)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("kiss", prefixes=".") & filters.me)
async def kiss_anim(client: Client, message: Message):
    frames = ["😗", "😙", "😚", "😘", "💋 <b>Mwaaah! Sent with love!</b> 💜"]
    await animate(message, frames, delay=0.4)

@Client.on_message(filters.command("fuck", prefixes=".") & filters.me)
async def fuck_anim(client: Client, message: Message):
    frames = [
        "╭━━━━━━━━━━━━━━━╮\n┃      🖕      ┃\n╰━━━━━━━━━━━━━━━╯",
        "╭━━━━━━━━━━━━━━━╮\n┃     🖕🖕     ┃\n╰━━━━━━━━━━━━━━━╯",
        "╭━━━━━━━━━━━━━━━╮\n┃    🖕🖕🖕    ┃\n╰━━━━━━━━━━━━━━━╯",
        "╭━━━━━━━━━━━━━━━╮\n┃   𝗙𝗨𝗖𝗞 𝗢𝗙𝗙   ┃\n╰━━━━━━━━━━━━━━━╯"
    ]
    await animate(message, frames, delay=0.7)

@Client.on_message(filters.command("rocket", prefixes=".") & filters.me)
async def rocket_anim(client: Client, message: Message):
    frames = [
        "🚀 <i>3...</i>",
        "🚀 <i>2...</i>",
        "🚀 <i>1...</i>",
        "🔥🚀 <b>LIFTOFF!</b>",
        "      🚀\n   ☁️☁️\n  🔥🔥",
        "            🚀 ✨ <b>TO INFINITY AND BEYOND!</b> ✨"
    ]
    await animate(message, frames, delay=0.5)

@Client.on_message(filters.command("helikopter", prefixes=".") & filters.me)
async def heli_anim(client: Client, message: Message):
    frames = ["🚁 <i>Helikopter...</i>", "🚁 <i>Helikopter Helikopter!</i>", "🚁💨", "🚁💨💨💨"]
    await animate(message, frames, delay=0.4, delete_after=True)
