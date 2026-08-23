"""
╔═══════════════════════════════════════════════════════════╗
║  plugins/notes.py — Quick Reply Notes Vault               ║
║  Features:                                               ║
║    • .save <key> (Save text or replied media note)       ║
║    • .get <key> (Instantly send saved note)              ║
║    • .delnote <key> (Delete specific note)               ║
║    • .notes (List all saved notes)                       ║
║    • .clearnotes (Delete all notes)                      ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

NOTES_FILE = "saved_notes.json"

def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_notes(data: dict):
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing notes file: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SAVE NOTE (.save <key> [text])
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["save", "savenote"], prefixes=".") & filters.me)
async def save_note_cmd(client: Client, message: Message):
    parts = message.text.split(" ", 2)
    if len(parts) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.save <key> <text></code> or reply to a message with <code>.save <key></code>")
        
    key = parts[1].lower().strip()
    note_content = parts[2].strip() if len(parts) > 2 else ""
    
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.text:
            note_content = replied.text
        elif replied.caption:
            note_content = replied.caption
            
    if not note_content:
        return await message.edit_text("❌ Note content cannot be empty!")
        
    notes = load_notes()
    notes[key] = note_content
    save_notes(notes)
    
    await message.edit_text(f"✅ <b>Note Saved!</b>\nTrigger: <code>.get {key}</code>")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. GET NOTE (.get <key>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["get", "note"], prefixes=".") & filters.me)
async def get_note_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.get <key></code>")
        
    key = message.command[1].lower().strip()
    notes = load_notes()
    
    if key not in notes:
        return await message.edit_text(f"❌ No note found with key: <code>{key}</code>")
        
    content = notes[key]
    await message.edit_text(content)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. DELETE NOTE (.delnote <key>)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command(["delnote", "dnote"], prefixes=".") & filters.me)
async def del_note_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("❌ <b>Usage:</b> <code>.delnote <key></code>")
        
    key = message.command[1].lower().strip()
    notes = load_notes()
    
    if key in notes:
        del notes[key]
        save_notes(notes)
        await message.edit_text(f"🗑️ Note <code>{key}</code> deleted successfully.")
    else:
        await message.edit_text(f"❌ Note <code>{key}</code> does not exist.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. LIST ALL NOTES (.notes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("notes", prefixes=".") & filters.me)
async def list_notes_cmd(client: Client, message: Message):
    notes = load_notes()
    if not notes:
        return await message.edit_text("ℹ️ You have no saved notes yet. Use <code>.save <key> <text></code> to create one.")
        
    text = f"📝 <b>Saved Notes ({len(notes)}):</b>\n\n"
    for k in notes.keys():
        text += f"• <code>.get {k}</code>\n"
    await message.edit_text(text)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. CLEAR ALL NOTES (.clearnotes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("clearnotes", prefixes=".") & filters.me)
async def clear_notes_cmd(client: Client, message: Message):
    save_notes({})
    await message.edit_text("🗑️ <b>All saved notes cleared!</b>")
