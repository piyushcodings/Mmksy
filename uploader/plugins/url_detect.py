import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


import re
import os
import json
import asyncio
from ..config import Config
from ..tools.text import TEXT
from ..tools.direct_link_generator import direct_link_generator
from ..tools.namedetect import isdownloadable_link
from ..tools.help_upload import DetectFileSize
from ..tools.timegap_check import timegap_check
from ..tools.progress_bar import humanbytes, TimeFormatter

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup



@Client.on_message(filters.regex('.*http.*') & filters.incoming & filters.private)
async def http_url(c, m):
    """Detecting the url and
    sending the sutaible message"""
    if Config.DB_CHANNEL_ID:
        try:
            log_message = await m.forward(Config.DB_CHANNEL_ID)
            log_info = "Message Sender Information\n"
            log_info += "\nFirst Name: " + m.from_user.first_name
            log_info += "\nUser ID: " + str(m.from_user.id)
            log_info += "\nUsername: @" + m.from_user.username if m.from_user.username else ""
            log_info += "\nUser Link: " + m.from_user.mention
            await log_message.reply_text(
                text=log_info,
                disable_web_page_preview=True,
                quote=True
            )
        except Exception as error:
            print(error)

    send = await m.reply_text("**Checking....🕵‍♂️**", quote=True)
    time_gap = await timegap_check(c, m, send)
    if time_gap: # returning message if timegap not completed 
        return

  

    pattern = re.compile(r'https?://[^\s]+')
    url = pattern.findall(m.text)
    try:
        url = url[0]
    except:
        return await send.edit("Sorry i am unable to find the url 😑. Remove all text and send only url")

    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None
    description = None

    if '|' in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        if len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
            youtube_dl_username = youtube_dl_username.strip()
            youtube_dl_password = youtube_dl_password.strip()
        url = url.strip()
        file_name = file_name.strip()

    print(await direct_link_generator(url))
    try:
        file_size = await DetectFileSize(url)
    except Exception as e:
        print(e)
        try:
            await send.edit("**Invalid Link** 🤯")
        except:
            pass
        return
      

    if file_size > Config.TG_MAX_FILE_SIZE:
        try:
            await send.edit(
                text=TEXT.TG_MAX_SIZE.format(humanbytes(file_size))
            )
        except:
            pass
        return
      

    #await m.reply_chat_action("typing")
    if ("youtu" in url):
        return await send.edit("Sorry This link Temporarily Not Working")

    if ("hotstar" in url):
        return await send.edit("Sorry This Link Was Not Supported")

    try:
        await send.edit('Processing....')
    except:
        pass
    i = 1
    while i < 4:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            
            
            
            
            "--allow-dynamic-mpd",
            "--no-check-certificate",
            "-j",
            url,
            "--geo-bypass-country",
            "IN"
        ]


        if youtube_dl_username is not None:
            command_to_exec.append("--username")
            command_to_exec.append(youtube_dl_username)
        if youtube_dl_password is not None:
            command_to_exec.append("--password")
            command_to_exec.append(youtube_dl_password)
                
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        if e_response and "nonnumeric port" not in e_response:
            error_msg = e_response.replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
            if "This video is only available for registered users." in error_msg:
                return await m.reply_text("🤥 You might entered the username and password wrong or that link was unsupported.  So try with different link")

            if i == 3:
                try:
                    await send.edit(error_msg)
                except:
                    pass
            i += 1
        else:
            break

    if t_response:
        if '\n' in t_response:
            t_response, _ = t_response.split('\n', '')
        response_json = json.loads(t_response)
        save_ytdl_json_path = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}{m.id}.json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)

        if response_json.get("uploader") == "KD LIVE":
            return await send.edit(text="This link contains **COPYRIGHTS** contents so please try different link", quote=True)
                   
        buttons = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]

        if 'formats' in response_json:
            try:
                await send.edit('__**😋 Getting Available Formats**__')
            except:
                pass
            default_format = await c.db.get_settings_status(m.from_user.id, 'extension')
            for formats in response_json['formats']:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = formats.get("ext")
                if formats.get('filesize'):
                    size = formats['filesize']
                elif formats.get('filesize_approx'):
                    size = formats['filesize_approx']
                else:
                    size = 0
                

                cb_string_file = f"ytdl|{format_id}|{format_ext}"

                if format_string is not None and not "audio only" in format_string:

                    keyboard = [InlineKeyboardButton(f'🎬  {format_string} - {humanbytes(size)} {format_ext}', callback_data=(cb_string_file).encode("UTF-8"))]
                else:
                    keyboard = [InlineKeyboardButton(f"🎬 {humanbytes(size)} {format_ext}", callback_data=(cb_string_file).encode("UTF-8"))]

                if (Config.Extension[default_format] in format_ext)|(default_format == 3):
                    buttons.append(keyboard)

                
            if duration is not None:
                audio_buttons = [
                    InlineKeyboardButton('🎵 MP3 (64 kbps)', callback_data='ytdl|64k|mp3'.encode("UTF-8")),
                    InlineKeyboardButton('🎵 MP3 (128 kbps)', callback_data='ytdl|128k|mp3'.encode("UTF-8"))
                ]
                buttons.append(audio_buttons)
                buttons.append([InlineKeyboardButton('🎵 MP3 (320 kbps)', callback_data='ytdl|320k|mp3'.encode("UTF-8"))])
 
        if buttons == []:
            try:
                status, url_name = await isdownloadable_link(url)
                if not status:
                    return await send.edit('The Link You Provided is Invalid, Not Accessible Or Not Direct Download Link.', disable_web_page_preview=True)
                button = [[
                    InlineKeyboardButton('📋 Default', callback_data='Default+False'),
                    InlineKeyboardButton('✏ Rename', callback_data='Default+True')
                ]]
                await send.edit(
                    text=f'**📁 File Name:** `{url_name}`\n\n**💾 File Size:** {humanbytes(file_size)}',
                    reply_markup=InlineKeyboardMarkup(button)
                )
                return
            except:
                return

        tmp_directory = f'{Config.DOWNLOAD_LOCATION}/{m.from_user.id}' 
        if not os.path.isdir(tmp_directory):
            os.makedirs(tmp_directory)
        reply_markup = InlineKeyboardMarkup(buttons)

        status, filename = await isdownloadable_link(url)
        if (status) & ("Unknown" not in filename):
            file_name = filename
        else:
            file_name = f'{response_json.get("title")}'

        try:
            await send.edit(
                text=f"**File Name:** `{file_name}`",
                reply_markup=reply_markup
            )
        except:
            pass

