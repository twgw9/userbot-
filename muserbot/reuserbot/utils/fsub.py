import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import database

logger = logging.getLogger(__name__)

async def check_fsub_status(bot: Bot, user_id: int) -> bool:
    """
    Check karta hai ki user ne saare channels join kiye hain ya nahi.
    Private channels (t.me/+...) ko skip karta hai taaki Peer ID error na aaye.
    """
    channels = await database.get_fsub_channels()
    if not channels:
        return True # Agar koi channel set hi nahi hai, toh direct True
    
    for ch in channels:
        link = ch['link']
        
        # Private channels ko skip karo (Bot unka username nahi nikal sakta)
        if 't.me/+' in link or 't.me/joinchat/' in link:
            logger.warning(f"Skipping private link {link} for FSub check.")
            continue
            
        # Public Username extract karna
        if 't.me/' in link:
            username = link.split('t.me/')[-1]
        else:
            username = link.lstrip('@')
            
        try:
            member = await bot.get_chat_member(chat_id=f"@{username}", user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except (TelegramBadRequest, TelegramForbiddenError):
            logger.warning(f"FSub Check Error for {link}: Bot might not be admin. Skipping.")
            continue # Agar bot admin na ho toh error na de, skip kare
        except Exception as e:
            logger.error(f"Unexpected FSub Error: {e}")
            continue
            
    return True