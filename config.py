import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

ADMINS = list(
    map(
        int,
        os.getenv("ADMINS").split(",")
    )
)