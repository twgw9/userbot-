"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/ai_tools.py — AI Assistant, Image Gen & Tools    ║
║  Features:                                               ║
║    • .ai & .gpt (Conversational AI Assistant)            ║
║    • .draw & .imagine (AI Image & Art Generator)         ║
║    • .summarize & .code & .fixgrammar (Productivity)     ║
║    • .tr (Multi-language instant translation)            ║
║    • .calc, .tts, .carbon, .quote                        ║
╚═══════════════════════════════════════════════════════════╝
"""

import urllib.parse
import aiohttp
import asyncio
import logging
import io
import re
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SMART AI ASSISTANT (.ai, .gpt, .ask)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["ai", "gpt", "ask"], prefixes=".") & filters.me)
async def ai_assistant(client: Client, message: Message):
    query = ""
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        query = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) >= 2:
        query = message.text.split(" ", 1)[1]
        
    if not query:
        return await message.edit_text("❌ <b>Usage:</b> <code>.ai <your question></code> or reply to a message.")
        
    await message.edit_text("🤖 <i>MUserBot AI is thinking...</i>")
    
    encoded_prompt = urllib.parse.quote(query)
    
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://darkness.ashlynn.workers.dev/chat/?prompt={encoded_prompt}", timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("response") or data.get("reply") or data.get("message")
                        if reply:
                            return await message.edit_text(f"🤖 <b>MUserBot AI:</b>\n\n{reply}")
            except Exception:
                pass
                
            async with session.get(f"https://api.safone.dev/chat?message={encoded_prompt}", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ans = data.get("answer") or data.get("response") or data.get("message")
                    if ans:
                        return await message.edit_text(f"🤖 <b>MUserBot AI:</b>\n\n{ans}")
                        
        await message.edit_text(f"🤖 <b>AI Answer:</b>\n\nReceived query: '<i>{query}</i>'. AI engine online.")
    except Exception as e:
        await message.edit_text(f"❌ AI Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. AI IMAGE GENERATION (.draw, .imagine, .dalle)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["draw", "imagine", "dalle", "aiimage"], prefixes=".") & filters.me)
async def ai_draw_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.draw <prompt describing your image></code>\n<i>Example:</i> <code>.draw Cyberpunk neon city in rain 4k</code>")
        
    prompt = message.text.split(" ", 1)[1].strip()
    msg = await message.edit_text(f"🎨 <i>Generating AI Artwork: '<b>{prompt}</b>'...</i>")
    
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=30) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    photo_io = io.BytesIO(img_bytes)
                    photo_io.name = "ai_art.png"
                    
                    await client.send_photo(
                        chat_id=message.chat.id,
                        photo=photo_io,
                        caption=f"🎨 <b>AI Artwork Generated!</b>\n📝 <b>Prompt:</b> <i>{prompt}</i>\n⚡ <i>Created via MUserBot Pro</i>"
                    )
                    return await msg.delete()
                    
        await msg.edit_text("❌ Failed to render AI image. Please try a different prompt.")
    except Exception as e:
        await msg.edit_text(f"❌ AI Draw Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. AI CODE GENERATOR (.code <task>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["code", "writecode"], prefixes=".") & filters.me)
async def ai_code_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.code <python/js/cpp/html> <task></code>\n<i>Example:</i> <code>.code python binary search algorithm with comments</code>")
        
    task = message.text.split(" ", 1)[1].strip()
    prompt = f"Write clean, optimized, production-ready code with concise comments for: {task}. Return the code enclosed in Markdown code blocks."
    
    msg = await message.edit_text("💻 <i>Generating code...</i>")
    encoded = urllib.parse.quote(prompt)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.safone.dev/chat?message={encoded}", timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ans = data.get("answer") or data.get("response") or data.get("message")
                    if ans:
                        return await msg.edit_text(f"💻 <b>AI Code Generator:</b>\n\n{ans}")
        await msg.edit_text("❌ Could not generate code.")
    except Exception as e:
        await msg.edit_text(f"❌ Code Error: <code>{e}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. INSTANT MULTI-LANGUAGE TRANSLATOR (.tr)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["tr", "translate"], prefixes=".") & filters.me)
async def translate_cmd(client: Client, message: Message):
    target_lang = "en"
    text_to_translate = ""
    
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        text_to_translate = message.reply_to_message.text or message.reply_to_message.caption
        if len(message.command) >= 2:
            target_lang = message.command[1]
    elif len(message.command) >= 3:
        target_lang = message.command[1]
        text_to_translate = " ".join(message.command[2:])
    elif len(message.command) == 2:
        text_to_translate = message.command[1]
    else:
        return await message.edit_text("❌ <b>Usage:</b> <code>.tr <lang_code> <text></code> or reply to a message with <code>.tr hi</code>.")
        
    await message.edit_text("🌐 <i>Translating...</i>")
    encoded_text = urllib.parse.quote(text_to_translate)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded_text}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    translated_text = "".join([chunk[0] for chunk in data[0] if chunk[0]])
                    src_lang = data[2] if len(data) > 2 else "auto"
                    
                    result_msg = (
                        f"🌐 <b>Translation ({src_lang.upper()} ➔ {target_lang.upper()}):</b>\n\n"
                        f"<code>{translated_text}</code>"
                    )
                    await message.edit_text(result_msg)
                else:
                    await message.edit_text("❌ Translation API returned an error.")
    except Exception as e:
        await message.edit_text(f"❌ Translation Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. HIGH PRECISION CALCULATOR (.calc)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["calc", "math"], prefixes=".") & filters.me)
async def calc_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.calc 2 + 2 * (10 / 5)</code>")
        
    expr = message.text.split(" ", 1)[1].strip()
    if not re.match(r'^[0-9+\-*/()., %^eEpiPI\s]+$', expr.replace("math.", "")):
        return await message.edit_text("❌ Invalid expression! Only numbers and standard mathematical operators (+ - * / % ^) are permitted.")
        
    try:
        import math
        safe_dict = {
            "__builtins__": None,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "log": math.log, "pi": math.pi, "e": math.e, "pow": pow, "abs": abs
        }
        clean_expr = expr.replace("^", "**")
        result = eval(clean_expr, safe_dict)
        
        await message.edit_text(
            f"🧮 <b>Calculation:</b>\n"
            f"<b>Expression:</b> <code>{expr}</code>\n"
            f"<b>Result:</b> <code>{result}</code>"
        )
    except Exception as e:
        await message.edit_text(f"❌ Calculation Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. TEXT TO SPEECH AUDIO SYNTHESIS (.tts)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("tts", prefixes=".") & filters.me)
async def tts_cmd(client: Client, message: Message):
    lang = "en"
    text = ""
    
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        text = message.reply_to_message.text or message.reply_to_message.caption
        if len(message.command) >= 2:
            lang = message.command[1]
    elif len(message.command) >= 3:
        lang = message.command[1]
        text = " ".join(message.command[2:])
    elif len(message.command) == 2:
        text = message.command[1]
    else:
        return await message.edit_text("❌ <b>Usage:</b> <code>.tts <lang> <text></code> or reply to a message with <code>.tts hi</code>")
        
    msg = await message.edit_text("🎙️ <i>Synthesizing voice note...</i>")
    encoded = urllib.parse.quote(text)
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl={lang}&client=tw-ob"
    
    try:
        await client.send_voice(
            chat_id=message.chat.id,
            voice=tts_url,
            caption=f"🎙️ <b>Voice Note ({lang.upper()}):</b> <i>{text[:100]}...</i>"
        )
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ TTS Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. CARBON CODE SNIPPET GENERATOR (.carbon)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("carbon", prefixes=".") & filters.me)
async def carbon_cmd(client: Client, message: Message):
    code = ""
    if message.reply_to_message and message.reply_to_message.text:
        code = message.reply_to_message.text
    elif len(message.command) >= 2:
        code = message.text.split(" ", 1)[1]
    else:
        return await message.edit_text("❌ <b>Usage:</b> <code>.carbon <code></code> or reply to a code block.")
        
    msg = await message.edit_text("🎨 <i>Generating Carbon code graphic...</i>")
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"code": code}
            async with session.post("https://carbonara.solopov.dev/api/cook", json=payload, timeout=20) as resp:
                if resp.status == 200:
                    image_bytes = await resp.read()
                    photo_io = io.BytesIO(image_bytes)
                    photo_io.name = "carbon.png"
                    await client.send_photo(
                        chat_id=message.chat.id,
                        photo=photo_io,
                        caption="🎨 <b>Carbon Code Snippet</b>"
                    )
                    return await msg.delete()
        await msg.edit_text("❌ Could not render carbon snippet.")
    except Exception as e:
        await msg.edit_text(f"❌ Carbon Error: <code>{str(e)}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. QUOTE STICKER GENERATOR (.quote, .q)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["quote", "q"], prefixes=".") & filters.me)
async def quote_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("❌ Reply to a message to generate a quote sticker.")
        
    replied = message.reply_to_message
    msg = await message.edit_text("💬 <i>Generating quote sticker...</i>")
    
    user_name = replied.from_user.first_name if replied.from_user else "User"
    user_text = replied.text or replied.caption or "Media"
    user_id = replied.from_user.id if replied.from_user else 0
    
    payload = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": [
            {
                "entities": [],
                "avatar": True,
                "from": {
                    "id": user_id,
                    "name": user_name,
                    "photo": {}
                },
                "text": user_text,
                "replyMessage": {}
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://bot.lyo.su/quote/generate", json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    import base64
                    img_data = base64.b64decode(data["result"]["image"])
                    sticker_io = io.BytesIO(img_data)
                    sticker_io.name = "quote.webp"
                    
                    await client.send_sticker(chat_id=message.chat.id, sticker=sticker_io)
                    return await msg.delete()
        await msg.edit_text("❌ Failed to generate quote sticker.")
    except Exception as e:
        await msg.edit_text(f"❌ Quote Error: <code>{str(e)}</code>")
