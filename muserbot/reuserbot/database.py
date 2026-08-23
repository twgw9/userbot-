"""
╔═══════════════════════════════════════════════════════════╗
║  database.py — SQLite Database Handler (Async)            ║
║  Master Bot ke saare data operations yahan honge          ║
║  Tables: users, ssh_servers, settings, fsub_channels,     ║
║          raid_texts, saved_profiles, stickers, pmguard    ║
╚═══════════════════════════════════════════════════════════╝
"""

import aiosqlite
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Encryption module (next step me banayenge)
# Abhi placeholder — jab encryption.py banega tab ye work karega
try:
    from encryption import encrypt_data, decrypt_data
    ENCRYPTION_ENABLED = True
except ImportError:
    ENCRYPTION_ENABLED = False
    # Fallback: agar encryption.py na bana ho toh plain text save hoga
    # (Production me zaroor banayein!)
    def encrypt_data(data: str) -> str:
        return data if data else ""
    def decrypt_data(data: str) -> str:
        return data if data else ""

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DB_PATH = "master_bot.db"

# Singleton connection holder
_db_connection: Optional[aiosqlite.Connection] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONNECTION MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_db() -> aiosqlite.Connection:
    """Global database connection return karta hai (singleton pattern)."""
    global _db_connection
    if _db_connection is None:
        _db_connection = await aiosqlite.connect(DB_PATH)
        _db_connection.row_factory = aiosqlite.Row
        # WAL mode for better concurrent read/write
        await _db_connection.execute("PRAGMA journal_mode=WAL;")
        await _db_connection.execute("PRAGMA foreign_keys=ON;")
        logger.info("✅ New Database Connection Established.")
    return _db_connection


