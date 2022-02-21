from dotenv import load_dotenv
from os import getenv

load_dotenv()

# database
DATABASE_URI = getenv("DATABASE_URI")

# slack tokens
SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = getenv("SLACK_APP_TOKEN")
