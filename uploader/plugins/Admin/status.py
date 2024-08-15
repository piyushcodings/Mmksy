from pyrogram import filters, Client
from uploader.config import Config


@Client.on_message(filters.private & filters.command("status") & filters.user(Config.AUTH_USERS))
async def sts(c, m):
    total_users = await c.db.total_users_count()
    bot_updates = await c.db.get_user_update()
    i = 0
    async for user in bot_updates:
        i += 1
    text = f"Total user(s) till date: {total_users}\n\n"
    text += f"Bot Updates Active Users: {i}"
    await m.reply_text(text=text, quote=True)