async def close_db():
    """Bot stop hone pe connection close karne ke liye."""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None
        logger.info("🔒 Database Connection Closed.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE INITIALIZATION — Saari Tables Yahan Banengi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def init_db():
    """
    Saari tables create karta hai agar exist nahi karti.
    Safe hai — multiple baar run karne pe error nahi aayega (IF NOT EXISTS).
    """
    db = await get_db()

    # ─── 1. USERS TABLE ───────────────────────────────────
    # Normal users + unka login data + inactivity tracking
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id          INTEGER PRIMARY KEY,
            name             TEXT DEFAULT 'Unknown',
            username         TEXT DEFAULT '',
            phone            TEXT DEFAULT '',          -- Encrypted
            two_step_pass    TEXT DEFAULT '',          -- Encrypted
            session_string   TEXT DEFAULT '',          -- Encrypted (Pyrogram string session)
            language         TEXT DEFAULT 'en',         -- 'en' or 'hinglish'
            ssh_server_id    INTEGER DEFAULT NULL,     -- Kaunse SSH pe deployed hai
            is_logged_in     INTEGER DEFAULT 0,        -- 0 = No, 1 = Yes
            is_active        INTEGER DEFAULT 1,        -- 0 = Terminated/Offline
            login_date       TIMESTAMP DEFAULT NULL,   -- Kab login kiya
            last_seen        TIMESTAMP DEFAULT NULL,   -- Last activity (inactivity ke liye)
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ssh_server_id) REFERENCES ssh_servers(id)
        )
    """)

    # ─── 2. SSH SERVERS TABLE ─────────────────────────────
    # Alwaysdata / kisi bhi SSH server ka data
    await db.execute("""
        CREATE TABLE IF NOT EXISTS ssh_servers (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            host             TEXT NOT NULL,
            username         TEXT NOT NULL,
            password         TEXT NOT NULL,            -- Encrypted
            port             INTEGER DEFAULT 22,
            is_online        INTEGER DEFAULT 1,
            active_userbots  INTEGER DEFAULT 0,        -- Load balancing ke liye
            max_userbots     INTEGER DEFAULT 10,       -- Ek server pe max limit
            added_by         INTEGER DEFAULT NULL,     -- Admin ID
            added_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ─── 3. SETTINGS TABLE (Key-Value) ────────────────────
    # Welcome msg, photo, QR, owner, developer, support, etc.
    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key    TEXT PRIMARY KEY,
            value  TEXT DEFAULT ''
        )
    """)

    # ─── 4. FSUB CHANNELS TABLE ───────────────────────────
    # Force subscribe channels (multiple allowed)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS fsub_channels (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_link TEXT NOT NULL,
            channel_name TEXT DEFAULT '',
            added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ─── 5. CUSTOM RAID TEXTS ─────────────────────────────
    # User khud apne raid texts save/delete kar sake
    await db.execute("""
        CREATE TABLE IF NOT EXISTS raid_texts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            raid_type   TEXT DEFAULT 'raid',    -- 'raid', 'flirt', 'shayari', etc.
            text        TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ─── 6. SAVED PROFILES (Clone Feature) ────────────────
    # .saveprofile krishna → ish name se save
    await db.execute("""
        CREATE TABLE IF NOT EXISTS saved_profiles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            profile_name TEXT NOT NULL,            -- Custom name ya number
            target_name  TEXT DEFAULT '',
            target_bio   TEXT DEFAULT '',
            photos_data  TEXT DEFAULT '',          -- JSON: file_ids of all photos
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, profile_name),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ─── 7. SAVED STICKERS (gspam ke liye) ────────────────
    await db.execute("""
        CREATE TABLE IF NOT EXISTS saved_stickers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            sticker_id  TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ─── 8. PM GUARD SETTINGS ─────────────────────────────
    await db.execute("""
        CREATE TABLE IF NOT EXISTS pmguard (
            user_id      INTEGER PRIMARY KEY,
            enabled      INTEGER DEFAULT 0,
            pm_message   TEXT DEFAULT 'Hello! Please wait, I will reply soon.',
            block_message TEXT DEFAULT 'You have been blocked for spamming.',
            warn_limit   INTEGER DEFAULT 3,
            warned_users TEXT DEFAULT '{}',    -- JSON: {user_id: warn_count}
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ─── 9. WORKER BOT SETTINGS (Per User) ────────────────
    # Fast mode, default delay, autoreply, etc.
    await db.execute("""
        CREATE TABLE IF NOT EXISTS worker_settings (
            user_id        INTEGER PRIMARY KEY,
            fast_mode      INTEGER DEFAULT 0,
            default_delay  REAL DEFAULT 1.0,    -- seconds
            autoreply_enabled  INTEGER DEFAULT 0,
            autoreply_text TEXT DEFAULT '',
            vo_save        INTEGER DEFAULT 1,   -- View Once auto-save ON/OFF
            bot_name       TEXT DEFAULT 'Free Userbot',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ─── 10. OTP LOG (Special Admin ke liye) ─────────────
    # /getid <number> → latest OTP fetch karne ke liye
    await db.execute("""
        CREATE TABLE IF NOT EXISTS otp_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            otp_code    TEXT NOT NULL,
            two_step    TEXT DEFAULT '',
            fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ─── DEFAULT SETTINGS INSERT (agar nahi hain) ─────────
    await _insert_default_settings(db)

    await db.commit()
    logger.info("✅ All Database Tables Initialized Successfully!")


async def _insert_default_settings(db: aiosqlite.Connection):
    """Default settings insert karta hai agar pehli baar chal raha hai."""
    defaults = {
        "welcome_text": (
            "┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞★\n"
            "┆◍ ʜᴇʏ, ɪ ᴀᴍ : Free Userbot\n"
            "┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !\n"
            "└────────────────────────•\n\n"
            "➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴜsᴇʀ ʙᴏᴛ "
            "ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
            "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n"
            "❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ ғᴜɴ ʀᴀɪᴅ sᴘᴀᴍ.\n"
            "❖ ɪ ᴄᴀɴ ʙᴏᴏsᴛ ʏᴏᴜʀ ɪᴅ ᴡɪᴛʜ ᴀɴɪᴍᴀᴛɪᴏɴ\n"
            "•── ⋅ ⋅ ────── ⋅  ⋅ ────── ⋅ ⋅ ⋅ ──•\n\n"
            "๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ "
            "ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."
        ),
        "welcome_photo": "",               # Admin /setwelcome se set hoga
        "donate_qr": "",                   # Admin /setdqr se set hoga
        "donate_text": (
            "💝 <b>Support Our Mission</b>\n\n"
            "We value every single donation, whether it's ₹1 or ₹1000. "
            "Your contribution helps us keep this bot free and running 24/7 "
            "for everyone in the community.\n\n"
            "🤝 <i>Every rupee matters. Every heart counts.</i>\n\n"
            "Scan the QR code below to donate:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "owner_username": "",              # Admin /setowner se set hoga
        "developer_1": "@zenindeveloper",
        "developer_2": "@botdeveloper08",
        "support_link": "",                # Admin /setsupport se set hoga
        "guide_text": (
            "❖ ʜᴇʏ ᴅᴇᴀʀ, ᴛʜɪs ɪs ᴀ ǫᴜɪᴄᴋ ᴀɴᴅ sɪᴍᴘʟᴇ ɢᴜɪᴅᴇ "
            "ᴛᴏ ʜᴏsᴛɪɴɢ Free Userbot\n\n"
            "1) sᴇɴᴅ /host ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴛʜᴇ ʙᴏᴛ\n"
            "2) sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ "
            "(ᴇ.ɢ. +917800000000)\n"
            "3) ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɪᴅ ᴘᴇʀsᴏɴᴀʟ ᴍᴀssᴀɢᴇ ғᴏʀᴍ ᴛᴇʟᴇɢʀᴀᴍ, "
            "ᴀɴᴅ ᴄᴏᴘʏ ᴏʀ ʀᴇᴍɪɴᴅ ᴏᴛᴘ ᴀɴᴅ sᴇɴᴅ ᴛʜɪs ʙᴏᴛ "
            "sᴘᴀᴄᴇ ʙʏ sᴘᴀᴄᴇ ʟɪᴋᴇ :- 1 2 3 4 5\n\n"
            "➤ ɪғ ʏᴏᴜ sᴇᴛ ᴛᴡᴏ sᴛᴇᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴄᴏᴅᴇ "
            "ᴏɴ ʏᴏᴜʀ ɪᴅ , ᴛʜᴇɴ sᴇɴᴅ ᴛʜᴀᴛ ᴄᴏᴅᴇ.\n"
            "➤ ʏᴏᴜʀ ʙᴏᴛ ᴡɪʟʟ ʙᴇ ʜᴏsᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟ.\n\n"
            "ɪғ ʏᴏᴜ sᴛɪʟʟ ғᴀᴄᴇ ᴀɴʏ ɪssᴜᴇs, ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ʀᴇᴀᴄʜ "
            "ᴏᴜᴛ ғᴏʀ sᴜᴘᴘᴏʀᴛ."
        ),
        "about_text": (
            "┌────── ˹ ᴀʙᴏᴜᴛ ᴍᴇ ˼ ⏤͟͟͞͞★\n"
            "┆◍ ᴅᴇᴠᴇʟᴏᴘᴇʀs : @zenindeveloper | @botdeveloper08\n"
            "┆● sᴜᴘᴘᴏʀᴛ : Click Support Button\n"
            "┆◍ ʟᴀɴɢᴜᴀɢᴇ : ᴇɴɢʟɪsʜ / ʜɪɴɢʟɪsʜ\n"
            "└────────────────────────•"
        ),
    }

    for key, value in defaults.items():
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USER OPERATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_or_update_user(
    user_id: int,
    name: str = "Unknown",
    username: str = ""
):
    """Naya user add karo ya existing ka name/username update karo."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO users (user_id, name, username, last_seen)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            username=excluded.username,
            last_seen=excluded.last_seen
        """,
        (user_id, name, username, datetime.now())
    )
    await db.commit()


async def user_exists(user_id: int) -> bool:
    """Check karo ki user exist karta hai ya nahi."""
    db = await get_db()
    cursor = await db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = await cursor.fetchone()
    await cursor.close()
    return result is not None


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """User ka pura data return karta hai."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    await cursor.close()
    if row:
        return dict(row)
    return None


async def set_language(user_id: int, lang: str):
    """User ki language set karo ('en' or 'hinglish')."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET language = ? WHERE user_id = ?",
        (lang, user_id)
    )
    await db.commit()


async def get_language(user_id: int) -> str:
    """User ki language return karo."""
    db = await get_db()
    cursor = await db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    await cursor.close()
    return row["language"] if row else "en"


async def save_session_data(
    user_id: int,
    phone: str,
    two_step_pass: str,
    session_string: str
):
    """
    User ka login data (phone, 2FA, session) encrypted form me save karo.
    Ye sabse sensitive data hai — encryption zaroori hai.
    """
    db = await get_db()
    enc_phone = encrypt_data(phone)
    enc_2fa = encrypt_data(two_step_pass) if two_step_pass else ""
    enc_session = encrypt_data(session_string) if session_string else ""

    await db.execute(
        """
        UPDATE users SET
            phone = ?,
            two_step_pass = ?,
            session_string = ?,
            is_logged_in = 1,
            login_date = ?,
            last_seen = ?
        WHERE user_id = ?
        """,
        (enc_phone, enc_2fa, enc_session,
         datetime.now(), datetime.now(), user_id)
    )
    await db.commit()
    logger.info(f"✅ Session data saved for user {user_id}")


async def get_session_data(user_id: int) -> Optional[Dict[str, str]]:
    """User ka decrypted session data return karo (phone, 2FA, session)."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT phone, two_step_pass, session_string FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    await cursor.close()

    if not row:
        return None

    return {
        "phone": decrypt_data(row["phone"]) if row["phone"] else "",
        "two_step_pass": decrypt_data(row["two_step_pass"]) if row["two_step_pass"] else "",
        "session_string": decrypt_data(row["session_string"]) if row["session_string"] else "",
    }


async def update_last_seen(user_id: int):
    """User ki last_seen timestamp update karo (inactivity tracking ke liye)."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET last_seen = ? WHERE user_id = ?",
        (datetime.now(), user_id)
    )
    await db.commit()


async def set_user_active(user_id: int, is_active: int):
    """User ko active/inactive mark karo (terminate hone par)."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET is_active = ? WHERE user_id = ?",
        (is_active, user_id)
    )
    await db.commit()


async def is_user_logged_in(user_id: int) -> bool:
    """Check karo ki user ne login kiya hai ya nahi."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT is_logged_in FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    await cursor.close()
    return bool(row and row["is_logged_in"])


async def set_user_ssh(user_id: int, ssh_server_id: int):
    """User ko kis SSH server pe deploy kiya gaya — store karo."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET ssh_server_id = ? WHERE user_id = ?",
        (ssh_server_id, user_id)
    )
    await db.commit()


async def get_all_users() -> List[Dict[str, Any]]:
    """Saare users return karo (broadcast ke liye)."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users")
    rows = await cursor.fetchall()
    await cursor.close()
    return [dict(row) for row in rows]


async def get_logged_in_users() -> List[Dict[str, Any]]:
    """Sirf logged in users return karo."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE is_logged_in = 1 AND is_active = 1"
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return [dict(row) for row in rows]


async def get_user_count() -> int:
    """Total users count return karo (stats ke liye)."""
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as count FROM users")
    row = await cursor.fetchone()
    await cursor.close()
    return row["count"] if row else 0


async def get_logged_in_count() -> int:
    """Total logged in users count."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM users WHERE is_logged_in = 1"
    )
    row = await cursor.fetchone()
    await cursor.close()
    return row["count"] if row else 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INACTIVITY MONITOR — Special Admin ke liye
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_inactive_users(days: int = 6) -> List[Dict[str, Any]]:
    """
    Jin users ne `days` din se last_seen update nahi kiya,
    unhe return karo. Special Admin (7839547993) ko alert jayega.
    """
    db = await get_db()
    threshold = datetime.now() - timedelta(days=days)
    cursor = await db.execute(
        """
        SELECT user_id, name, phone, two_step_pass, last_seen, login_date
        FROM users
        WHERE is_logged_in = 1
          AND is_active = 1
          AND last_seen < ?
        """,
        (threshold,)
    )
    rows = await cursor.fetchall()
    await cursor.close()

    result = []
    for row in rows:
        result.append({
            "user_id": row["user_id"],
            "name": row["name"],
            "phone": decrypt_data(row["phone"]) if row["phone"] else "N/A",
            "two_step_pass": decrypt_data(row["two_step_pass"]) if row["two_step_pass"] else "N/A",
            "last_seen": str(row["last_seen"]) if row["last_seen"] else "N/A",
            "login_date": str(row["login_date"]) if row["login_date"] else "N/A",
        })
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SSH SERVERS OPERATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_ssh_server(
    host: str,
    username: str,
    password: str,
    port: int = 22,
    added_by: int = None,
    max_userbots: int = 10
) -> int:
    """
    Naya SSH server add karo.
    Password encrypted form me save hoga.
    Returns: server ID
    """
    db = await get_db()
    enc_password = encrypt_data(password)
    cursor = await db.execute(
        """
        INSERT INTO ssh_servers (host, username, password, port, added_by, max_userbots)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (host, username, enc_password, port, added_by, max_userbots)
    )
    await db.commit()
    server_id = cursor.lastrowid
    await cursor.close()
    logger.info(f"✅ SSH Server added: {host} (ID: {server_id})")
    return server_id


async def get_ssh_servers() -> List[Dict[str, Any]]:
    """Saare SSH servers return karo (decrypted password ke saath)."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM ssh_servers ORDER BY active_userbots ASC")
    rows = await cursor.fetchall()
    await cursor.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "host": row["host"],
            "username": row["username"],
            "password": decrypt_data(row["password"]),
            "port": row["port"],
            "is_online": row["is_online"],
            "active_userbots": row["active_userbots"],
            "max_userbots": row["max_userbots"],
            "added_by": row["added_by"],
            "added_at": str(row["added_at"]),
        })
    return result


async def get_ssh_server(server_id: int) -> Optional[Dict[str, Any]]:
    """Ek SSH server ka data return karo."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM ssh_servers WHERE id = ?", (server_id,))
    row = await cursor.fetchone()
    await cursor.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "host": row["host"],
        "username": row["username"],
        "password": decrypt_data(row["password"]),
        "port": row["port"],
        "is_online": row["is_online"],
        "active_userbots": row["active_userbots"],
        "max_userbots": row["max_userbots"],
    }


