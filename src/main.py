from asyncio import run
from os import getenv
from random import choice
from re import compile

from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from uvloop import install as uvloop_setup

from src.controllers.grog import grog_response_list
from src.controllers.lobby_details import fetch_lobby_details, format_lobby_details
from src.controllers.mad import mad_reactions_list

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


@app.message(compile(r"\bmad\b"))
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

    game_details = fetch_lobby_details(command_context)
    formatted_response = format_lobby_details(game_details)

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
