"""
╔═══════════════════════════════════════════════════════════╗
║  worker_globals.py — Worker Userbot Global States         ║
║  Tracks active spam/raid tasks, AFK state, PM guard data  ║
╚═══════════════════════════════════════════════════════════╝
"""

import time

# Active Spam/Raid tasks tracker: {chat_id: True/False}
ACTIVE_TASKS = {}

# Active Tagall tasks tracker: {chat_id: "task_type"}
ACTIVE_TAGS = {}

# View Once auto-save & last chat reference
LAST_CHAT_ID = None

# Saved stickers cache for .gspam
SAVED_STICKERS = []

# AFK state tracker: {"afk": bool, "reason": str, "time": float, "mentions": list}
AFK_DATA = {
    "is_afk": False,
    "reason": "",
    "time": 0,
    "mentions": []
}

# Bot start time for uptime tracking
START_TIME = time.time()

def stop_task(chat_id: int):
    """Chat me chal rahe spam/raid ko stop karna"""
    ACTIVE_TASKS[chat_id] = False

def start_task(chat_id: int):
    """Naya spam/raid task register karna"""
    ACTIVE_TASKS[chat_id] = True

def is_task_active(chat_id: int) -> bool:
    """Task active hai ya stop ho gaya check karna"""
    return ACTIVE_TASKS.get(chat_id, False)

def stop_all_chat_tasks():
    """Globally saare active tasks stop karna"""
    for k in list(ACTIVE_TASKS.keys()):
        ACTIVE_TASKS[k] = False
    for k in list(ACTIVE_TAGS.keys()):
        ACTIVE_TAGS.pop(k, None)
