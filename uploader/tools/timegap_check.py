import datetime
from ..config import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserBannedInChannel, UserNotParticipant


async def timegap_check(c, m, sent):
    """Checking the time gap is completed or not 
    and checking the parallel process"""

    try:
        chat = await c.get_chat_member('PinnacleBots', m.from_user.id)
        if chat.status=='kicked':
            await sent.edit('😡 You Are Banned 😝')
            return True

    except UserNotParticipant:
        button = [[InlineKeyboardButton('🔰 Join Now 🔰', url='https://t.me/PinnacleBots')]]
        markup = InlineKeyboardMarkup(button)
        await sent.edit(text=f"👋 Hi {m.from_user.mention(style='md')},\n\n**Please Join My Updates Channel to use this Bot!**\n\nDue to Overload, Only Channel Subscribers can use the Bot!", reply_markup=markup)
        return True

    except Exception as e:
        await sent.edit("**Something went Wrong. Contact my Devloper [PinaccleBots](https://t.me/PinnacleSupport)", disable_web_page_preview=True)
        return True

    if not await c.db.is_user_exist(m.from_user.id):
        await c.db.add_user(m.from_user.id)
        await c.send_message(
            Config.DB_CHANNEL_ID,
            f"New User {m.from_user.mention} started."
        )

    ban_status = await c.db.get_ban_status(m.from_user.id)
    if ban_status["is_banned"]:
        if (datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])).days > ban_status["ban_duration"]:
            await c.db.remove_ban(m.from_user.id)
        else:
            banned_text = "--**🛑 YOU ARE BANNED 🛑**--\n\n"
            banned_text += '**Banned Date:** '
            banned_text += f"`{ban_status['banned_on']}`\n"
            banned_text += '**Banned Duration:** '
            banned_text += f"{ban_status['ban_duration']} day(s)\n"
            banned_text += '**Reason:** '
            banned_text += f"__**{ban_status['ban_reason']}**__\n\n"
            banned_text += f"if you think this is a mistake contact Devloper [Shivam](https://t.me/Legend_Shivam_7)"
            await sent.edit(banned_text)
            return True

    if m.from_user.id == Config.AUTH_USERS:
        # If the user is the owner, no time gap is applied
        return False

    if m.from_user.id in Config.TIME_GAP1:
        # If one process is running
        text = "**✋ Please wait untill the previous task complete.**\n\n"
        text += "After previous task completed there will be a time gap.\n"
        text += "__Time gap will be same as time consumed by your previous task ⏱.__"
        await sent.edit(
            text=text
            
        )
        return True

    elif m.from_user.id in Config.TIME_GAP2:
        # if time gap not completed
        msg = Config.timegap_message[m.from_user.id]
        await sent.delete()
        await msg.reply_text(
            text="**👆 See This Message And don't disturb me again 😏**",
            
            quote=True
        )
        return True
    else:
        return False
