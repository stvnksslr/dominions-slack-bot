from os import getenv

from dotenv import load_dotenv
from asyncio import run
from uvloop import install as uvloop_setup

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from src.controllers.snek_status import server_response_wrapper, server_details_wrapper

load_dotenv()

SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = getenv("SLACK_APP_TOKEN")

app = AsyncApp(token=SLACK_BOT_TOKEN)


@app.command("/details")
async def fetch_server_details(ack, respond, command):
    """
    Request all server settings from snek.earth

    :param ack:
    :param respond:
    :param command:
    :return:
    """
    command_context = command["text"]
    formatted_game_details = await server_details_wrapper(port=command_context)
    await ack()
    await respond(blocks=formatted_game_details, text="status")


@app.command("/check")
async def fetch_server_status(ack, respond, command):
    """
    Requests all player status's and the current servers turn timer

    :param ack:
    :param respond:
    :param command:
    :return:
    """
    command_context = command["text"]
    formatted_response = await server_response_wrapper(port=command_context)
    await ack()
    await respond(blocks=formatted_response, text="status")


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
