import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
import os
import time

from ..config import Config
from ..tools.text import TEXT
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


################## Saving thumbnail 🖼 ##################

@Client.on_message(filters.photo & filters.incoming & filters.private)
async def save_photo(c, m):

    send_message = await m.reply_text(
        "Processing.....⏳",
        
        quote=True
    )

    is_user_exist = await c.db.is_user_exist(m.from_user.id)
    if not is_user_exist:
        await c.db.add_user(m.from_user.id)

    download_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"
    await c.db.update_settings_status(m.from_user.id, 'permanent_thumb', m.id)
    await m.download(
        file_name=download_location,
        block=False
    )

    await send_message.edit(
        text=TEXT.SAVED_CUSTOM_THUMBNAIL
        
    )


################## Deleting permanent thumbnail 🗑 ##################

@Client.on_message(filters.command("delthumb") & filters.incoming & filters.private)
async def delete_thumbnail(c, m):

    send_message = await m.reply_text(
        "Processing.....⏳",
        
        quote=True
    )

    is_user_exist = await c.db.is_user_exist(m.from_user.id)
    if not is_user_exist:
        await c.db.add_user(m.from_user.id)

    download_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"
    thumbnail = await c.db.get_settings_status(m.from_user.id, 'permanent_thumb')

    if not thumbnail:
        text = TEXT.NO_CUSTOM_THUMB_NAIL_FOUND

    if thumbnail:
        try:
            await c.db.update_settings_status(m.from_user.id, 'permanent_thumb', '')
        except:
            pass
        text = TEXT.DELETED_CUSTOM_THUMBNAIL

    try:
        os.remove(download_location)
    except:
        pass

    await send_message.edit(
        text=text
        
    )


################## Sending permanent thumbnail 🕶 ##################

@Client.on_message(filters.command("thumbnail") & filters.incoming & filters.private)
async def show_thumbnail(c, m):

    send_message = await m.reply_text(
        "Processing.....⏳",
        
        quote=True
    )

    is_user_exist = await c.db.is_user_exist(m.from_user.id)
    if not is_user_exist:
        await c.db.add_user(m.from_user.id)

    thumbnail = await c.db.get_settings_status(m.from_user.id, 'permanent_thumb')
    if not thumbnail:
         await send_message.edit(
             text=TEXT.NO_CUSTOM_THUMB_NAIL_FOUND
         )
    if thumbnail:
         download_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"

         if not os.path.exists(download_location):
             thumb_nail = await c.get_messages(m.chat.id, thumbnail)
             try:
                 photo_location = await thumb_nail.download(file_name=download_location)
             except:
                 await c.db.update_settings_status(m.from_user.id, 'permanent_thumb', '')
                 return await send_message.edit(text=TEXT.NO_CUSTOM_THUMB_NAIL_FOUND)
         else:
             photo_location = download_location

         await send_message.delete()
         await m.reply_photo(
             photo=photo_location,
             caption=TEXT.THUMBNAIL_CAPTION,
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Del thumbnail 🗑️", callback_data="del")]]),
             
             quote=True
         )


################## THE END 🛑 ##################
