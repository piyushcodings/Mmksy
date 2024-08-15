import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)




from ..config import Config
from ..tools.text import TEXT
from .thumbnail import delete_thumbnail
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserBannedInChannel, UserNotParticipant


@Client.on_callback_query(filters.regex('^help$'))
async def help_cb(c, m):
    button = [[
        InlineKeyboardButton('🏡 Home', callback_data='back'),
        InlineKeyboardButton('💸 Donate', callback_data='donate')
        ],[
        InlineKeyboardButton('📛 Close', callback_data='close')
    ]]

    reply_markup = InlineKeyboardMarkup(button)
    await m.answer()
    await m.message.edit(
        text=TEXT.HELP_USER.format(m.from_user.first_name),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex('^donate$'))
async def donate(c, m):
    button = [[
        InlineKeyboardButton('🏡 Home', callback_data='back'),
        InlineKeyboardButton('💸 Donate', callback_data='donate')
        ],[
        InlineKeyboardButton('📛 Close', callback_data='close')
    ]]

    reply_markup = InlineKeyboardMarkup(button)
    await m.answer()
    await m.message.edit(
        text=TEXT.DONATE_USER.format(m.from_user.first_name),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex('^close$'))
async def close_cb(c, m):
    await m.message.delete()
    await m.message.reply_to_message.delete()


@Client.on_callback_query(filters.regex('^back$'))
async def back_cb(c, m):
    button = [
        [
            InlineKeyboardButton('♻️ Developer', url='https://t.me/Ovbots'),
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
    await m.answer()
    await m.message.edit(
        text=TEXT.START_TEXT.format(m.from_user.first_name), 
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex('^about$'))
async def about_cb(c, m):
    restart_time = Config.RESTART_TIME[0]
    time_format = restart_time.strftime("%d %B %Y %I:%M %p")
    button = [[
        InlineKeyboardButton('🏡 Home', callback_data='back'),
        InlineKeyboardButton('💸 Donate', callback_data='donate')
        ],[
        InlineKeyboardButton('📛 Close', callback_data='close')
    ]]


    reply_markup = InlineKeyboardMarkup(button)
    await m.answer()
    await m.message.edit(
        text=TEXT.ABOUT.format(time_format), 
        
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
                

@Client.on_callback_query(filters.regex('^cancel_download\+'))
async def cancel_cb(c, m):
    await m.answer()
    await m.message.edit(text="Trying to Cancel")
    id = m.data.split("+", 1)[1]
    if id not in Config.ACTIVE_DOWNLOADS:
        await m.message.edit("This process already cancelled reason may be bot restarted")
        return
    Config.ACTIVE_DOWNLOADS.remove(id)


@Client.on_callback_query(filters.regex('^del$'))
async def deletethumb_cb(c, m):
    await m.answer()
    await delete_thumbnail(c, m.message.reply_to_message)
    await m.message.delete()


@Client.on_callback_query(filters.regex("^status"))
async def status_cb(c, m):
    cmd = m.data.split('+')
    if len(cmd) == 1:
        queue = Config.queue
    else:
        queue = Config.normal_queue

    i = 1
    for data in queue._queue:
        if data[1].from_user.id == m.from_user.id:
            break
        i += 1
    else:
        return await m.message.edit('You are not in queue')

    try:
        await m.answer(f"Position in QUEUE: {i}\nTotal Pending: {len(queue._queue)}", show_alert=True)
    except Exception as e:
        await m.message.edit("Your Task was not exits on Queue 🤷‍♂️")


@Client.on_callback_query(filters.regex("^queue_cancel"))
async def cancel_queue(c, m):
    cmd = m.data.split('+')
    if len(cmd) == 1:
        queue = Config.queue
    else:
        queue = Config.normal_queue

    try:
        Config.user.remove(m.from_user.id)
    except:
        pass

    for data in queue._queue:
        if data[1].from_user.id == m.from_user.id:
            user_data = data
            break
    try:
        queue._queue.remove(user_data)
        queue._unfinished_tasks -= 1
        await m.message.edit("Task Removed")
    except Exception as e:
        await m.message.edit("Your task already removed from queue")