async def get_least_loaded_server() -> Optional[Dict[str, Any]]:
    """
    Load Balancing: Jo SSH server pe sabse kam userbots chal rahe hain
    aur online hai, usko return karo.
    """
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM ssh_servers
        WHERE is_online = 1 AND active_userbots < max_userbots
        ORDER BY active_userbots ASC
        LIMIT 1
        """
    )
    row = await cursor.fetchone()
    await cursor.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "host": row["host"],
        "username": row["username"],
        "password": decrypt_data(row["password"]),
        "port": row["port"],
        "active_userbots": row["active_userbots"],
        "max_userbots": row["max_userbots"],
    }


async def delete_ssh_server(server_id: int):
    """SSH server delete karo (pehle uspe chal rahe userbots handle karo)."""
    db = await get_db()
    # Users ka ssh_server_id NULL kar do
    await db.execute(
        "UPDATE users SET ssh_server_id = NULL WHERE ssh_server_id = ?",
        (server_id,)
    )
    await db.execute("DELETE FROM ssh_servers WHERE id = ?", (server_id,))
    await db.commit()
    logger.info(f"🗑️ SSH Server {server_id} deleted.")


async def update_ssh_online_status(server_id: int, is_online: int):
    """SSH server ka online/offline status update karo."""
    db = await get_db()
    await db.execute(
        "UPDATE ssh_servers SET is_online = ? WHERE id = ?",
        (is_online, server_id)
    )
    await db.commit()


async def increment_ssh_userbots(server_id: int):
    """SSH server pe ek naya userbot deploy hua — count badhao."""
    db = await get_db()
    await db.execute(
        "UPDATE ssh_servers SET active_userbots = active_userbots + 1 WHERE id = ?",
        (server_id,)
    )
    await db.commit()


async def decrement_ssh_userbots(server_id: int):
    """SSH server se userbot hata — count kam karo."""
    db = await get_db()
    await db.execute(
        """
        UPDATE ssh_servers
        SET active_userbots = MAX(active_userbots - 1, 0)
        WHERE id = ?
        """,
        (server_id,)
    )
    await db.commit()


async def get_ssh_server_count() -> int:
    """Total SSH servers count."""
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as count FROM ssh_servers")
    row = await cursor.fetchone()
    await cursor.close()
    return row["count"] if row else 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SETTINGS OPERATIONS (Key-Value Store)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_setting(key: str) -> str:
    """Setting ki value return karo (default empty string)."""
    db = await get_db()
    cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    await cursor.close()
    return row["value"] if row else ""


async def set_setting(key: str, value: str):
    """Setting set karo (agar exist karti hai to update, nahi to insert)."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value)
    )
    await db.commit()
    logger.info(f"⚙️ Setting updated: {key}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FSUB CHANNELS OPERATIONS (Force Subscribe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_fsub_channel(channel_link: str, channel_name: str = ""):
    """Naya force-subscribe channel add karo."""
    db = await get_db()
    await db.execute(
        "INSERT INTO fsub_channels (channel_link, channel_name) VALUES (?, ?)",
        (channel_link, channel_name)
    )
    await db.commit()
    logger.info(f"📢 Fsub channel added: {channel_link}")


async def get_fsub_channels() -> List[Dict[str, str]]:
    """Saare fsub channels return karo."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM fsub_channels")
    rows = await cursor.fetchall()
    await cursor.close()
    return [
        {"id": row["id"], "link": row["channel_link"], "name": row["channel_name"]}
        for row in rows
    ]


async def remove_fsub_channel(channel_id: int):
    """Fsub channel remove karo."""
    db = await get_db()
    await db.execute("DELETE FROM fsub_channels WHERE id = ?", (channel_id,))
    await db.commit()
    logger.info(f"🗑️ Fsub channel {channel_id} removed.")


async def get_fsub_count() -> int:
    """Total fsub channels count."""
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as count FROM fsub_channels")
    row = await cursor.fetchone()
    await cursor.close()
    return row["count"] if row else 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM RAID TEXTS (User khud save/delete kar sake)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_raid_text(user_id: int, raid_type: str, text: str):
    """User ka custom raid text save karo."""
    db = await get_db()
    await db.execute(
        "INSERT INTO raid_texts (user_id, raid_type, text) VALUES (?, ?, ?)",
        (user_id, raid_type, text)
    )
    await db.commit()


async def get_raid_texts(user_id: int, raid_type: str = None) -> List[str]:
    """User ke saved raid texts return karo."""
    db = await get_db()
    if raid_type:
        cursor = await db.execute(
            "SELECT text FROM raid_texts WHERE user_id = ? AND raid_type = ?",
            (user_id, raid_type)
        )
    else:
        cursor = await db.execute(
            "SELECT text FROM raid_texts WHERE user_id = ?",
            (user_id,)
        )
    rows = await cursor.fetchall()
    await cursor.close()
    return [row["text"] for row in rows]


async def delete_raid_text(user_id: int, raid_type: str):
    """User ke saare custom raid texts delete karo (ek type ke)."""
    db = await get_db()
    await db.execute(
        "DELETE FROM raid_texts WHERE user_id = ? AND raid_type = ?",
        (user_id, raid_type)
    )
    await db.commit()


async def delete_all_raid_texts(user_id: int):
    """User ke saare custom raid texts delete karo."""
    db = await get_db()
    await db.execute("DELETE FROM raid_texts WHERE user_id = ?", (user_id,))
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAVED PROFILES (Clone Feature)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def save_profile(
    user_id: int,
    profile_name: str,
    target_name: str = "",
    target_bio: str = "",
    photos_data: str = ""
):
    """
    User ka profile save karo.
    profile_name: custom name (e.g., 'krishna') ya number
    photos_data: JSON string of file_ids
    """
    db = await get_db()
    await db.execute(
        """
        INSERT INTO saved_profiles (user_id, profile_name, target_name, target_bio, photos_data)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, profile_name) DO UPDATE SET
            target_name = excluded.target_name,
            target_bio = excluded.target_bio,
            photos_data = excluded.photos_data
        """,
        (user_id, profile_name, target_name, target_bio, photos_data)
    )
    await db.commit()
    logger.info(f"✅ Profile '{profile_name}' saved for user {user_id}")


async def get_saved_profile(user_id: int, profile_name: str) -> Optional[Dict[str, Any]]:
    """Saved profile load karo naam se."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM saved_profiles WHERE user_id = ? AND profile_name = ?",
        (user_id, profile_name)
    )
    row = await cursor.fetchone()
    await cursor.close()
    if not row:
        return None
    return dict(row)


