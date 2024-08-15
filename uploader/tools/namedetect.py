import aiohttp
import urllib


async def isdownloadable_link(link):
    """Return (downloadable or not, filename)"""
    
    filename = 'Unknown'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link, timeout=aiohttp.ClientTimeout(total=30)) as response:
                content_type = response.content_type
                filesize = int(response.headers.get("Content-Length", 0))
                if 'text' in content_type.lower() or 'html' in content_type.lower() or filesize < 100:
                    return False, filename
                else:
                    try:
                        filename = response.content_disposition.filename
                    except:
                        pass
                    
                    if not filename:
                        filename = response._real_url.name
                    if not '.' in filename:
                        # add ext
                        filename += '.' + content_type.split('/')[-1]
                    filename = filename.replace('_', ' ')
                    filename = urllib.parse.unquote(filename)
                    return True, filename

    except Exception as e:
        print(e)
        return False, filename

