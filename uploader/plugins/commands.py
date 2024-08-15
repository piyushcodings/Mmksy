import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


import pyrogram
from ..config import Config
from ..tools.text import TEXT
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 



@Client.on_message(filters.command(["features"]))
async def send_help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
   await client.send_message(message.chat.id, FEATURES_TXT, reply_to_message_id=message.id, disable_web_page_preview=True)




@Client.on_message(filters.command("dlcaption") & filters.private & filters.incoming)
async def delcap(c, m):
    if not await c.db.is_user_exist(m.from_user.id):
        await c.db.add_user(m.from_user.id)
    caption = await c.db.get_settings_status(m.from_user.id, 'custom_caption')
    if not caption:
        text = "You didn't set any caption yet 😩"
    else:
        await c.db.update_settings_status(m.from_user.id, 'custom_caption', '')
        text = "Default caption deleted successfully ✨"
    await m.reply_text(text, quote=True)

@Client.on_message(filters.command("scaption") & filters.private & filters.incoming)
async def set_caption(c, m):
    if not await c.db.is_user_exist(m.from_user.id):
        await c.db.add_user(m.from_user.id)

    if len(m.command) == 1:
        await m.reply_text(
            "Use this command to set the custom caption for your files."
            "For setting your caption send caption in the format \n`/set_caption <your_caption>`\n\n"
            "Examples:\n\nSimple caption: `/scaption My caption`\n\n"
            "Dynamic capiton: `/set_caption 📕 File Name: {filename}\n\n💾 Size: {filesize}\n\n⏰ Duration: {duration}`\n\n\n"
            "Available Variables:\n\n"
            "    • `{filename}` - replaced by the filename\n"
            "    • `{duration}` - replaced by the duration of videos\n"
            "    • `{filesize}` - replaced by filesize\n\n"
            "Note:\nYou can check the current caption using /caption",
            quote=True)
    else:
        if len(m.text.markdown) > len(m.text.html):
            caption = m.text.markdown.split(' ', 1)[1]
        else:
            caption = m.text.html.split(' ', 1)[1]
        await c.db.update_settings_status(m.from_user.id, 'custom_caption', caption)
        await m.reply_text(f'Your Caption:\n\n{caption}', quote=True)


@Client.on_message(filters.command("caption") & filters.private & filters.incoming)
async def caption(c, m):
    if not await c.db.is_user_exist(m.from_user.id):
        await c.db.add_user(m.from_user.id)

    caption = await c.db.get_settings_status(m.from_user.id, 'custom_caption')
    if not caption:
        text = "You didn't set any custom caption yet for setting custom caption use /set_caption."
    else:
        text = f"Your custom caption: \n\n{caption}"
    await m.reply_text(text, quote=True)


