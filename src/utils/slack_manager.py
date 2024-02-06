from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from src.utils.constants import SLACK_BOT_TOKEN

app = AsyncApp(token=SLACK_BOT_TOKEN)
client = AsyncWebClient(token=SLACK_BOT_TOKEN)
