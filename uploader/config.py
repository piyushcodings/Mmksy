import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(logging.WARNING)

import asyncio
from collections import defaultdict


class Config:
    ACTIVE_DOWNLOADS = []
    API_ID = int("10412514")
    API_HASH = "4d55a7064ad72adcfa8944f505453a8c"

    AUTH_USERS =  [int(i) for i in os.environ.get("AUTH_USERS", "1620169470").split(" ")]
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6192974593:AAGZxFkcgaBh9xJyHLGjCvPTOnY6A_sIc2s")
    DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://sahaynitin2006:54xUl2DdnXQPntZx@cluster0.s8nwow5.mongodb.net/?retryWrites=true&w=majority")
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", "-1001720609021"))
    PROCESS_MAX_TIMEOUT = 3600
    RESTART_TIME = []
    TG_MAX_FILE_SIZE = 3980000000
    TIME_GAP1 = {}
    TIME_GAP2 = {}
    timegap_message = {}
    TRACE_CHANNEL = os.environ.get("DB_CHANNEL_ID", "-1001720609021")
    last_edit = defaultdict(lambda: 0)
    SESSION_STRING = os.environ.get(
        "SESSION_STRING",
        "BQBbrFbGJmkNu1iSnJYuStz9JfxXY_s_j0cr0SxW4_9AVClK5D4WDymx-voNloEu28UjyPBLeckDsEQUBhHKebROcA4ZOcnpTLxa7jmwQMSct88nbDKPcswOhvtcaM-uMUlwUU51aCfl0jm5q9xmgVkdFO2htVKeEYasC642mlKmtnl0h44oOBqwGsy7KloPzxwB58yhxn3OWFF0bKqt1PyDl-rdXQ_gKVG3Z96id5I_tUeKl5mn89xDEZxMhbjD54S-h1O8MgB_Ix2xzVKy5GK9GobmDBS6ib_s_gp4KZOWQW_uG5N0grgNDQMnMjWXz2hcYVwB3yM38QljSTEqD4O9YJHS_gAHO2_PCx1tuZFB98u3KSNpyObkXcrgEHE9MR5clD3Vqr7rLZE0Dy5FMVBmnWVNf_HK-cggxsjVbxRXwY8QND309LnmVpdsc865XEZ5N77r0EAXBLo6B4BxWDqO6GnJj6qhzgAAAAB1aFXoAA",
    )

    # QUEUE
    SESSION_NAME = os.environ.get("SESSION_NAME", "TellyBotzz")
    WORKERS = 5
    QUEUE_MAXSIZE = 20
    normal_queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
    queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
    normal_tasks = []
    tasks = []
    user = []
    Library = ['aria2', 'aiohttp']
    Extension = ['mp4', 'webm', 'mkv', 'all']
