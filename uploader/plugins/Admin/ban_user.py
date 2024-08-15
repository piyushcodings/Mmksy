import logging
import traceback

from pyrogram import filters, Client
from uploader.config import Config

log = logging.getLogger(__name__)


@Client.on_message(filters.private & filters.command("ban_user") & filters.user(Config.AUTH_USERS))
async def ban(c, m):

    if len(m.command) == 1:
        await m.reply_text(
            "Use this command to ban any user from the bot.\n\nUsage:\n\n`/ban_user user_id "
            "ban_duration ban_reason`\n\nEg: `/ban_user 1234567 28 You misused me.`\n This will "
            "ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} day(s) for the reason {ban_reason}."

        try:
            text = f'**--Message From Admin {m.from_user.first_name}--**'
            text += f"\n\nYou are banned to use this bot for **{ban_duration}** day(s) for "
            text += f"the reason __{ban_reason}__ \n\n**Message from the admin**"

            await c.send_message(
                user_id,
                text
            )
            ban_log_text += "\n\nUser notified successfully!"
        except Exception as e:
            ban_log_text += (
                f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
            )
        await c.db.ban_user(user_id, ban_duration, ban_reason)
        await m.reply_text(ban_log_text, quote=True)
    except Exception as e:
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True,
        )

