from os import getenv
from dotenv import load_dotenv
from asyncio import run
from uvloop import install as uvloop_setup

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# load env variables
load_dotenv()

SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = getenv("SLACK_APP_TOKEN")

app = AsyncApp(token=SLACK_BOT_TOKEN)


@app.message("hello")
async def message_hello(message, say):
    await say(f"Hey there <@{message['user']}>!")  # responds to whole channel


@app.command("/check")
async def repeat_text(ack, respond, command):  # Acknowledge command request
    await ack()  # tells the command api that the command has been received
    await respond(f"{command['text']}")  # responds only to user


async def main():
    """
    main method to encapsulate the app

    :return:
    """
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()


# Start your app
if __name__ == "__main__":
    uvloop_setup()
    run(main())
