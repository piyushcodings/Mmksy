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
    API_ID = int("23907288")
    API_HASH = "f9a47570ed19aebf8eb0f0a5ec1111e5"

    AUTH_USERS =  [int(i) for i in os.environ.get("AUTH_USERS", "5605747843").split(" ")]
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7506408964:AAFB-iKQtMOY-pIx9noUNY5lApgKorew4l4")
    DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://gojomerge:5exfugtttf@cluster0.mefkdax.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", "-1002249908184"))
    PROCESS_MAX_TIMEOUT = 3600
    RESTART_TIME = []
    TG_MAX_FILE_SIZE = 3980000000
    TIME_GAP1 = {}
    TIME_GAP2 = {}
    timegap_message = {}
    TRACE_CHANNEL = os.environ.get("DB_CHANNEL_ID", "-1002249908184")
    last_edit = defaultdict(lambda: 0)
    SESSION_STRING = os.environ.get(
        "SESSION_STRING",
        "BQFsy9gAWwqRcubot1GlGhJWo6Mf_QCktBHHLeIlbbwFhyb1Abn0ILqG7ku_OvZBd7ZWRrgqZvDjeb2XdVrsjSOH3ximv6pIt4ocdd6dp_DZeHQXvMSs5Bk0bFqZF2k-PS_cR9DPlUy9UOFXpuXtJjwKZCj25Ha0vQTY4TONMF8MzMvK87a9I2WetNIIKhr7mrRUCGoEWusg1grTqmeE0LmQa11tL30j0aW3p678blcOCdxMvgpEcvbV0RwlClYHVA1mCZPwsiaQKWJCg0Oj7UFPRhRwPy3mA7DSyA0tKavoPucF3RNiHTdZBqItGVdXlUANlnn3zsAggPrgkkuCrQOQZVgKywAAAAGBTJMDAA",
    )

    # QUEUE
    SESSION_NAME = os.environ.get("SESSION_NAME", "PinaccleBots")
    WORKERS = 5
    QUEUE_MAXSIZE = 20
    normal_queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
    queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
    normal_tasks = []
    tasks = []
    user = []
    Library = ['aria2', 'aiohttp']
    Extension = ['mp4', 'webm', 'mkv', 'all']
