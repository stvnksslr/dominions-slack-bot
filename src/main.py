from asyncio import gather, run, sleep
from collections.abc import Awaitable, Callable
from os import getenv
from random import choice
from re import compile as re_compile
from typing import Any, NoReturn, TypedDict, cast

import pyroscope
from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from uvloop import install as install_uvloop

from src.controllers.command_parser import command_parser_wrapper
from src.handlers import handle_refresh_game_status, handle_set_primary_game
from src.responders import grog_response_list, mad_reactions_list
from src.tasks.update_games import update_games_wrapper
from src.utils.constants import SLACK_APP_TOKEN
from src.utils.db_manager import init
from src.utils.log_manager import setup_logger
from src.utils.slack_manager import app

setup_logger()

# Initialize Pyroscope profiling
if pyroscope_server := getenv("PYROSCOPE_SERVER_ADDRESS"):
    gil_only = getenv("PYROSCOPE_GIL_ONLY", "true").lower() == "true"
    pyroscope.configure(
        application_name=getenv("PYROSCOPE_APPLICATION_NAME", "feral-grog-bot"),
        server_address=pyroscope_server,
        tags={"namespace": getenv("POD_NAMESPACE", "bots")},
        oncpu=True,
        gil_only=gil_only,
        report_thread_name=True,
    )
    logger.info(f"Pyroscope CPU profiling enabled (gil_only={gil_only}), sending to {pyroscope_server}")


class SlackSayResponse(TypedDict, total=False):
    text: str
    blocks: list[dict[str, Any]]


@app.message(keyword=re_compile(pattern="(?i)grog"))
async def grog_responder(say: Callable[[SlackSayResponse], Awaitable[Any]]) -> None:
    """
    when the word grog is mentioned in a channel the bot is present it
    will return one of several random responses
    """
    random_grog = choice(seq=grog_response_list)
    await say(cast(SlackSayResponse, {"text": random_grog}))


@app.message(keyword=re_compile(pattern=r"\bmad\b"))
async def mad_reactor(message: dict[str, Any], client: AsyncWebClient) -> None:
    """
    when someone is mad, let them know that they're mad
    """
    random_mad = choice(seq=mad_reactions_list)

    try:
        await client.reactions_add(
            channel=message["channel"],
            timestamp=message["ts"],
            name=random_mad,
        )
    except SlackApiError as e:
        # already_reacted on a repeat pick, or invalid_name if the workspace lacks the custom emoji
        logger.warning(f"could not add reaction '{random_mad}': {e}")


@app.command(command="/dom")
async def handle_dom_command(
    ack: Callable[[], Awaitable[None]],
    say: Callable[[SlackSayResponse], Awaitable[Any]],
    respond: Callable,
    command: dict[str, Any],
) -> None:
    """
    This function handles the '/dom' command in the Slack bot.
    """
    # ack first: Slack gives us 3 seconds, and parsing can involve a scrape of the dominions server
    await ack()

    blocks, ephemeral = await command_parser_wrapper(command=command["text"])

    if ephemeral:
        await respond(blocks=blocks, text="Response (see blocks for formatted content)")
    else:
        await say(cast(SlackSayResponse, {"blocks": blocks, "text": "Response (see blocks for formatted content)"}))


@app.event(event="message")
async def handle_message_events() -> None:
    """
    generic message handler to make sure messages get handled in some way
    """


# Interactive component handlers
@app.action({"action_id": "refresh_game_status"})
async def refresh_button_handler(ack: Callable[[], Awaitable[None]], body: dict[str, Any], respond: Callable) -> None:
    """Handle refresh game status button clicks"""
    await handle_refresh_game_status(ack, body, respond)


@app.action({"action_id": "set_primary_game"})
async def set_primary_button_handler(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], respond: Callable
) -> None:
    """Handle set primary game button clicks"""
    await handle_set_primary_game(ack, body, respond)


async def periodic_task() -> NoReturn:
    while True:
        logger.info("Running task...")
        try:
            await update_games_wrapper()
        except Exception:
            # never let a DB blip escape into gather() — that would take the slack handler down with it
            logger.exception("game update cycle failed")
        await sleep(delay=900)  # wait for 15 mins


async def main() -> None:
    """
    main method to encapsulate the app
    """
    await init()
    handler = AsyncSocketModeHandler(app=app, app_token=SLACK_APP_TOKEN)
    # Run both the handler and periodic task concurrently
    await gather(handler.start_async(), periodic_task())


# Start your app
if __name__ == "__main__":
    install_uvloop()
    run(main=main())