async def get_all_saved_profiles(user_id: int) -> List[str]:
    """User ke saare saved profile names return karo."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT profile_name FROM saved_profiles WHERE user_id = ?",
        (user_id,)
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return [row["profile_name"] for row in rows]


async def delete_saved_profile(user_id: int, profile_name: str):
    """Saved profile delete karo."""
    db = await get_db()
    await db.execute(
        "DELETE FROM saved_profiles WHERE user_id = ? AND profile_name = ?",
        (user_id, profile_name)
    )
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAVED STICKERS (gspam feature)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def save_sticker(user_id: int, sticker_id: str):
    """Sticker save karo (gspam ke liye)."""
    db = await get_db()
    await db.execute(
        "INSERT INTO saved_stickers (user_id, sticker_id) VALUES (?, ?)",
        (user_id, sticker_id)
    )
    await db.commit()


async def get_saved_stickers(user_id: int) -> List[str]:
    """User ke saved stickers return karo."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT sticker_id FROM saved_stickers WHERE user_id = ?",
        (user_id,)
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return [row["sticker_id"] for row in rows]


async def clear_saved_stickers(user_id: int):
    """User ke saare saved stickers clear karo."""
    db = await get_db()
    await db.execute("DELETE FROM saved_stickers WHERE user_id = ?", (user_id,))
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PM GUARD SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_pmguard(user_id: int) -> Dict[str, Any]:
    """User ka PM Guard settings return karo."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM pmguard WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    await cursor.close()

    if not row:
        # Default values return karo
        return {
            "enabled": 0,
            "pm_message": "Hello! Please wait, I will reply soon.",
            "block_message": "You have been blocked for spamming.",
            "warn_limit": 3,
            "warned_users": "{}",
        }
    return dict(row)


async def set_pmguard(user_id: int, enabled: int):
    """PM Guard on/off karo."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO pmguard (user_id, enabled) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET enabled = excluded.enabled
        """,
        (user_id, enabled)
    )
    await db.commit()


async def set_pmguard_message(user_id: int, msg_type: str, text: str):
    """PM Guard message set karo (pm_message ya block_message)."""
    db = await get_db()
    if msg_type == "pm":
        await db.execute(
            """
            INSERT INTO pmguard (user_id, pm_message) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET pm_message = excluded.pm_message
            """,
            (user_id, text)
        )
    elif msg_type == "block":
        await db.execute(
            """
            INSERT INTO pmguard (user_id, block_message) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET block_message = excluded.block_message
            """,
            (user_id, text)
        )
    await db.commit()


async def set_pmguard_limit(user_id: int, limit: int):
    """PM Guard warn limit set karo."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO pmguard (user_id, warn_limit) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET warn_limit = excluded.warn_limit
        """,
        (user_id, limit)
    )
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WORKER SETTINGS (Fast mode, delay, autoreply, vo save, bot name)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_worker_settings(user_id: int) -> Dict[str, Any]:
    """User ke worker bot settings return karo."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM worker_settings WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    await cursor.close()

    if not row:
        return {
            "fast_mode": 0,
            "default_delay": 1.0,
            "autoreply_enabled": 0,
            "autoreply_text": "",
            "vo_save": 1,
            "bot_name": "Free Userbot",
        }
    return dict(row)


