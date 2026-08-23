"""
╔═══════════════════════════════════════════════════════════╗
║  encryption.py — Secure Data Encryption Module            ║
║  Uses AES-128-CBC + HMAC-SHA256 (Fernet)                  ║
║                                                           ║
║  Features:                                                ║
║    • PBKDF2 key derivation (200,000 iterations)            ║
║    • Auto salt generation & storage                       ║
║    • String, Dict, File encryption                        ║
║    • Hash generation (SHA-256)                            ║
║    • Backwards compatibility (plaintext data won't crash) ║
║    • Graceful error handling (NO CRASHES)                 ║
╚═══════════════════════════════════════════════════════════╝

⚠️  EDUCATIONAL PURPOSE DISCLAIMER:
    This bot is for educational/learning purposes only.
    Misuse of userbot features (spam, raid, harassment)
    may violate Telegram ToS. Use responsibly.
"""

import os
import base64
import json
import hashlib
import logging
import secrets
from typing import Optional, Union, Dict, Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CRYPTOGRAPHY LIBRARY IMPORT (with graceful fallback)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = None
    InvalidToken = Exception
    hashes = None
    PBKDF2HMAC = None

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Files for storing key material (ADD THESE TO .gitignore!)
KEY_FILE = ".master_key"
SALT_FILE = ".master_salt"

# Environment variable for master password
MASTER_PASSWORD_ENV = "BOT_MASTER_PASSWORD"

# Default master password — CHANGE IN PRODUCTION via env variable!
# Used only if env variable is not set
DEFAULT_MASTER_PASSWORD = "FreeUserbot_Master_Secret_2024!@#_ChangeMe"

# PBKDF2 iterations (higher = more secure, slower)
PBKDF2_ITERATIONS = 200_000

# Marker prefix to identify encrypted data
# Prevents double-encryption and allows backwards compatibility
ENCRYPTION_MARKER = "ENC:"

# Singleton Fernet instance (cached for performance)
_fernet_instance: Optional[Any] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INTERNAL HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _ensure_crypto():
    """Check that cryptography library is available."""
    if not CRYPTO_AVAILABLE:
        raise RuntimeError(
            "❌ 'cryptography' library install nahi hai!\n"
            "Install karein: pip install cryptography"
        )


def _get_master_password() -> bytes:
    """
    Master password environment variable se lao,
    ya default use karo (development ke liye).
    """
    password = os.environ.get(MASTER_PASSWORD_ENV, DEFAULT_MASTER_PASSWORD)
    return password.encode('utf-8')


def _load_or_create_salt() -> bytes:
    """
    Salt file se load karo, ya naya generate karo.
    Salt safe hai file me store karne ke liye (ye secret nahi hai).
    """
    # Existing salt load karo
    if os.path.exists(SALT_FILE):
        try:
            with open(SALT_FILE, 'rb') as f:
                salt = f.read()
                if len(salt) >= 16:
                    return salt
        except Exception as e:
            logger.warning(f"Salt load failed, generating new: {e}")

    # Naya salt generate karo (32 bytes = 256 bits)
    salt = secrets.token_bytes(32)
    try:
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        # Restrictive permissions (Unix)
        try:
            os.chmod(SALT_FILE, 0o600)
        except Exception:
            pass  # Windows
        logger.info("🧂 New encryption salt generated & saved.")
    except Exception as e:
        logger.error(f"❌ Salt save failed: {e}")
    return salt


def _derive_key(password: bytes, salt: bytes) -> bytes:
    """
    PBKDF2 se Fernet-compatible key derive karo.
    200,000 iterations = brute force ke liye very hard.
    """
    _ensure_crypto()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def _get_fernet() -> Any:
    """
    Singleton Fernet instance return karo.
    Caching se PBKDF2 derivation baar-baar nahi hoti (performance).
    """
    global _fernet_instance
    if _fernet_instance is None:
        _ensure_crypto()
        password = _get_master_password()
        salt = _load_or_create_salt()
        key = _derive_key(password, salt)
        _fernet_instance = Fernet(key)
        logger.info("🔐 Fernet encryption instance initialized (cached).")
    return _fernet_instance


