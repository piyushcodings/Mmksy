import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)



import math
import time
import asyncio
from ..config import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


############################# Progress Bar 📊 #############################
async def progress_bar(current, total, status_msg, start, c, m, id):
    present = time.time()
    if id not in Config.ACTIVE_DOWNLOADS or present - start > 1200:
        await c.stop_transmission()
    if present - Config.last_edit[id] > 5 or current == total:
        speed = current / (present - start)
        percentage = current * 100 / total
        time_to_complete = round(((total - current) / speed)) * 1000
        time_to_complete = TimeFormatter(time_to_complete)
        progressbar = "[{0}{1}]".format(\
            ''.join(["▰" for i in range(math.floor(percentage / 10))]),
            ''.join(["▱" for i in range(10 - math.floor(percentage / 10))])
            )
        current_message = f"**𝖴𝗉𝗅𝗈𝖺𝖽 𝖲𝗍𝖺𝗍𝗎𝗌:** {round(percentage, 2)}%\n\n"
        current_message += f"{progressbar}\n\n"
        current_message += f"➩ **Speed**: `{humanbytes(speed)}/sec`\n\n"
        current_message += f"➩ **Done**: `{humanbytes(current)}`\n\n"
        current_message += f"➩ **Size**: `{humanbytes(total)}`\n\n"
        current_message += f"➩ **Time Left**: `{time_to_complete if (start - present) != 0 else 'Calculating.....'}`"
        try:
            button = [[InlineKeyboardButton("𝖢𝖺𝗇𝖼𝖾𝗅 ⛔", callback_data=f"cancel_download+{id}")]]
            await m.edit(
                text=current_message,
                
                reply_markup=InlineKeyboardMarkup(button)
            )
            Config.last_edit[id] = time.time()
            
        except:
            pass

             

        


############################# Size #############################

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


############################# Time Formating ⏰ #############################

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " days, ") if days else "") + \
        ((str(hours) + " hrs, ") if hours else "") + \
        ((str(minutes) + " min, ") if minutes else "") + \
        ((str(seconds) + " sec, ") if seconds else "") + \
        ((str(milliseconds) + " millisec, ") if milliseconds else "")
    return tmp[:-2]


############################# END 🌋 #############################
