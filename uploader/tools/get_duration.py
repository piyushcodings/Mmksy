import asyncio

async def get_duration(file_link):
    duration_cmd = ['ffprobe', '-headers', 'IAM:', '-i', file_link, '-v', 'error', '-show_entries',
                    'format=duration', '-of', 'csv=p=0:s=x', '-select_streams', 'v:0', ]

    process = await asyncio.create_subprocess_exec(
        *duration_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    out, err = await process.communicate()

    out = out.decode().strip()
    if not out:
        return err.decode()
    duration = round(float(out))
    if duration:
        return duration
    return 'No duration!'
