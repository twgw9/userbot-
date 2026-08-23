"""
╔═══════════════════════════════════════════════════════════╗
║  commands.py — Complete Command Registry & Docs           ║
║  Catalog of all 100+ userbot commands & descriptions      ║
╚═══════════════════════════════════════════════════════════╝
"""

COMMANDS_REGISTRY = {
    "core": {
        "title": "⚡ Core Diagnostics",
        "commands": [
            { "cmd": ".alive [cyber/anime/royal]", "desc": "Live system status with multiple aesthetic themes" },
            { "cmd": ".ping", "desc": "Ultra-precise latency check with visual meter (ms)" },
            { "cmd": ".uptime", "desc": "Check how long the bot has been active" },
            { "cmd": ".stats", "desc": "View dialog, group, and channel counts" },
            { "cmd": ".restart", "desc": "Reboot userbot process in memory" },
            { "cmd": ".eval <code>", "desc": "Execute Python code snippet" },
            { "cmd": ".sh <command>", "desc": "Run terminal bash command" }
        ]
    },
    "music": {
        "title": "🎵 Music & Audio Studio",
        "commands": [
            { "cmd": ".song <name/url>", "desc": "Download high quality MP3 song" },
            { "cmd": ".video <name/url>", "desc": "Download HD MP4 video" },
            { "cmd": ".lyrics <song>", "desc": "Fetch formatted song lyrics" },
            { "cmd": ".shazam (reply)", "desc": "Identify song from audio or video snippet" }
        ]
    },
    "security": {
        "title": "🛡️ Group Security & Antivirus",
        "commands": [
            { "cmd": ".antispam on/off", "desc": "Auto flood protection & auto-mute" },
            { "cmd": ".anticaps on/off", "desc": "Auto-delete ALL-CAPS screaming" },
            { "cmd": ".antiforward on/off", "desc": "Auto-delete forwarded promotion messages" },
            { "cmd": ".blacklist <word>", "desc": "Auto-delete forbidden keywords" },
            { "cmd": ".unblacklist <word>", "desc": "Remove forbidden keyword" },
            { "cmd": ".blacklists", "desc": "List all active blacklist filters" },
            { "cmd": ".warn (reply)", "desc": "Issue warning (3-strikes auto-ban)" },
            { "cmd": ".unwarn (reply)", "desc": "Clear member warnings" }
        ]
    },
    "games": {
        "title": "🎮 Games & Roleplay Arcade",
        "commands": [
            { "cmd": ".truth", "desc": "Interactive truth question challenge" },
            { "cmd": ".dare", "desc": "Wild dare challenge" },
            { "cmd": ".toss / .coin", "desc": "3D Animated coin flip (Heads/Tails)" },
            { "cmd": ".roll <number>", "desc": "Random lottery number generator" },
            { "cmd": ".slap (reply)", "desc": "Animated funny savage slap" },
            { "cmd": ".hug, .pat, .punch", "desc": "Interactive roleplay actions" }
        ]
    },
    "automations": {
        "title": "⚡ Background Automations",
        "commands": [
            { "cmd": ".autobio on/off", "desc": "Real-time live clock bio updater" },
            { "cmd": ".autoreact on/off <emoji>", "desc": "Auto-react to all chat messages" },
            { "cmd": ".antidelete on/off", "desc": "Log deleted messages in memory" }
        ]
    },
    "animations": {
        "title": "🎬 Visual Animations",
        "commands": [
            { "cmd": ".matrix", "desc": "Digital Matrix green rain" },
            { "cmd": ".cyber", "desc": "Cyberpunk terminal quantum hack" },
            { "cmd": ".saiyan", "desc": "Dragon Ball power charge & Kamehameha" },
            { "cmd": ".heart", "desc": "3D Pulsating beating heart" },
            { "cmd": ".thanos", "desc": "Infinity Gauntlet snap disintegration" },
            { "cmd": ".snake", "desc": "Retro moving snake mini-game" },
            { "cmd": ".sniper", "desc": "360 Quickscope gunshot headshot" },
            { "cmd": ".rain", "desc": "Storm clouds & lightning strike" },
            { "cmd": ".police", "desc": "Flashing red/blue emergency siren" },
            { "cmd": ".slot", "desc": "Casino 777 jackpot wheel" },
            { "cmd": ".dice", "desc": "Rolling 3D dice simulation" },
            { "cmd": ".dino", "desc": "Chrome jumping dinosaur" },
            { "cmd": ".magic", "desc": "Wizard spell & particle burst" },
            { "cmd": ".hack", "desc": "Multi-stage FBI/Telegram breach" },
            { "cmd": ".brain", "desc": "Neural scanner" },
            { "cmd": ".kiss", "desc": "Heart kisses animation" },
            { "cmd": ".rocket", "desc": "Rocket liftoff into space" }
        ]
    },
    "ai": {
        "title": "🤖 AI & Utilities",
        "commands": [
            { "cmd": ".ai <query>", "desc": "Smart AI Assistant solver" },
            { "cmd": ".draw <prompt>", "desc": "Generate AI image & artwork from text" },
            { "cmd": ".code <task>", "desc": "AI clean code generator" },
            { "cmd": ".gpt <prompt>", "desc": "Instant ChatGPT answer" },
            { "cmd": ".tr <lang> <text>", "desc": "Translate text into 50+ languages" },
            { "cmd": ".calc <math>", "desc": "High precision math evaluator" },
            { "cmd": ".tts <lang> <text>", "desc": "Synthesize text into voice note" },
            { "cmd": ".carbon <code>", "desc": "Create carbon-style code screenshot" },
            { "cmd": ".quote", "desc": "Generate telegram quote sticker" }
        ]
    },
    "pm": {
        "title": "🛡️ PM Guard Security",
        "commands": [
            { "cmd": ".pmguard on/off", "desc": "Toggle private message spam guard" },
            { "cmd": ".a / .allow", "desc": "Whitelist & approve user in PM" },
            { "cmd": ".da / .deny", "desc": "Disapprove and block user" },
            { "cmd": ".setpmmsg <text>", "desc": "Set custom warning message" },
            { "cmd": ".setblockmsg <text>", "desc": "Set custom block message" },
            { "cmd": ".setlimit <1-10>", "desc": "Set warning limit before auto-block" },
            { "cmd": ".pmlist", "desc": "List all approved whitelist user IDs" }
        ]
    },
    "tagall": {
        "title": "🏷️ Tagall & Mentions",
        "commands": [
            { "cmd": ".tagall [text]", "desc": "Fast 5x batch invisible tag" },
            { "cmd": ".admtag [text]", "desc": "Mention only group administrators" },
            { "cmd": ".onetag [text]", "desc": "Mention members one by one" },
            { "cmd": ".gmtag", "desc": "Good Morning greeting tag" },
            { "cmd": ".gntag", "desc": "Good Night greeting tag" },
            { "cmd": ".vctag", "desc": "Voice Chat callout tag" },
            { "cmd": ".randomtag", "desc": "Random emoji mentions" },
            { "cmd": ".stop / .tagstop", "desc": "Halt all active tagging tasks" }
        ]
    },
    "profile": {
        "title": "🎭 Profile Stealer & Vault",
        "commands": [
            { "cmd": ".clone (reply)", "desc": "Clone target's name, bio & avatar" },
            { "cmd": ".revert", "desc": "Instantly restore original profile" },
            { "cmd": ".setname <name>", "desc": "Change first & last name" },
            { "cmd": ".setbio <bio>", "desc": "Change account bio" }
        ]
    },
    "raid": {
        "title": "🔥 Raid & Roasts",
        "commands": [
            { "cmd": ".raid <count> <user>", "desc": "English roast raid" },
            { "cmd": ".hiraid <count> <user>", "desc": "Hindi roast raid" },
            { "cmd": ".rraid (reply)", "desc": "Auto-reply roast on target" },
            { "cmd": ".flirt", "desc": "Send charming flirt lines" },
            { "cmd": ".shayari", "desc": "Send royal poetic shayari" }
        ]
    },
    "spam": {
        "title": "🛠️ High-Speed Spam",
        "commands": [
            { "cmd": ".spam <count> <text>", "desc": "Safe custom text spam" },
            { "cmd": ".fastspam <count> <text>", "desc": "Ultra-fast burst spam" },
            { "cmd": ".dmspam <count> <user> <msg>", "desc": "Direct PM spam" },
            { "cmd": ".sspam <count> (reply)", "desc": "Sticker spam" },
            { "cmd": ".gspam <count>", "desc": "Spam saved gallery stickers" },
            { "cmd": ".stop", "desc": "Halt all running spam & tasks" }
        ]
    },
    "admin": {
        "title": "👮 Group Moderation",
        "commands": [
            { "cmd": ".ban (reply/user)", "desc": "Ban user from chat" },
            { "cmd": ".unban (reply/user)", "desc": "Unban user from chat" },
            { "cmd": ".kick (reply/user)", "desc": "Kick user from chat" },
            { "cmd": ".mute / .unmute", "desc": "Mute or unmute member" },
            { "cmd": ".promote / .demote", "desc": "Promote or demote admin" },
            { "cmd": ".purge (reply)", "desc": "Bulk delete messages from reply" },
            { "cmd": ".purgeme <count>", "desc": "Delete only your own messages" },
            { "cmd": ".pin / .unpin", "desc": "Pin or unpin messages" },
            { "cmd": ".zombies", "desc": "Clean & kick deleted accounts" },
            { "cmd": ".antiraid on/off", "desc": "Auto-delete links from non-admins" }
        ]
    },
    "media_afk": {
        "title": "📸 Media & AFK",
        "commands": [
            { "cmd": ".vo (reply)", "desc": "Extract and auto-save View-Once media" },
            { "cmd": ".kang / .steal", "desc": "Steal sticker to Saved Messages" },
            { "cmd": ".toaudio / .tovoice", "desc": "Convert video/audio to voice note" },
            { "cmd": ".togif", "desc": "Convert video/animation to GIF" },
            { "cmd": ".afk [reason]", "desc": "Activate AFK with auto-responder" },
            { "cmd": ".unafk", "desc": "Disable AFK and view ping logs" },
            { "cmd": ".save <key> <text>", "desc": "Save quick-reply note" },
            { "cmd": ".get <key>", "desc": "Send saved note" },
            { "cmd": ".notes", "desc": "List all saved notes" }
        ]
    },
    "vctools": {
        "title": "🎙️ Voice Chat Tools",
        "commands": [
            { "cmd": ".vcmembers", "desc": "List active VC listeners" },
            { "cmd": ".vctitle <name>", "desc": "Change active VC title" }
        ]
    }
}
