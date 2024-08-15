# 
import re
import json
import aiohttp
import urllib.parse
from os import popen
from random import choice
from bs4 import BeautifulSoup
import cloudscraper
from pyrogram.types import *
from re import *


async def direct_link_generator(text_url: str):
    """ direct links generator """
    if not text_url:
        return text_url
    
    elif 'instagram.com' in text_url:
        return await insta(text_url)

    
    elif 'yadi.sk' in text_url:
        return await yandex_disk(text_url)
    elif 'mediafire.com' in text_url:
        return await mediafire(text_url)
    elif 'osdn.net' in text_url:
        return await osdn(text_url)
    elif 'racaty.net' in text_url:
        return await racaty(text_url)
    else:
        return text_url


async def insta(url: str) -> str:
    """ instagram posts direct link generator """

    pattern = re.compile(r"https?://www\.instagram\.com/(tv|reel|p)/([^/]+)/.*")
    try:
        code = next(pattern.finditer(url)).group(2)
        api_url = f'https://instagram.com/p/{code}?__a=1'
        data = (await req(api_url))#['graphql']['shortcode_media']
        print(data)
        isvideo = data['is_video']
        if isvideo:
            return data['video_url'], data['display_url'], data['title']
        else:
            return data['display_url']
    except Exception as e:
        print(f'direct_link {e}')
        return "This is not a proper instagram link please check and send it again. Contact our support for more help"






async def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct links generator
    Based on https://github.com/wldhx/yadisk-direct"""

    try:
        text_url = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        reply = "**Yandex.Disk links was not found**"
        return reply

    api = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={text_url}'
    try:
        dl_url = (json.loads(await req(api)))['href']
        return dl_url
    except KeyError:
        return "**File not found / Download limit reached**"


async def mediafire(url: str) -> str:
    """ MediaFire direct links generator """

    try:
        text_url = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        return "**MediaFire link not found"
    page = BeautifulSoup(await req(text_url), 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    dl_url = info.get('href')
    return dl_url


async def osdn(url: str) -> str:
    """ OSDN direct links generator """

    osdn_link = 'https://osdn.net'
    try:
        text_url = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        return "**No OSDN link found**"
    page = BeautifulSoup(
        await req(text_url), 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    text_url = urllib.parse.unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re.sub(r'm=(.*)&f', f'm={mirror}&f', text_url))
    return urls[0]


async def useragent():
    """useragent random setter"""

    useragents = BeautifulSoup(
        await req(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/'),
        'lxml').findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text


async def racaty(url: str) -> str:
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*racaty\.net\S+', url)[0]
    except IndexError:
        return 'No Racaty.net url found'
    reqs = await req(text_url)
    bss = BeautifulSoup(reqs, 'html.parser')
    op = bss.find('input', {'name':'op'})['value']
    id = bss.find('input', {'name':'id'})['value']
    rep = await req(text_url, data={'op': op,'id': id})
    bss2 = BeautifulSoup(rep, 'html.parser')
    dl_url = bss2.find('a', {'id': 'uniqueExpirylink'})['href']
    return dl_url


async def req(url, data=None):
    async with aiohttp.ClientSession() as session: 
        if data:
            async with session.post(url, data=data) as response:
                return (await response.text()).encode().decode()
        else:
            async with session.get(url) as response:
                return (await response.text()).encode().decode()