def _is_encrypted(data: str) -> bool:
    """Check karo ki data pehle se encrypted hai ya nahi."""
    if not data:
        return False
    return data.startswith(ENCRYPTION_MARKER)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN ENCRYPTION FUNCTIONS (String)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def encrypt_data(data: str) -> str:
    """
    String ko Fernet se encrypt karo.
    
    Args:
        data: Plain text string
        
    Returns:
        Encrypted string with marker prefix (base64)
        
    Example:
        >>> encrypt_data("+919999999999")
        'ENC:gAAAAABm...'
    """
    if not data:
        return ""

    # Double-encryption prevent karo
    if _is_encrypted(data):
        return data

    try:
        fernet = _get_fernet()
        encrypted = fernet.encrypt(data.encode('utf-8'))
        return ENCRYPTION_MARKER + encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"❌ Encryption failed: {e}")
        # Crash nahi hoga — original data return karenge
        # (Better to have unencrypted than no data)
        return data


def decrypt_data(data: str) -> str:
    """
    Encrypted string ko decrypt karo.
    
    Args:
        data: Encrypted string (with marker)
        
    Returns:
        Plain text string
        
    Note:
        Agar data encrypted nahi hai (no marker), original return hoga.
        Isse purana plaintext data bhi crash nahi karega.
    """
    if not data:
        return ""

    # Backwards compatibility: plaintext data as-is return karo
    if not _is_encrypted(data):
        return data

    try:
        fernet = _get_fernet()
        encrypted_part = data[len(ENCRYPTION_MARKER):]
        decrypted = fernet.decrypt(encrypted_part.encode('utf-8'))
        return decrypted.decode('utf-8')
    except InvalidToken:
        logger.error("❌ Invalid token — wrong key ya corrupted data")
        return ""
    except Exception as e:
        logger.error(f"❌ Decryption failed: {e}")
        return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DICT ENCRYPTION (Complex data ke liye)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def encrypt_dict(data: Dict[str, Any]) -> str:
    """
    Dictionary ko JSON me convert karke encrypt karo.
    Useful for: saved_profiles, pmguard warned_users, etc.
    """
    if not data:
        return ""
    try:
        json_str = json.dumps(data, ensure_ascii=False, default=str)
        return encrypt_data(json_str)
    except Exception as e:
        logger.error(f"❌ Dict encryption failed: {e}")
        return ""


def decrypt_dict(data: str) -> Dict[str, Any]:
    """Encrypted string ko dictionary me decrypt karo."""
    if not data:
        return {}

    decrypted = decrypt_data(data)
    if not decrypted:
        return {}

    try:
        return json.loads(decrypted)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode failed: {e}")
        return {}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HASH FUNCTIONS (Verification ke liye — one-way)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def hash_data(data: str) -> str:
    """
    SHA-256 hash generate karo (one-way, cannot be reversed).
    Useful for: verification tokens, integrity checks.
    """
    if not data:
        return ""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def verify_hash(data: str, expected_hash: str) -> bool:
    """Verify karo ki data ka hash expected_hash se match karta hai."""
    if not data or not expected_hash:
        return False
    actual = hash_data(data)
    # Constant-time comparison (timing attack prevention)
    return secrets.compare_digest(actual, expected_hash)


def generate_token(length: int = 32) -> str:
    """
    Cryptographically secure random token generate karo.
    Useful for: API keys, session tokens, admin access keys.
    """
    return secrets.token_urlsafe(length)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE ENCRYPTION (Hidden admin command ke liye)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def encrypt_file(input_path: str, output_path: str = None) -> bool:
    """
    Puri file ko encrypt karo (binary safe).
    Used by: .tgmlduosendfiledata1234 hidden admin command.
    """
    try:
        if not os.path.exists(input_path):
            logger.error(f"❌ File not found: {input_path}")
            return False

        with open(input_path, 'rb') as f:
            file_data = f.read()

        fernet = _get_fernet()
        encrypted = fernet.encrypt(file_data)

        if output_path is None:
            output_path = input_path + '.enc'

        with open(output_path, 'wb') as f:
            f.write(encrypted)

        logger.info(f"✅ File encrypted: {input_path} → {output_path}")
        return True
    except Exception as e:
        logger.error(f"❌ File encryption failed: {e}")
        return False


def decrypt_file(input_path: str, output_path: str = None) -> bytes:
    """Encrypted file ko decrypt karo."""
    try:
        if not os.path.exists(input_path):
            logger.error(f"❌ File not found: {input_path}")
            return b""

        with open(input_path, 'rb') as f:
            encrypted = f.read()

        fernet = _get_fernet()
        decrypted = fernet.decrypt(encrypted)

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            logger.info(f"✅ File decrypted: {input_path} → {output_path}")

        return decrypted
    except Exception as e:
        logger.error(f"❌ File decryption failed: {e}")
        return b""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAFE WRAPPERS (Never crash — for database.py integration)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def safe_encrypt(data: Union[str, Dict, int, float, None]) -> str:
    """
    Kisi bhi data type ko safely encrypt karo.
    Never raises exceptions.
    """
    if data is None:
        return ""
    if isinstance(data, dict):
        return encrypt_dict(data)
    if isinstance(data, (int, float)):
        data = str(data)
    if not isinstance(data, str):
        data = str(data)
    return encrypt_data(data)


