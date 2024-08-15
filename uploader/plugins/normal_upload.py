
import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


import re
import time
import math
import aiohttp
import asyncio
import random 

from ..config import Config
from collections import defaultdict
from ..tools.get_duration import get_duration
from ..tools.extention import fix_ext
from ..tools.thumbnail_fixation import fix_thumb
from ..tools.namedetect import isdownloadable_link
from ..tools.take_screen_shot import take_screen_shot

from ..tools.take_screen_shot import take_screen_shot
from ..tools.timegap_check import timegap_check
from ..tools.progress_bar import progress_bar, TimeFormatter, humanbytes
from .ytdl_upload import complete_process
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait


@Client.on_callback_query(filters.regex('^Default\+'))
async def default(c, m):
    await m.answer()
    await m.message.edit('**Processing....**')
    cmd, status = m.data.split('+')
    status = True if status == 'True' else False 
    pattern = re.compile(r'https?://[^\s]+')
    url = pattern.findall(m.message.reply_to_message.text)
    url = url[0]

    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

    if '|' in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0].strip()
            file_name = url_parts[1].strip()
        if len(url_parts) == 4:
            url = url_parts[0].strip()
            file_name = url_parts[1].strip()
            youtube_dl_username = url_parts[2].strip()
            youtube_dl_password = url_parts[3].strip()
        url = url.strip()

    sts, url_name = await isdownloadable_link(url)
    caption_name = url_name
    url_name = await fix_ext(url_name, url_name)
    if not sts:
        return await m.message.edit('The Link You Provided is Invalid, Not Accessible Or Not Direct Download Link.', disable_web_page_preview=True)

    if status:
        await m.message.edit(text=f"**FileName:** `{url_name}`\n\n**Send Me New Name**")
        new_file_name = await c.listen(chat_id=m.from_user.id, filters=filters.text)
        url_name = await fix_ext(new_file_name.text, url_name)
        caption_name = new_file_name.text
        await new_file_name.delete()

    if m.from_user.id in Config.user:
        return await m.message.edit(text="Your Task was on Queue Please Wait Untill it Was Completed.")
    try:
        Config.normal_queue.put_nowait((c, m, url, url_name, caption_name))
        Config.user.append(m.from_user.id)
    except asyncio.QueueFull:
        await m.message.edit("Sorry I Am Very Busy Now. Please Try Some Time Later")
    else:
        if not Config.normal_tasks:
            for i in range(Config.WORKERS):
                task = asyncio.create_task(worker(f"worker-{i}", Config.normal_queue))
                Config.normal_tasks.append(task)
        await asyncio.sleep(1)
        if len(Config.normal_queue._queue) != 0:
            buttons = [[
                InlineKeyboardButton("Server Status 📊", callback_data="status+1")
                ],[
                InlineKeyboardButton("Cancel ⛔", callback_data="queue_cancel+1")
            ]]
            await m.message.edit(text="Your Task Added To **QUEUE**.\nThis Method Was implemented To Reduce The Overload On Bot. So Please Cooperate With Us.\n\n Press The Following Button To Check The Position in Queue", reply_markup=InlineKeyboardMarkup(buttons))


