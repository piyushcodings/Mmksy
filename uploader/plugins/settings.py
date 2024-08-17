import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)

from ..config import Config
from ..tools.text import TEXT
from .thumbnail import show_thumbnail
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


#################### Sending message for Settings Command ⚙ ####################

@Client.on_message(filters.command('settings') & filters.incoming & filters.private)
async def settings(c, m, cb=False):
    if not cb:
        send_message = await m.reply_text(
            "Processing.....⏳",
            
            quote=True
        )
    
    if not await c.db.is_user_exist(m.from_user.id):
        await c.db.add_user(m.from_user.id)
        await c.send_message(
            Config.DB_CHANNEL_ID,
            f"New User {m.from_user.mention} started."
        )

    settings = await c.db.get_all_settings(m.from_user.id)

    upload_mode = settings['upload_as_file']
    upload_text = '🗂️ File' if upload_mode else '🎥 Video'

    bot_updates_mode = settings['bot_updates']
    bot_updates_text = 'On 🔔' if bot_updates_mode else 'Off 🔕' 

    thumbnail = settings['permanent_thumb']
    thumb_text = 'ShowThumb🌌' if thumbnail else 'Set Custom 🌆 Thumbnail '

    ytdl_ext = settings['extension']
    ext_text = Config.Extension[ytdl_ext]


    

    settings_btn = [[
        InlineKeyboardButton(f'{upload_text}', callback_data=f"setting+upload_as_file+{not upload_mode}")
        ],[
        InlineKeyboardButton(f"ʙᴏᴛ ᴜᴘᴅᴀᴛᴇs ♻️: {bot_updates_text}", callback_data=f"setting+bot_updates+{not bot_updates_mode}")
        ],[
        InlineKeyboardButton(f"{thumb_text}", callback_data=f"thumbnail")
        ],[

        InlineKeyboardButton(f"ʏᴛᴅʟ ғɪʟᴛᴇʀ 🌀: {ext_text} 🔍", callback_data=f"ytdl_ext+{ytdl_ext}")
    ]]

    if cb:
        if m.message.reply_to_message.text == '/start':
            settings_btn.append([InlineKeyboardButton('《 BACK 》', callback_data='back')])
    try:
        if cb:
            await m.answer()
            await m.message.edit(
                text="⚙️ 𝖢𝗈𝗇𝖿𝗂𝗀 𝖡𝗈𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌",
               
                reply_markup=InlineKeyboardMarkup(settings_btn)
            )
        if not cb:
            await send_message.edit(
                text="⚙️ 𝖢𝗈𝗇𝖿𝗂𝗀 𝖡𝗈𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌",
               
                reply_markup=InlineKeyboardMarkup(settings_btn)
            )
    except:
        pass


#################### Callbacks related to Settings ⚙ ####################

@Client.on_callback_query(filters.regex('^setting'))
async def settings_cb(c, m):
    if len(m.data.split("+")) == 1:
        return await settings(c, m, cb=True)
    cmd, key, val = m.data.split("+")
    if 'True' in val or 'False' in val:
        value = True if val == 'True' else False
        await c.db.update_settings_status(m.from_user.id, str(key), value)
        await settings(c, m, cb=True)
    else:
        value = int(val)
        await c.db.update_settings_status(m.from_user.id, str(key), value)



@Client.on_callback_query(filters.regex('^ytdl_ext\+'))
async def update_ytdl(c, m):
    cmd, value = m.data.split('+')
    value = int(value)
    value += 1
    if value > 3:
        value = 0
    await c.db.update_settings_status(m.from_user.id, 'extension', value)
    await settings(c, m, cb=True) 


@Client.on_callback_query(filters.regex('^thumbnail'))
async def thumb_cb(c, m):
    thumbnail = await c.db.get_settings_status(m.from_user.id, 'permanent_thumb')
    if not thumbnail:
        await m.answer('Send me a photo For saving permanently 🏞', show_alert=True)
    else:
        await show_thumbnail(c, m.message.reply_to_message)
    await settings(c, m, cb=True)



#################### THE END 🌋 ####################
