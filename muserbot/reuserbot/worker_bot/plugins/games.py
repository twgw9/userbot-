"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/games.py — Interactive Games & Roleplay Arcade   ║
║  Features:                                               ║
║    • .truth & .dare (Interactive party games)            ║
║    • .toss & .coin (3D Animated coin flip)               ║
║    • .roll <number> (Random number lottery)              ║
║    • .slap, .pat, .hug, .punch (Fun roleplay actions)    ║
╚═══════════════════════════════════════════════════════════╝
"""

import random
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

TRUTHS = [
    "What is the most embarrassing thing you've done on Telegram? 🙈",
    "Have you ever stalked someone's profile for hours without messaging? 🕵️‍♂️",
    "What is your biggest secret that nobody in this chat knows? 🤫",
    "If you could delete one person from this group permanently, who would it be? 💀",
    "What is the biggest lie you’ve ever told someone with a straight face? 🤥",
    "Who in this group do you secretly admire or have a crush on? ❤️",
    "Have you ever screenshotted a private chat and sent it to someone else? 📸"
]

DARES = [
    "Send a voice note singing the chorus of your favorite song right now! 🎤",
    "Change your Telegram bio to 'I am obsessed with MUserBot' for 2 hours! 🤖",
    "Send the 5th photo in your phone gallery to the group without explaining! 🖼️",
    "Text your crush or ex 'I still remember what you did' and screenshot the reply! 💬",
    "Call someone on Telegram and speak only in an alien accent for 1 minute! 👽",
    "Send a message in ALL CAPS for the next 15 minutes! 🔥"
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. TRUTH & DARE (.truth, .dare)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("truth", prefixes=".") & filters.me)
async def truth_cmd(client: Client, message: Message):
    question = random.choice(TRUTHS)
    await message.edit_text(f"🎲 <b>TRUTH TIME!</b>\n\n<i>{question}</i>\n\n👉 <i>Answer honestly in chat!</i>")

@Client.on_message(filters.command("dare", prefixes=".") & filters.me)
async def dare_cmd(client: Client, message: Message):
    challenge = random.choice(DARES)
    await message.edit_text(f"🔥 <b>DARE ACCEPTED!</b>\n\n<b>Challenge:</b> <i>{challenge}</i>\n\n👉 <i>You have 5 minutes to complete it!</i>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 3D COIN FLIP (.toss, .coin)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["toss", "coin"], prefixes=".") & filters.me)
async def coin_toss_cmd(client: Client, message: Message):
    await message.edit_text("🪙 <i>Flipping coin high into the air...</i>")
    await asyncio.sleep(0.5)
    await message.edit_text("🪙 <i>Spinning... 💫</i>")
    await asyncio.sleep(0.5)
    
    result = random.choice(["HEADS 👑", "TAILS 🦅"])
    await message.edit_text(f"🪙 <b>Coin Landed:</b> <code>{result}</code>!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. RANDOM LOTTERY ROLL (.roll <max>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("roll", prefixes=".") & filters.me)
async def roll_cmd(client: Client, message: Message):
    max_num = 100
    if len(message.command) >= 2 and message.command[1].isdigit():
        max_num = int(message.command[1])
        
    num = random.randint(1, max_num)
    await message.edit_text(f"🎲 <b>Rolling between 1 and {max_num}...</b>\n\n🎯 <b>Landed On:</b> <code>{num}</code>!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. FUN ROLEPLAY ACTIONS (.slap, .pat, .hug, .punch)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_target_name(message: Message) -> str:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.first_name
    if len(message.command) >= 2:
        return message.text.split(" ", 1)[1]
    return "Someone"

@Client.on_message(filters.command("slap", prefixes=".") & filters.me)
async def slap_cmd(client: Client, message: Message):
    target = get_target_name(message)
    slaps = [
        f"🖐️ *SLAAAAAP!* Gave a thunderous supersonic slap to <b>{target}</b>! 💥",
        f"🐟 Picked up a giant wet fish and smacked <b>{target}</b> across the face! 🌊",
        f"🏏 Swung a cricket bat and sent <b>{target}</b> flying into the stratosphere! 🚀"
    ]
    await message.edit_text(random.choice(slaps))

@Client.on_message(filters.command("hug", prefixes=".") & filters.me)
async def hug_cmd(client: Client, message: Message):
    target = get_target_name(message)
    await message.edit_text(f"🤗 <i>Gave a warm, cozy, comforting bear hug to</i> <b>{target}</b>! 💖✨")

@Client.on_message(filters.command("pat", prefixes=".") & filters.me)
async def pat_cmd(client: Client, message: Message):
    target = get_target_name(message)
    await message.edit_text(f"🥰 <i>Gently pats</i> <b>{target}</b> <i>on the head. 'There there, good job!'</i> 🌸")

@Client.on_message(filters.command("punch", prefixes=".") & filters.me)
async def punch_cmd(client: Client, message: Message):
    target = get_target_name(message)
    await message.edit_text(f"🥊 <b>K.O.!</b> Landed a devastating One-Inch Punch right into <b>{target}'s</b> stomach! 💥💀")
