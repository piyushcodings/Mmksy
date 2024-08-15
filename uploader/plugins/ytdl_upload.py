import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)



import os
import re
import time
import json
import random
import shutil
import asyncio

from ..config import Config
from collections import defaultdict
from ..tools.get_duration import get_duration
from ..tools.thumbnail_fixation import fix_thumb
from ..tools.extention import fix_ext
from ..tools.namedetect import isdownloadable_link
from ..tools.take_screen_shot import take_screen_shot

from ..tools.timegap_check import timegap_check
from ..tools.progress_bar import progress_bar, TimeFormatter, humanbytes
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from pyrogram.errors import FloodWait



@Client.on_callback_query(filters.regex('^ytdl'))
async def ytdl(c, m):
    await m.answer()
    cmd, ytdl_format, ytdl_ext = m.data.split('|')
    time_gap = await timegap_check(c, m, m.message)
    if time_gap: # returning message if timegap not completed 
        return
    buttons = [[
        InlineKeyboardButton('📋 Default', callback_data=f'dl|{ytdl_format}|{ytdl_ext}|False'),
        InlineKeyboardButton('✏ Rename', callback_data=f'dl|{ytdl_format}|{ytdl_ext}|True')
    ]]
    await m.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex('^dl'))
async def ytdl_upload(c, m):
    await m.answer()
    time_gap = await timegap_check(c, m, m.message)
    if time_gap: # returning message if timegap not completed 
        return

    cmd, status = m.data.rsplit('|', 1)
    status = False if status == 'False' else True
    newname = None
    if status:
        new_name = await c.ask(chat_id=m.from_user.id, text='Send me the new FileName', filters=filters.text)
        newname = new_name.text
        await new_name.delete()
        await new_name.request.delete()

    if m.from_user.id in Config.user:
        return await m.message.edit(text="Your Task was on Queue Please wait untill it was completed.")
    try:
        Config.queue.put_nowait((c, m, newname))
        Config.user.append(m.from_user.id)
    except asyncio.QueueFull:
        await m.message.edit("Sorry I Am Very Busy Now. Please Try Some Time Later")
    else:
        if not Config.tasks:
            for i in range(Config.WORKERS):
                task = asyncio.create_task(ytdl_worker(f"worker-{i}", Config.queue))
                Config.tasks.append(task)
        await asyncio.sleep(1)
        if len(Config.queue._queue) != 0:
            buttons = [[
                InlineKeyboardButton("Server Status 📊", callback_data="status")
                ],[
                InlineKeyboardButton("Cancel ⛔", callback_data="queue_cancel")
            ]]
            msg = await m.message.edit(text="Your Task added to **QUEUE**.\nThis method was implemented to reduce the overload on bot. So please cooperate with us.\n\n Press the following button to check the position in queue", reply_markup=InlineKeyboardMarkup(buttons))