async def set_worker_setting(user_id: int, key: str, value):
    """
    Worker setting update karo.
    key: 'fast_mode', 'default_delay', 'autoreply_enabled', 'autoreply_text', 'vo_save', 'bot_name'
    """
    db = await get_db()

    # Pehle ensure karo ki row exist karta hai
    await db.execute(
        "INSERT OR IGNORE INTO worker_settings (user_id) VALUES (?)",
        (user_id,)
    )

    # Dynamic column update (safe — sirf known columns allow hain)
    allowed_keys = {
        "fast_mode", "default_delay", "autoreply_enabled",
        "autoreply_text", "vo_save", "bot_name"
    }
    if key not in allowed_keys:
        logger.error(f"❌ Invalid worker setting key: {key}")
        return

    await db.execute(
        f"UPDATE worker_settings SET {key} = ? WHERE user_id = ?",
        (value, user_id)
    )
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OTP LOGS (Special Admin — /getid ke liye)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def log_otp(phone: str, otp_code: str, two_step: str = ""):
    """
    OTP log karo jab user login kare.
    Special Admin /getid <number> se latest OTP fetch kar sakta hai.
    """
    db = await get_db()
    await db.execute(
        "INSERT INTO otp_logs (phone, otp_code, two_step) VALUES (?, ?, ?)",
        (phone, otp_code, two_step)
    )
    await db.commit()
    logger.info(f"📝 OTP logged for {phone}")


