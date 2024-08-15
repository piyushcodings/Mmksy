async def fix_ext(newname, realname):
    newname = newname.rsplit(".", 1)
    if len(newname) == 2:
        newname = f"{newname[0][:63 - len(newname[1])]}.{newname[1]}"
    else:
        newname = newname[0][:60]
    newname = newname.replace('/', ' ').replace('#', ' ')
    if not "." in newname and "." in realname:
        extention = realname.rsplit(".", 1)[1]
        if len(extention) in range(2,5):
            newname += f".{extention}"
    elif "." in newname and "." in realname:
        extention = newname.rsplit(".", 1)[1]
        old_ext = realname.rsplit(".", 1)[1]
        if len(extention) not in range(2,5):
            newname += f".{extention}"
    else:
        newname += ".mp4"

    return newname