async def ytdl_worker(name, queue):
    while True:
        try:

            # get a work item out of queue
            c, m, newname = await queue.get()
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

            cmd, ytdl_format, ytdl_ext, _ = m.data.split('|')
            tmp_directory_for_each_user = f'{Config.DOWNLOAD_LOCATION}/{m.from_user.id}{time.time()}'
            if not os.path.isdir(tmp_directory_for_each_user):
                os.makedirs(tmp_directory_for_each_user)

            thumb_image_path = f'{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg'
            ytdl_json_path = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}{m.message.reply_to_message.id}.json"
            try:
                with open(ytdl_json_path, "r", encoding="utf8") as f:
                    response_json = json.load(f)
            except FileNotFoundError as e:
                await m.message.edit(text="**Send the link again** 😊")
                continue

            Config.TIME_GAP1[m.from_user.id] = time.time()
            pattern = re.compile(r'https?://[^\s]+')
            url = pattern.findall(m.message.reply_to_message.text)
            url = url[0].split('|')[0]
            youtube_dl_username = None
            youtube_dl_password = None
            file_name = None

            if '|' in m.message.reply_to_message.text:
                url_parts = m.message.reply_to_message.text.split("|")
                if len(url_parts) == 2:
                    file_name = url_parts[1].strip()
                if len(url_parts) == 4:
                     file_name = url_parts[1].strip()
                     youtube_dl_username = url_parts[2].strip()
                     youtube_dl_password = url_parts[3].strip()
                url = url.strip()

            try:
                await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Downloading 📥")
                await m.message.edit(text="__Trying To Download....📥__")
            except:
                pass

            caption_name = file_name
            if file_name is None:
                status, filename = await isdownloadable_link(url)
                if (status) & ("Unknown" not in filename):
                    file_name = filename
                    caption_name = filename
                else:
                    caption_name = response_json.get("title")
                    file_name = f'{response_json.get("title")[:60 - len(ytdl_ext)]}.{ytdl_ext}'
            try:
                await m.message.edit(f"**File Name:** {caption_name}\n\n **Downloading...📥**")
            except:
                pass

            download_directory = f'{tmp_directory_for_each_user}/{file_name}'
            command_to_exec = []
            if ytdl_ext == "mp3": 
                command_to_exec = [
                    "yt-dlp",
                    "-c",
                    "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
                    "--hls-prefer-ffmpeg", 
                    "--extract-audio",
                    "--audio-format", ytdl_ext,
                    "--audio-quality", ytdl_format,
                    url,
                    "-o", download_directory
                ]
            else:
        
                minus_f_format = ytdl_format + "+bestaudio[ext=m4a]/best"
                command_to_exec = [
                    "yt-dlp",
                    "-c",
                    "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
                    "--embed-subs",
                    "-f", minus_f_format,
                    "--hls-prefer-ffmpeg", url,
                    "-o", download_directory,
                    "--geo-bypass-country",
                    "IN"
                ]

            if youtube_dl_username is not None:
                command_to_exec.append("--username")
                command_to_exec.append(youtube_dl_username)
            if youtube_dl_password is not None:
                command_to_exec.append("--password")
                command_to_exec.append(youtube_dl_password)
            command_to_exec.append("--no-warnings")

            process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()

            ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
            if e_response and ad_string_to_replace in e_response:
                error_message = e_response.replace(ad_string_to_replace, "")
                await m.message.edit(text=error_message)
                continue

            if t_response:
                os.remove(ytdl_json_path)
                file_size = Config.TG_MAX_FILE_SIZE + 1
                try:
                    file_size = os.stat(download_directory).st_size
                except FileNotFoundError as exc:
                    files = os.listdir(f'{tmp_directory_for_each_user}/')
                    if len(files) == 0:
                        try:
                            try:
                                 shutil.rmtree(tmp_directory_for_each_user)
                                 os.remove(thumb_image_path)
                            except:
                                 pass
                            try:
                                await m.message.edit("**Download Failed!!**\n\n Try to select other format if again fail with other formats also try other link.")
                                await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** DOWNLOAD FAILED")
                            except:
                                 pass
                            del Config.TIME_GAP1[m.from_user.id]
                        except:
                            pass
                        continue

                    try:
                        download_directory = f"{tmp_directory_for_each_user}/{files[0]}"                     
                        os.stat(download_directory).st_size
                    except FileNotFoundError:
                        try:
                            try:
                                 shutil.rmtree(tmp_directory_for_each_user)
                                 os.remove(thumb_image_path)
                            except:
                                 pass
                            try:
                                await m.message.edit("**Download Failed!!**\n\n Try to select other format if again fail with other formats also try other link.")
                                await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** DOWNLOAD FAILED")
                            except:
                                 pass
                            del Config.TIME_GAP1[m.from_user.id]
                        except:
                            pass
                        continue

                try:
                    await m.message.edit('**File Downloaded Successfully**')
                except:
                    pass
                settings = await c.db.get_all_settings(m.from_user.id)
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

                if newname:
                    fixed_name = await fix_ext(newname, os.path.basename(download_directory))
                    new_dir = f"{tmp_directory_for_each_user}/{fixed_name}"
                    os.rename(download_directory, new_dir)
                    download_directory = new_dir

                try:
                    await m.message.edit(text=f"**FileName:** `{caption_name}`\n\nPreparing to Upload")
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
                        thumbnail_location = None
                        if not as_file:
                            try:
                                thumbnail_location = await take_screen_shot(download_directory, tmp_directory_for_each_user, random.randint(0, duration - 1))
                            except Exception as e:
                                print(e)
                                thumbnail_location = None

                width, height, thumbnail = await fix_thumb(thumbnail_location)
                try:
                    caption = settings['custom_caption']
                    caption = caption.replace("{}", "")
                    caption_duration = TimeFormatter(duration * 1000)
                    caption_size = humanbytes(os.path.getsize(download_directory))
                    final_caption = caption.format_map(defaultdict(str, filename=caption_name, duration=caption_duration, filesize=caption_size)) if caption else ""
                    final_caption = final_caption[:1023]
                except:
                    final_caption = f"**{file_name}**"

                try:
                    await m.message.edit(text="Trying to upload....📤")
                except:
                    pass
                start_time = time.time()
                if ytdl_ext == "mp3":
                    try:
                        final_media = await c.send_audio(
                            chat_id=m.from_user.id, 
                            audio=download_directory,
                            caption=final_caption,
                            duration=duration,
                            performer=response_json["uploader"] if 'uploader' in response_json else None, 
                            title=response_json["title"] if 'title' in response_json else None,
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

                if (not as_file) & (ytdl_ext != "mp3"):
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
 
                if (as_file) & (ytdl_ext != "mp3"):
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
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\nID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** FloodWait {e}")
                        except:
                            pass
                        del Config.TIME_GAP1[m.from_user.id]
                        continue
                    except Exception as e:
                        try:
                            await m.message.edit(f"--Error:--\n{e}")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\nID:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Error while uploading {e}")
                        except:
                            pass
                        del Config.TIME_GAP1[m.from_user.id]
                        continue

                if (final_media is None)|(id not in Config.ACTIVE_DOWNLOADS):
                    try:
                        if not id in Config.ACTIVE_DOWNLOADS:
                            await msg.edit("Process Cancelled Successfully ✅")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Cancelled By user")
                        elif time.time() - start_time > 1200:
                            await msg.edit("Process Cancelled Due to timeout of 20min.")
                            await trace.edit(text=f"**Name:** {m.from_user.mention(style='md')}\n\n**id:** {m.from_user.id}\n\n**UserName:** @{m.from_user.username}\n\n**Link:** {m.message.reply_to_message.text}\n\n**Status:** Cancelled due to TimeOut")
                        else:
                            await msg.edit("**Upload Failed!!**\n\nSome recently uploaded files are unable to upload so please try after some time.")
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
            await m.message.edit(f"**Error:** {e}")
            await c.send_message(chat_id=-1002016424677, text=f"Ytdl error {e}")
        finally:
            Config.queue.task_done()

        if id in Config.ACTIVE_DOWNLOADS:
            asyncio.create_task(complete_process(c, m.message.reply_to_message))


async def complete_process(c, m):
    Config.TIME_GAP2[m.from_user.id] = time.time()
    started_time = Config.TIME_GAP1[m.from_user.id]
    end_time = Config.TIME_GAP2[m.from_user.id]
    del Config.TIME_GAP1[m.from_user.id]
    time_consumed = time.time() - started_time

    send_message = await m.reply_text(text=f"Please wait {TimeFormatter(round(end_time + time_consumed - time.time()) * 1000)}, because i am reseting")
    Config.timegap_message[m.from_user.id] = send_message
    # editing the message untill time gap ended 
    while round(time.time() - end_time) < time_consumed:
        try:
            await send_message.edit(text=f"Please wait {TimeFormatter(round(end_time + time_consumed - time.time()) * 1000)}, because i am reseting")
        except Exception as e:
            pass
        await asyncio.sleep(3)
    await send_message.delete()
    await m.reply_text("**You Can Send Me New Task Now**")
    del Config.TIME_GAP2[m.from_user.id]



            