@Client.on_message(filters.command('list'))
async def list(c, m):
    result = Config.normal_queue._unfinished_tasks - len(Config.normal_queue._queue)
    ytdl = Config.queue._unfinished_tasks - len(Config.queue._queue)
    await m.reply_text(f'NORMAL UPLOAD SERVER:\n\n    •Active Tasks: {result}\n\n    •Pending: {len(Config.normal_queue._queue)}\n\nYtdl Server:\n\n    •Active Tasks: {ytdl}\n\n    •Pending: {len(Config.queue._queue)}', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Close ❌', callback_data='close')]]), quote=True)


@Client.on_message(filters.command("warn"))
async def warn(c, m):
    if m.from_user.id in Config.AUTH_USERS:
        if len(m.command) >= 3:
            try:
                user_id = m.text.split(' ', 2)[1]
                reason = m.text.split(' ', 2)[2]
                await m.reply_text("User Notfied Sucessfully")
                await c.send_message(chat_id=int(user_id), text=reason)
            except:
                 await m.reply_text("User Not Notfied Sucessfully 😔")
    else:
        await m.reply_text(text="You Are Not Admin 😡", quote=True)


@Client.on_message(filters.command("help") & filters.private & filters.incoming)
async def help(c, m, cb=False):
    button = [[
        InlineKeyboardButton('🏡 Home', callback_data='back'),
        InlineKeyboardButton('💸 Donate', callback_data='donate')
        ],[
        InlineKeyboardButton('📛 Close', callback_data='close')
    ]]
    reply_markup = InlineKeyboardMarkup(button)

    if cb:
        try:
            await m.message.edit(
                text=TEXT.HELP_USER.format(m.from_user.first_name),
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        except:
            pass
    else:
        await m.reply_text(
            text=TEXT.HELP_USER.format(m.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )



@Client.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(c, m, cb=False):
    if not cb:
        start = await m.reply_text("Checking...", quote=True)

    button = [
        [
            InlineKeyboardButton('♻️ Developer', url='https://t.me/PinnacleBots'),
            InlineKeyboardButton('🌷 About', callback_data='about')
        ],
        [
            InlineKeyboardButton('❓ Help', callback_data="help"),
            InlineKeyboardButton('💠 Settings', callback_data="setting")
        ],
        [
            InlineKeyboardButton('📛 Close', callback_data="close")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(button)
    if cb:
        try:
            await m.message.edit(
                text=TEXT.START_TEXT.format(m.from_user.first_name), 
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        except:
            pass
    else:
        await start.edit(
            text=TEXT.START_TEXT.format(m.from_user.first_name), 
            disable_web_page_preview=True,
            reply_markup=reply_markup
        ) 


@Client.on_message(filters.command("about") & filters.private & filters.incoming)
async def about(c, m, cb=False):
    restart_time = Config.RESTART_TIME[0]
    time_format = restart_time.strftime("%d %B %Y %I:%M %p")
    button = [[
        InlineKeyboardButton('🏡 Home', callback_data='back'),
        InlineKeyboardButton('💸 Donate', callback_data='donate')
        ],[
        InlineKeyboardButton('📛 Close', callback_data='close')
    ]]
    reply_markup = InlineKeyboardMarkup(button)
    if cb:
        try:
            await m.message.edit(
                text=TEXT.ABOUT.format(time_format),
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        except:
            pass
    else:
        await m.reply_text(
            text=TEXT.ABOUT.format(time_format),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )




@Client.on_message(filters.command(["me", "info", "information"]))
async def info(bot, update):
    if (not update.reply_to_message) and (
        (not update.forward_from) or (not update.forward_from_chat)
    ):
        info = user_info(update.from_user)
    elif update.reply_to_message and update.reply_to_message.forward_from:
        info = user_info(update.reply_to_message.forward_from)
    elif update.reply_to_message and update.reply_to_message.forward_from_chat:
        info = chat_info(update.reply_to_message.forward_from_chat)
    elif (update.reply_to_message and update.reply_to_message.from_user) and (
        not update.forward_from or not update.forward_from_chat
    ):
        info = user_info(update.reply_to_message.from_user)
    else:
        return
    try:
        await update.reply_text(text=info, disable_web_page_preview=True, quote=True)
        logger.info(
            f"Command /Info Used By {update.from_user.first_name} {str(update.from_user.id)} @{update.from_user.username}"
        )
    except Exception as error:
        await update.reply_text(error)


def user_info(user):
    text = "--**User Details :**--\n"
    text += f"\n\n**🦚 First Name :** `{user.first_name}`"
    text += f"\n\n**🐧 Last Name :** `{user.last_name}`" if user.last_name else ""
    text += f"\n\n**👤 User Id :** `{user.id}`"
    text += f"\n\n**👦 Username :** @{user.username}" if user.username else ""
    text += f"\n\n**🔗 User Link :** {user.mention}" if user.username else ""
    try:
        user.is_premium
        text += (
            f"\n\n**🌟 Premium User :** {user.is_premium}"
            if user.is_premium
            else f"\n\n**🌟 Premium User :** False"
        )
    except:
        pass
    text += f"\n\n**💬 DC ID :** `{user.dc_id}`" if user.dc_id else ""
    text += f"\n\n**❌ Is Deleted :** True" if user.is_deleted else ""
    text += f"\n\n**🤖 Is Bot :** True" if user.is_bot else ""
    text += f"\n\n**✅ Is Verified :** True" if user.is_verified else ""
    text += f"\n\n**✖️ Is Restricted :** True" if user.is_verified else ""
    text += f"\n\n**💨 Is Scam :** True" if user.is_scam else ""
    text += f"\n\n**👺 Is Fake :** True" if user.is_fake else ""
    text += f"\n\n**🤔 Is Support :** True" if user.is_support else ""
    text += (
        f"\n\n**📃 Language Code :** {user.language_code}" if user.language_code else ""
    )

    text += f"\n\n**💫 Status :** {user.status}" if user.status else ""
    text += f"\n\nIf you need user id, Then just tap and copy. "
    return text


def chat_info(chat):
    text = "--**Chat Details :**--\n"
    text += f"\n\n**Title :** `{chat.title}`"
    text += f"\n\n**Chat ID :** `{chat.id}`"
    text += f"\n\n**Username :** @{chat.username}" if chat.username else ""
    text += f"\n\n**Type :** `{chat.type}`"
    text += f"\n\n**DC ID :** `{chat.dc_id}`"
    try:
        chat.is_premium
        text += (
            f"\n\n**Premium User :** {chat.is_premium}"
            if chat.is_premium
            else f"\n\n**Premium User :** False"
        )
    except:
        pass

    text += f"\n\n**Is Verified :** True" if chat.is_verified else ""
    text += f"\n\n**Is Restricted :** True" if chat.is_verified else ""
    text += f"\n\n**Is Creator :** True" if chat.is_creator else ""
    text += f"\n\n**Is Scam :** True" if chat.is_scam else ""
    text += f"\n\n**Is Fake :** True" if chat.is_fake else ""
    return text
