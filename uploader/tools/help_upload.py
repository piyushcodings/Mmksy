import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


import os
import aiohttp
import asyncio
import concurrent.futures

def req(url):
    return requests.get(url, allow_redirects=True, stream=True)

async def DetectFileSize(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True) as response:
            data = response.headers.get("content-length", 0)
            return int(data)

    """loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        response = await loop.run_in_executor(pool, req, url)
    data = await response.headers.get("content-length", 0)
    return int(data)"""

async def DownLoadFile(url, file_name, chunk_size, client, ud_type, message_id, chat_id):
    if os.path.exists(file_name):
        os.remove(file_name)

    if not url:
        return file_name

    downloaded_size = 0
    with open(file_name, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)

    return file_name
