from os import getenv
from random import choice

from dotenv import load_dotenv
from asyncio import run

from uvloop import install as uvloop_setup
from re import compile

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from src.controllers.grog import grog_response_list
from src.controllers.mad import mad_reactions_list
from src.controllers.snek_status import server_response_wrapper, server_details_wrapper

load_dotenv()

SLACK_BOT_TOKEN = getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = getenv("SLACK_APP_TOKEN")

app = AsyncApp(token=SLACK_BOT_TOKEN)


@app.message(compile("(?i)grog"))
async def grog_responder(say):
    """
    when the word grog is mentioned in a channel the bot is present it
    will return one of several random responses

    :param say:
    :return:
    """
    random_grog = choice(grog_response_list)
    await say(random_grog)


@app.message(compile("(?i)mad"))
async def mad_reactor(message, client):
    """
    when someone is mad, let them know that they're mad
    """
    random_mad = choice(mad_reactions_list)
    await client.reactions_add(
        channel=message["channel"],
        timestamp=message["ts"],
        name=random_mad,
    )


@app.event("message")
async def handle_message_events():
    """
    generic message handler to make sure messages get handled in some way

    :return:
    """
    pass


@app.command("/details")
async def fetch_server_details(ack, say, command):
    """
    Request all server settings from snek.earth

    :param ack:
    :param say:
    :param command:
    :return:
    """
    command_context = command["text"]
    formatted_game_details = await server_details_wrapper(port=command_context)
    await ack()
    await say(blocks=formatted_game_details, text="status")


@app.command("/check")
async def fetch_server_status(ack, say, command):
    """
    Requests all player status's and the current servers turn timer

    :param ack:
    :param say:
    :param command:
    :return:
    """
    command_context = command["text"]
    formatted_response = await server_response_wrapper(port=command_context)
    await ack()
    await say(blocks=formatted_response, text="status")


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