async def worker(name, queue):
    while True:
        try:
            c, m, url, url_name, caption_name = await Config.normal_queue.get()
            Config.user.remove(m.from_user.id)
          

            

            try:
                await m.message.edit('**Processing....⏳**')
            except:
                pass

            id = f'{m.message.id}/{m.from_user.id}'
            try:
                trace = await c.send_message(chat_id=Config.TRACE_CHANNEL, text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** `{m.from_user.id}`\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Checking.")
            except:
                pass
            Config.ACTIVE_DOWNLOADS.append(id)

            thumb_image_path = f'{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg'
            tmp_directory_for_each_user = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}"
            if not os.path.isdir(tmp_directory_for_each_user):
                 os.makedirs(tmp_directory_for_each_user) 
            download_directory = f"{tmp_directory_for_each_user}/{url_name}"
            Config.TIME_GAP1[m.from_user.id] = time.time()
            settings = await c.db.get_all_settings(m.from_user.id)
            async with aiohttp.ClientSession() as session: 
                c_time = time.time()
                try:
                    await m.message.edit(text="__Trying to Download....📥__") 
                    await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Downloading 📥") 
                except:
                    pass
                try:
                    sts = await download_coroutine(c, m, session, url, download_directory, c_time, id)
                        
                    if not sts:
                        try:
                            del Config.TIME_GAP1[m.from_user.id]
                        except:
                            pass
                        continue
                except Exception as e:
                    try:
                        del Config.TIME_GAP1[m.from_user.id]
                    except:
                        pass
                    if str(e) == '':
                        continue
                    try:
                        await m.message.edit(f"**Error:**\n\n{e}")
                        await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Failed to aiohttp due to {e}") 
                    except:
                        pass
                    continue

            if not os.path.exists(download_directory):
                if id in Config.ACTIVE_DOWNLOADS:
                    try:
                        await m.message.edit("**Download Failed!!**")
                        await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\nID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** **Download Failed**")
                    except:
                        pass
                    try:
                        del Config.TIME_GAP1[m.from_user.id]
                    except:
                        pass
                    continue
                else:
                    try:
                        await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\nID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Process Cancelled by user")
                        await m.message.edit(text="__Process Cancelled Successfully ✅__")
                    except:
                        pass
                    try:
                        del Config.TIME_GAP1[m.from_user.id]
                    except:
                        pass
                    continue
            else:
                try:
                    await m.message.edit('**File Downloaded Successfully**')
                except:
                    pass
               # screenshots = settings['screen_shot']
                #samplevideo = settings['sample_video']
                as_file = settings['upload_as_file']
                thumb_id = settings['permanent_thumb']

                try:
                    duration = await get_duration(download_directory)
                except:
                    duration = "Failed to get duration"

                if isinstance(duration, str):
                    duration = 0               

                try:
                    await m.message.edit(text=f"**FileName:** `{caption_name}`\n\n__Preparing to upload__")
                    await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Uploading 📤")
                except:
                    pass


                thumbnail_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"
                # if thumbnail not exists checking the database for thumbnail
                if not os.path.exists(thumbnail_location):
                    if thumb_id:
                        thumb_msg = await c.get_messages(m.from_user.id, thumb_id)
                        try:
                            thumbnail_location = await thumb_msg.download(file_name=thumbnail_location)
                        except:
                            await c.db.update_settings_status(m.from_user.id, 'permanent_thumb', '')
                            thumbnail_location = None
                    else:
                        if as_file:
                            thumbnail_location = None
                        if not as_file:
                            try:
                                thumbnail_location = await take_screen_shot(download_directory, tmp_directory_for_each_user, random.randint(0, duration - 1))
                            except Exception as e:
                                print(f"Error while taking screenshot for thumb due to {e}")
                                thumbnail_location = None

                width, height, thumbnail = await fix_thumb(thumbnail_location)
                try:
                    caption = settings['custom_caption']
                    caption_duration = TimeFormatter(duration * 1000)
                    caption_size = humanbytes(os.path.getsize(download_directory))
                    caption = caption.replace("{}", "")
                    final_caption = caption.format_map(defaultdict(str, filename=caption_name, duration=caption_duration, filesize=caption_size)) if caption else ''
                    final_caption = final_caption[:1023]
                except:
                    final_caption = f"**{url_name}**"

                try:
                    await m.message.edit(text="__Trying to Upload....📤__")
                except:
                    pass
                start_time = time.time()
                if not as_file:
                    try:
                        final_media = await c.send_video(
                            chat_id=m.from_user.id,
                            video=download_directory,
                            caption=final_caption,
                            duration=duration,
                            width=width,
                            height=height,
                            supports_streaming=True,
                            thumb=thumbnail,
                            reply_to_message_id=m.message.reply_to_message.id,
                            progress=progress_bar,
                            progress_args=("Upload Status:", start_time, c, m.message, id)
                        )
                        await m.message.delete()
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        try:
                            await m.message.edit("Flood Wait try again later this file")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**ID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** FloodWait {e}")
                        except:
                            pass
                        del Config.TIME_GAP1[m.from_user.id]
                        continue 
                    except Exception as e:
                        try:
                            await m.message.edit(f"--Error:--\n{e}")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**ID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Error while uploading {e}")
                        except:
                            pass
                        del Config.TIME_GAP1[m.from_user.id]
                        continue 
 
                if as_file:
                    try:
                        final_media = await c.send_document(
                            chat_id=m.from_user.id,
                            document=download_directory,
                            thumb=thumbnail,
                            caption=final_caption,
                            reply_to_message_id=m.message.reply_to_message.id,
                            progress=progress_bar,
                            progress_args=("Upload Status:", start_time, c, m.message, id)  
                        )
                        await m.message.delete()
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        try:
                            await m.message.edit("Flood Wait try again later this file")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**ID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** FloodWait {e}")
                        except:
                            pass
                        del Config.TIME_GAP1[m.from_user.id]
                        continue 

                    except Exception as e:
                        try:
                            await m.message.edit(f"--Error:--\n{e}")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**ID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Error while uploading {e}")
                        except:
                            pass
                        del Config.TIME_GAP1[m.from_user.id]
                        continue 

                if (final_media is None)|(id not in Config.ACTIVE_DOWNLOADS):
                    try:
                        if not id in Config.ACTIVE_DOWNLOADS:
                            await m.message.edit("__Process Cancelled Successfully ✅__")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Cancelled By user")
                        elif time.time() - start_time > 1200:
                            await m.message.edit("Process Cancelled Due to timeout of 20min.")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Cancelled due to TimeOut")
                        else:
                            await m.message.edit("**Upload Failed!!**\n\nSome recently uploaded files are unable to upload so please try after some time.")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** upload Failed")
                    except:
                        pass
                    try:
                        del Config.TIME_GAP1[m.from_user.id]
                    except:
                        pass
                    continue

                try:
                    await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Uploaded Sucessfully ✅")
                    await m.message.delete()
                except:
                    pass
        except Exception as e:
            await c.send_message(chat_id=-1001720609021, text=e)
            await m.message.edit(f"**Error:** {e}")

        finally:
            Config.normal_queue.task_done()
        if id in Config.ACTIVE_DOWNLOADS:
            asyncio.create_task(complete_process(c, m.message.reply_to_message))


