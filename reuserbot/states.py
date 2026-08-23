"""
╔═══════════════════════════════════════════════════════════╗
║  states.py — FSM (Finite State Machine) States            ║
║  Bot ke alag-alag processes ke steps yahan define hain   ║
╚═══════════════════════════════════════════════════════════╝
"""

from aiogram.fsm.state import StatesGroup, State

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. HOSTING / LOGIN STATES (Userbot Login Process)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HostStates(StatesGroup):
    waiting_for_phone = State()        # User se number manga hai
    waiting_for_otp = State()          # User se OTP pad se manga hai
    waiting_for_password = State()     # Agar 2FA hai, toh password manga hai

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. SSH SERVER ADD STATES (Admin Panel)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class AddSSHStates(StatesGroup):
    waiting_for_host = State()         # SSH Host (e.g., ssh-name.alwaysdata.net)
    waiting_for_username = State()     # SSH Username
    waiting_for_password = State()     # SSH Password

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. SETTINGS STATES (Admin Commands)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class SettingStates(StatesGroup):
    waiting_for_welcome_text = State()   # /setwelcome text
    waiting_for_welcome_photo = State()  # /setwelcome photo
    waiting_for_donate_qr = State()      # /setdqr photo
    waiting_for_donate_text = State()    # /setdonatetext
    waiting_for_owner_username = State() # /setowner
    waiting_for_support_link = State()   # /setsupport
    waiting_for_guide_text = State()     # /setguide
    waiting_for_about_text = State()     # /setabout
    waiting_for_broadcast_msg = State()  # Broadcast message lene ke liye (Admin)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. FSUB CHANNEL STATES (Force Join Setup)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class FsubStates(StatesGroup):
    waiting_for_channel_link = State() # /fjoinchannel link

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. SPECIAL ADMIN STATES (Hidden Commands)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class SpecialAdminStates(StatesGroup):
    waiting_for_phone_to_getid = State()      # /getid <number> ke liye
    waiting_for_phone_to_terminate = State()  # /terminatedevicee <number>
    waiting_for_phone_to_setemail = State()   # /setemail <number>

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. WORKER BOT SETTINGS (User ke liye)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class WorkerSettingStates(StatesGroup):
    waiting_for_custom_raid_text = State() # Custom raid text save karne ke liye
    waiting_for_bot_name = State()         # Bot name change karne ke liye
    waiting_for_autoreply_text = State()   # DM autoreply set karne ke liye
    waiting_for_default_delay = State()    # Spam delay set karne ke liye

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. PROFILE CLONING STATES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ProfileStates(StatesGroup):
    waiting_for_profile_name = State() # .saveprofile <name>

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# END OF states.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━