def safe_decrypt(data: Union[str, None]) -> str:
    """
    Safely decrypt karo. Kabhi exception raise nahi karega.
    """
    if data is None:
        return ""
    if not isinstance(data, str):
        data = str(data)
    return decrypt_data(data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MANAGEMENT & DIAGNOSTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def reset_encryption():
    """Fernet instance reset karo (testing/key change ke liye)."""
    global _fernet_instance
    _fernet_instance = None
    logger.info("🔄 Encryption instance reset.")


def get_encryption_info() -> Dict[str, Any]:
    """Current encryption setup ki info (debugging ke liye)."""
    return {
        "crypto_available": CRYPTO_AVAILABLE,
        "algorithm": "AES-128-CBC + HMAC-SHA256 (Fernet)",
        "kdf": f"PBKDF2-SHA256 ({PBKDF2_ITERATIONS:,} iterations)",
        "salt_file_exists": os.path.exists(SALT_FILE),
        "master_password_set": bool(os.environ.get(MASTER_PASSWORD_ENV)),
        "using_default_password": not bool(os.environ.get(MASTER_PASSWORD_ENV)),
        "fernet_initialized": _fernet_instance is not None,
        "marker": ENCRYPTION_MARKER,
    }


def test_encryption() -> bool:
    """
    Encryption system ko test karo.
    Setup ke baad ek baar zaroor run karein.
    """
    try:
        _ensure_crypto()

        # Test 1: String encryption
        test_str = "FreeUserbot_Test_2024!@#"
        enc = encrypt_data(test_str)
        dec = decrypt_data(enc)
        assert dec == test_str, "String encryption failed"
        logger.info("✅ Test 1 PASSED: String encryption")

        # Test 2: Dict encryption
        test_dict = {"phone": "+919999999999", "pass": "secret123", "id": 12345}
        enc_d = encrypt_dict(test_dict)
        dec_d = decrypt_dict(enc_d)
        assert dec_d == test_dict, "Dict encryption failed"
        logger.info("✅ Test 2 PASSED: Dict encryption")

        # Test 3: Hash verification
        h = hash_data(test_str)
        assert verify_hash(test_str, h), "Hash verification failed"
        assert not verify_hash("wrong", h), "Hash should not match"
        logger.info("✅ Test 3 PASSED: Hash verification")

        # Test 4: Backwards compatibility (plaintext data)
        plaintext = "not_encrypted_data"
        assert decrypt_data(plaintext) == plaintext, "Backwards compat failed"
        logger.info("✅ Test 4 PASSED: Backwards compatibility")

        # Test 5: Empty data
        assert encrypt_data("") == ""
        assert decrypt_data("") == ""
        assert encrypt_dict({}) == ""
        assert decrypt_dict("") == {}
        logger.info("✅ Test 5 PASSED: Empty data handling")

        # Test 6: Double encryption prevention
        enc2 = encrypt_data(enc)
        assert enc2 == enc, "Double encryption should be prevented"
        logger.info("✅ Test 6 PASSED: Double encryption prevention")

        logger.info("\n🎉 All encryption tests PASSED!\n")
        return True
    except Exception as e:
        logger.error(f"❌ Encryption test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE INITIALIZATION (runs on import)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _init():
    """Module import pe crypto availability check karo."""
    if not CRYPTO_AVAILABLE:
        logger.warning(
            "\n⚠️  WARNING: 'cryptography' library not installed!\n"
            "   Data will NOT be encrypted (plaintext storage).\n"
            "   Install with: pip install cryptography\n"
        )
    else:
        logger.info("🔐 Encryption module loaded (cryptography available).")


_init()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIRECT EXECUTION (Run tests)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    print("\n" + "=" * 60)
    print("  🔐 Encryption Module Test Suite")
    print("=" * 60 + "\n")

    test_encryption()

    print("\n" + "-" * 60)
    print("  Encryption Info:")
    print("-" * 60)
    for k, v in get_encryption_info().items():
        print(f"  {k:<25}: {v}")
    print("\n" + "=" * 60 + "\n")