async def download_coroutine(c, m, session, url, download_directory, start, id):
    downloaded = 0
    display_message = ""
    last_edit = 0
    async with session.get(url, timeout=Config.PROCESS_MAX_TIMEOUT) as response:
        try:
            total_length = int(response.headers["Content-Length"])
            content_type = response.headers["Content-Type"]
        except:
            await m.message.edit(
                "**Download Failed**\n\n"
                "Unable to extract Size. Please try again later."
                "If again fails try different link."
            )
            return False
  
        if "text" in content_type and total_length < 500:
            await response.release()
            return True

        try:
            await m.message.edit(
                f"__**Initiating Download**__\n\n"
                f"**🔗 URL:** {url}\n\n"
                f"**📁 File Name:** {os.path.basename(download_directory)}\n\n"
                f"**💽 File Size:** {humanbytes(total_length)}",
                disable_web_page_preview=True
                )
        except:
            pass

        with open(download_directory, "wb") as f_handle:
            while True:
                try:
                    chunk = await response.content.read(5*1024*1024)
                except:
                    break

                if not chunk:
                    break

                f_handle.write(chunk)
                downloaded += len(chunk)
                now = time.time()
                diff = now - start

                if not id in Config.ACTIVE_DOWNLOADS:
                    try:

                        await m.message.edit(
                            "__Process Cancelled Successfully ✅__"
                        )
                    except:
                        pass
                    await c.stop_transmission()
                    await response.release()
                    return False

                if now - start > 1800:
                    try:

                        await m.message.edit(
                            "Process Cancelled\n\n**Reason: Timeout Error**"
                        )
                    except:
                        pass
                    await c.stop_transmission()
                    await response.release()
                    return False

                if now - last_edit > 5 or downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = round(
                        (total_length - downloaded) / speed) * 1000
                    estimated_total_time = elapsed_time + time_to_completion
                    try:
                        progress = "[{}{}]".format(
                            ''.join(["▰" for i in range(math.floor(percentage / 10))]),
                            ''.join(["▱" for i in range(10 - math.floor(percentage / 10))])
                        )
                        txt =""
                        txt += f"__**𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀:** {round(percentage, 2)}%__\n\n"
                        txt += f"{progress}\n\n"
                        txt += f"**➩ Speed:** `{humanbytes(speed)}/s`\n\n"
                        txt += f"**➩ Done:** `{humanbytes(downloaded)}`\n\n"
                        txt += f"**➩ Size:** `{humanbytes(total_length)}`\n\n"
                        txt += f"**➩ Time Left:** `{TimeFormatter(time_to_completion)}`\n\n"
                        buttons = [[
                            InlineKeyboardButton(
                                "𝖢𝖺𝗇𝖼𝖾𝗅 🚫", callback_data=f"cancel_download+{id}"
                            )
                        ]]
                        await m.message.edit(
                            text=txt,
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                        last_edit = time.time()
                    except:
                        pass

        await response.release()
        return True


@Client.on_callback_query(filters.regex('^cancel_gid\+'))
async def cancel_gid(c, m):
    await m.answer()
    gid = m.data.split('+')[1]
    aria2 = await starting_aria2()
    file = aria2.get_download(gid)
    file.remove(force=True)