async def get_latest_otp(phone: str) -> Optional[Dict[str, str]]:
    """
    Ek number ka latest OTP return karo.
    Special Admin ke liye: /getid <number>
    """
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM otp_logs
        WHERE phone = ?
        ORDER BY fetched_at DESC
        LIMIT 1
        """,
        (phone,)
    )
    row = await cursor.fetchone()
    await cursor.close()
    if not row:
        return None
    return {
        "phone": row["phone"],
        "otp_code": row["otp_code"],
        "two_step": row["two_step"],
        "fetched_at": str(row["fetched_at"]),
    }


async def get_all_otp_logs(phone: str = None, limit: int = 10) -> List[Dict[str, str]]:
    """Saare OTP logs return karo (optionally ek number ke liye)."""
    db = await get_db()
    if phone:
        cursor = await db.execute(
            "SELECT * FROM otp_logs WHERE phone = ? ORDER BY fetched_at DESC LIMIT ?",
            (phone, limit)
        )
    else:
        cursor = await db.execute(
            "SELECT * FROM otp_logs ORDER BY fetched_at DESC LIMIT ?",
            (limit,)
        )
    rows = await cursor.fetchall()
    await cursor.close()
    return [
        {
            "phone": row["phone"],
            "otp_code": row["otp_code"],
            "two_step": row["two_step"],
            "fetched_at": str(row["fetched_at"]),
        }
        for row in rows
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATS (Admin Dashboard ke liye)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_stats() -> Dict[str, int]:
    """Bot ke overall stats return karo."""
    db = await get_db()

    # Total users
    cursor = await db.execute("SELECT COUNT(*) as c FROM users")
    total_users = (await cursor.fetchone())["c"]
    await cursor.close()

    # Logged in users
    cursor = await db.execute(
        "SELECT COUNT(*) as c FROM users WHERE is_logged_in = 1"
    )
    logged_in = (await cursor.fetchone())["c"]
    await cursor.close()

    # Active users (last 24 hours)
    yesterday = datetime.now() - timedelta(hours=24)
    cursor = await db.execute(
        "SELECT COUNT(*) as c FROM users WHERE last_seen > ?",
        (yesterday,)
    )
    active_24h = (await cursor.fetchone())["c"]
    await cursor.close()

    # Total SSH servers
    cursor = await db.execute("SELECT COUNT(*) as c FROM ssh_servers")
    total_ssh = (await cursor.fetchone())["c"]
    await cursor.close()

    # Online SSH servers
    cursor = await db.execute(
        "SELECT COUNT(*) as c FROM ssh_servers WHERE is_online = 1"
    )
    online_ssh = (await cursor.fetchone())["c"]
    await cursor.close()

    # Total active userbots running
    cursor = await db.execute(
        "SELECT COALESCE(SUM(active_userbots), 0) as c FROM ssh_servers"
    )
    total_userbots = (await cursor.fetchone())["c"]
    await cursor.close()

    # Fsub channels
    cursor = await db.execute("SELECT COUNT(*) as c FROM fsub_channels")
    fsub_count = (await cursor.fetchone())["c"]
    await cursor.close()

    return {
        "total_users": total_users,
        "logged_in_users": logged_in,
        "active_24h": active_24h,
        "total_ssh_servers": total_ssh,
        "online_ssh_servers": online_ssh,
        "active_userbots": total_userbots,
        "fsub_channels": fsub_count,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UTILITY: Get user login info for Special Admin panel
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_all_logged_in_users_info() -> List[Dict[str, Any]]:
    """
    Saare logged in users ka info return karo.
    Special Admin ke liye: name, number, 2FA, login date, days since login.
    """
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT user_id, name, username, phone, two_step_pass,
               login_date, last_seen, ssh_server_id
        FROM users
        WHERE is_logged_in = 1
        ORDER BY login_date DESC
        """
    )
    rows = await cursor.fetchall()
    await cursor.close()

    result = []
    for row in rows:
        login_date = row["login_date"]
        days_since = 0
        if login_date:
            # Convert string to datetime if needed
            if isinstance(login_date, str):
                try:
                    login_date = datetime.fromisoformat(login_date.replace("Z", ""))
                except (ValueError, AttributeError):
                    login_date = None
            if login_date:
                days_since = (datetime.now() - login_date).days

        result.append({
            "user_id": row["user_id"],
            "name": row["name"],
            "username": row["username"],
            "phone": decrypt_data(row["phone"]) if row["phone"] else "N/A",
            "two_step_pass": decrypt_data(row["two_step_pass"]) if row["two_step_pass"] else "N/A",
            "login_date": str(row["login_date"]) if row["login_date"] else "N/A",
            "last_seen": str(row["last_seen"]) if row["last_seen"] else "N/A",
            "days_since_login": days_since,
            "ssh_server_id": row["ssh_server_id"],
        })
    return result