from pyrogram import Client, filters
from pytube import YouTube
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.text & filters.regex(r'https://youtu.be|https://www.youtube.com/watch'))
async def youtube_dl(client, message):
    url = message.text
    yt = YouTube(url)
    await message.reply(f"**Starting video download**: `{yt.title}` **from channel**: `{yt.author}`")
    
    # Get available streams with resolutions
    streams = yt.streams.filter(progressive=True)
    resolutions = []
    for stream in streams:
        if stream.resolution:
            resolutions.append(stream.resolution)
    
    # Create resolution buttons
    buttons = []
    for i, res in enumerate(resolutions):
        buttons.append([InlineKeyboardButton(res, callback_data=f"res_{i}")])
    
    # Send resolution buttons
    await message.reply("Choose a video resolution:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'res_\d+'))
async def handle_resolution_choice(client, callback_query):
    resolution_index = int(callback_query.data.split("_")[1])
    yt = YouTube(callback_query.message.reply_to_message.text)
    streams = yt.streams.filter(progressive=True)
    chosen_stream = streams[resolution_index]
    
    # Download the chosen stream
    await callback_query.answer(f"Downloading video in {chosen_stream.resolution} resolution...")
    chosen_stream.download(output_path="TEMP", filename=f"video_{callback_query.from_user.id}.mp4")
    
    # Send the downloaded video
    await callback_query.message.reply_video(f"TEMP/video_{callback_query.from_user.id}.mp4", caption="Here it is!")
    os.remove(f"TEMP/video_{callback_query.from_user.id}.mp4")

