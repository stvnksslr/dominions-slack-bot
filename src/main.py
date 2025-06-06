from asyncio import create_task, run, sleep
from collections.abc import Awaitable, Callable
from json import JSONDecodeError, loads
from random import choice
from re import compile as re_compile
from typing import Any, NoReturn, TypedDict

from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient
from uvloop import install as uvloop_setup

from src.commands.command_factory import CommandFactory
from src.controllers.command_parser import command_parser_wrapper
from src.responders import grog_response_list, mad_reactions_list
from src.tasks.update_games import update_games_wrapper
from src.utils.constants import SLACK_APP_TOKEN
from src.utils.db_manager import init
from src.utils.log_manager import setup_logger
from src.utils.slack_manager import app

setup_logger()


class SlackSayResponse(TypedDict, total=False):
    text: str
    blocks: list[dict[str, Any]]


async def send_response(
    say: Callable[[SlackSayResponse], Awaitable[Any]], response: str | list[dict[str, Any]]
) -> None:
    """
    Helper function to send a response, handling both string and Slack block formats.
    """
    if isinstance(response, str):
        await say({"text": response})
    else:
        await say({"blocks": response, "text": "Response (see blocks for formatted content)"})


@app.message(keyword=re_compile(pattern="(?i)grog"))
async def grog_responder(say: Callable[[SlackSayResponse], Awaitable[Any]]) -> None:
    """
    when the word grog is mentioned in a channel the bot is present it
    will return one of several random responses
    """
    random_grog = choice(seq=grog_response_list)
    await say({"text": random_grog})


async def mad_reactor(message: dict[str, Any], client: AsyncWebClient) -> None:
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
async def handle_add_game_command(
    ack: Callable[[], Awaitable[None]], say: Callable[[SlackSayResponse], Awaitable[Any]], command: dict[str, Any]
) -> None:
    """
    This function handles the '/dom' command in the Slack bot.
    """
    response = await command_parser_wrapper(command=command["text"])
    await ack()

    try:
        # Attempt to parse the response as JSON
        parsed_response = loads(response)
        if isinstance(parsed_response, list):
            await say({"blocks": parsed_response, "text": "Response (see blocks for formatted content)"})
        else:
            await say({"text": response})
    except JSONDecodeError:
        # If it's not valid JSON, treat it as a plain string
        await say({"text": response})


@app.command(command="/check")
async def fetch_server_status(
    ack: Callable[[], Awaitable[None]], say: Callable[[SlackSayResponse], Awaitable[Any]], command: dict[str, Any]
) -> None:
    """
    This function handles checking a game via the website instead of the db
    """
    await ack()
    game_name = command["text"].strip()

    if not game_name:
        await say({"text": "Please provide a game name. Usage: /check [game_name]"})
        return

    try:
        command_obj = CommandFactory.get_command("check")
        response = await command_obj.execute(game_name)
        await send_response(say, response)
    except Exception as e:
        logger.error(f"Error fetching game details: {e}")
        await say({"text": f"An error occurred while fetching game details: {e!s}"})


@app.command(command="/turn")
async def turn_command(ack: Callable[[], Awaitable[None]], say: Callable[[SlackSayResponse], Awaitable[Any]]) -> None:
    command_obj = CommandFactory.get_command("turn")
    response = await command_obj.execute()
    await ack()
    await send_response(say, response)


@app.event(event="message")
async def handle_message_events() -> None:
    """
    generic message handler to make sure messages get handled in some way
    """


async def periodic_task() -> NoReturn:
    while True:
        logger.info("Running task...")
        await update_games_wrapper()
        await sleep(delay=900)  # wait for 15 mins


async def main() -> None:
    """
    main method to encapsulate the app
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
