from asyncio import create_task, run, sleep
from random import choice
from re import compile
from typing import NoReturn

from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from uvloop import install as uvloop_setup

from src.controllers.command_parser import command_parser_wrapper
from src.controllers.lobby_details import fetch_lobby_details, format_lobby_details
from src.controllers.lobby_details_v2 import turn_command_wrapper
from src.responders import grog_response_list, mad_reactions_list
from src.tasks.update_games import update_games_wrapper
from src.utils.constants import SLACK_APP_TOKEN
from src.utils.db_manager import init
from src.utils.log_manager import setup_logger
from src.utils.slack_manager import app

setup_logger()


@app.message(keyword=compile(pattern="(?i)grog"))
async def grog_responder(say) -> None:
    """
    when the word grog is mentioned in a channel the bot is present it
    will return one of several random responses

    :param say:
    :return:
    """
    random_grog = choice(seq=grog_response_list)
    await say(random_grog)


@app.message(keyword=compile(pattern=r"\bmad\b"))
async def mad_reactor(message, client) -> None:
    """
    when someone is mad, let them know that they're mad
    """
    random_mad = choice(seq=mad_reactions_list)

    await client.reactions_add(
        channel=message["channel"],
        timestamp=message["ts"],
        name=random_mad,
    )


@app.command(command="/dom")
async def handle_add_game_command(ack, say, command) -> None:
    """
    This function handles the '/dom' command in the Slack bot. It takes three parameters:
    'ack', 'say', and 'command'.

    :param ack: function to acknowledge the command
    :param say: function to send a message back to the user
    :param command: dictionary containing the command text
    :return: None
    """
    response = await command_parser_wrapper(command=command["text"])

    await ack()
    await say(response)


@app.command(command="/check")
async def fetch_server_status(ack, say, command) -> None:
    """
    Requests all player status's and the current servers turn timer

    :param ack:
    :param say:
    :param command:
    :return:
    """
    command_context = command["text"]

    game_details = await fetch_lobby_details(server_name=command_context)
    if game_details is None:
        await ack()
        await say("Failed to fetch game details")
        return

    formatted_response = format_lobby_details(lobby_details=game_details)

    await ack()
    await say(blocks=formatted_response, text="status")


@app.command(command="/turn")
async def turn_command(ack, say) -> None:
    formatted_response = await turn_command_wrapper()
    await ack()
    await say(blocks=formatted_response, text="status")


@app.event(event="message")
async def handle_message_events() -> None:
    """
    generic message handler to make sure messages get handled in some way

    :return:
    """


async def periodic_task() -> NoReturn:
    while True:
        logger.info("Running task...")
        await update_games_wrapper()
        await sleep(delay=900)  # wait for 15 mins


async def main():
    """
    main method to encapsulate the app

    :return:
    """
    await init()
    task = create_task(coro=periodic_task())
    handler = AsyncSocketModeHandler(app=app, app_token=SLACK_APP_TOKEN)
    await handler.start_async()
    task.cancel()


# Start your app
if __name__ == "__main__":
    uvloop_setup()
    run(main=main())
