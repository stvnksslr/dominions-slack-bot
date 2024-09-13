from asyncio import create_task, run, sleep
from json import JSONDecodeError, loads
from random import choice
from re import compile
from typing import Any, Dict, List, NoReturn, Union

from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from uvloop import install as uvloop_setup

from src.commands.command_factory import CommandFactory
from src.controllers.command_parser import command_parser_wrapper
from src.controllers.lobby_details import get_lobby_details, turn_command_wrapper
from src.responders import grog_response_list, mad_reactions_list
from src.tasks.update_games import update_games_wrapper
from src.utils.constants import SLACK_APP_TOKEN
from src.utils.db_manager import init
from src.utils.log_manager import setup_logger
from src.utils.slack_manager import app

setup_logger()


async def send_response(say, response: Union[str, List[Dict[str, Any]]]) -> None:
    """
    Helper function to send a response, handling both string and Slack block formats.
    """
    if isinstance(response, str):
        await say(text=response)
    else:
        await say(blocks=response, text="Response (see blocks for formatted content)")


@app.message(keyword=compile(pattern="(?i)grog"))
async def grog_responder(say) -> None:
    """
    when the word grog is mentioned in a channel the bot is present it
    will return one of several random responses
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
    This function handles the '/dom' command in the Slack bot.
    """
    response = await command_parser_wrapper(command=command["text"])
    await ack()

    try:
        # Attempt to parse the response as JSON
        parsed_response = loads(response)
        if isinstance(parsed_response, list):
            await say(blocks=parsed_response, text="Response (see blocks for formatted content)")
        else:
            await say(text=response)
    except JSONDecodeError:
        # If it's not valid JSON, treat it as a plain string
        await say(text=response)


@app.command(command="/check")
async def fetch_server_status(ack, say, command) -> None:
    """
    This function handles checking a game via the website instead of the db
    """
    await ack()
    game_name = command["text"].strip()

    if not game_name:
        await say("Please provide a game name. Usage: /check [game_name]")
        return

    try:
        command_obj = CommandFactory.get_command("check")
        response = await command_obj.execute(game_name)
        await send_response(say, response)
    except Exception as e:
        logger.error(f"Error fetching game details: {e}")
        await say(f"An error occurred while fetching game details: {e!s}")


@app.command(command="/turn")
async def turn_command(ack, say) -> None:
    command_obj = CommandFactory.get_command("turn")
    response = await command_obj.execute()
    await ack()
    await send_response(say, response)


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
