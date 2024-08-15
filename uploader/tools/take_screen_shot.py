import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)



import os
import time
import asyncio
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


#################################################################################################################################################################################################################################################################################################

async def take_screen_shot(video_file, output_directory, ttl):

    out_put_file_name = output_directory + "/" + str(time.time()) + ".jpg"
    file_genertor_command = ["ffmpeg", "-ss", str(ttl), "-i", video_file, "-vframes", "1", out_put_file_name]

    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


#################################################################################################################################################################################################################################################################################################

async def generate_screen_shots(video_file, output_directory, min_duration, no_of_photos):
    metadata = extractMetadata(createParser(video_file))
    duration = 0
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
    if duration > min_duration:
        images = []
        ttl_step = duration // no_of_photos
        current_ttl = ttl_step
        for looper in range(0, no_of_photos):
            ss_img = await take_screen_shot(video_file, output_directory, current_ttl)
            current_ttl = current_ttl + ttl_step
            images.append(ss_img)
        return images
    else:
        return None


#################################################################################################################################################################################################################################################################################################