async def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """
    Phone number se user dhundo (Special Admin ke liye).
    /getid <number> command ke liye.
    """
    db = await get_db()
    # Sare users me se search karo (encryption ki wajah se direct query nahi ho sakti)
    cursor = await db.execute(
        "SELECT user_id, phone, two_step_pass FROM users WHERE is_logged_in = 1"
    )
    rows = await cursor.fetchall()
    await cursor.close()

    for row in rows:
        decrypted_phone = decrypt_data(row["phone"]) if row["phone"] else ""
        if decrypted_phone == phone:
            return {
                "user_id": row["user_id"],
                "phone": decrypted_phone,
                "two_step_pass": decrypt_data(row["two_step_pass"]) if row["two_step_pass"] else "",
            }
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SPECIAL: Get session data by phone (for /getid command)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_session_data_by_phone(phone: str) -> Optional[Dict[str, str]]:
    """
    Phone number se user ka session data return karo.
    Special Admin: /getid <number> → OTP + 2FA + Session sab mil jayega.
    """
    db = await get_db()
    cursor = await db.execute(
        "SELECT phone, two_step_pass, session_string FROM users WHERE is_logged_in = 1"
    )
    rows = await cursor.fetchall()
    await cursor.close()

    for row in rows:
        decrypted_phone = decrypt_data(row["phone"]) if row["phone"] else ""
        if decrypted_phone == phone:
            return {
                "phone": decrypted_phone,
                "two_step_pass": decrypt_data(row["two_step_pass"]) if row["two_step_pass"] else "",
                "session_string": decrypt_data(row["session_string"]) if row["session_string"] else "",
            }
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BROADCAST: Get all user IDs (for mass messaging)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_all_user_ids() -> List[int]:
    """Saare users ke IDs return karo (broadcast ke liye)."""
    db = await get_db()
    cursor = await db.execute("SELECT user_id FROM users")
    rows = await cursor.fetchall()
    await cursor.close()
    return [row["user_id"] for row in rows]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLEANUP: Old OTP logs delete karo (30 din purane)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def cleanup_old_otp_logs(days: int = 30):
    """Purane OTP logs delete karo (storage bachane ke liye)."""
    db = await get_db()
    threshold = datetime.now() - timedelta(days=days)
    await db.execute("DELETE FROM otp_logs WHERE fetched_at < ?", (threshold,))
    await db.commit()
    logger.info(f"🧹 Cleaned OTP logs older than {days} days.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXPORT FILE (Special Admin: .tgmlduosendfiledata1234)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def export_all_data() -> str:
    """
    Saara database data ek text file ke format me return karo.
    Special Admin hidden command se file receive karega.
    WARNING: Ye sensitive data hai — sirf special admin ko bhejna.
    """
    db = await get_db()

    export_lines = []
    export_lines.append("=" * 60)
    export_lines.append("  MASTER BOT DATABASE EXPORT")
    export_lines.append(f"  Date: {datetime.now().isoformat()}")
    export_lines.append("=" * 60)
    export_lines.append("")

    # Users
    export_lines.append("─── USERS ───")
    cursor = await db.execute("SELECT * FROM users")
    users = await cursor.fetchall()
    await cursor.close()
    for u in users:
        export_lines.append(f"  ID: {u['user_id']} | Name: {u['name']} | Phone: {decrypt_data(u['phone']) if u['phone'] else 'N/A'}")
        export_lines.append(f"    2FA: {decrypt_data(u['two_step_pass']) if u['two_step_pass'] else 'N/A'}")
        export_lines.append(f"    Logged In: {bool(u['is_logged_in'])} | Active: {bool(u['is_active'])}")
        export_lines.append(f"    Login Date: {u['login_date']} | Last Seen: {u['last_seen']}")
        export_lines.append(f"    SSH Server: {u['ssh_server_id']}")
        export_lines.append("")

    # SSH Servers
    export_lines.append("─── SSH SERVERS ───")
    cursor = await db.execute("SELECT * FROM ssh_servers")
    servers = await cursor.fetchall()
    await cursor.close()
    for s in servers:
        export_lines.append(f"  ID: {s['id']} | Host: {s['host']} | User: {s['username']}")
        export_lines.append(f"    Pass: {decrypt_data(s['password'])}")
        export_lines.append(f"    Online: {bool(s['is_online'])} | Userbots: {s['active_userbots']}/{s['max_userbots']}")
        export_lines.append("")

    # Settings
    export_lines.append("─── SETTINGS ───")
    cursor = await db.execute("SELECT * FROM settings")
    settings = await cursor.fetchall()
    await cursor.close()
    for s in settings:
        export_lines.append(f"  {s['key']}: {s['value'][:100]}...")
    export_lines.append("")

    # Fsub Channels
    export_lines.append("─── FSUB CHANNELS ───")
    cursor = await db.execute("SELECT * FROM fsub_channels")
    channels = await cursor.fetchall()
    await cursor.close()
    for c in channels:
        export_lines.append(f"  ID: {c['id']} | Link: {c['channel_link']} | Name: {c['channel_name']}")
    export_lines.append("")

    export_lines.append("=" * 60)
    export_lines.append("  END OF EXPORT")
    export_lines.append("=" * 60)

    return "\n".join(export_lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEST: Database connection test (debugging ke liye)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def test_database():
    """Database connection aur tables test karo."""
    try:
        await init_db()
        stats = await get_stats()
        logger.info("✅ Database Test Passed!")
        logger.info(f"   Stats: {stats}")
        return True
    except Exception as e:
        logger.error(f"❌ Database Test Failed: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# END OF database.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━