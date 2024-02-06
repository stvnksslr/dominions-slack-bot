from os import getenv

from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = getenv("SLACK_APP_TOKEN")


DB_URI = getenv("DATABASE_URI")
