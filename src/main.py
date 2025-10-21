from asyncio import create_task, run, sleep
from collections.abc import Awaitable, Callable
from json import JSONDecodeError, loads
from random import choice
from re import compile as re_compile
from typing import Any, NoReturn, TypedDict, cast

from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient
from uvloop import install as install_uvloop

from src.commands.command_factory import CommandFactory
from src.controllers.command_parser import command_parser_wrapper
from src.handlers import (
    handle_add_game_modal_submit,
    handle_refresh_game_status,
    handle_remove_game_modal_submit,
    handle_set_primary_game,
    handle_set_primary_modal_submit,
)
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
        await say(cast(SlackSayResponse, {"text": response}))
    else:
        await say(cast(SlackSayResponse, {"blocks": response, "text": "Response (see blocks for formatted content)"}))


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
            await say(
                cast(
                    SlackSayResponse, {"blocks": parsed_response, "text": "Response (see blocks for formatted content)"}
                )
            )
        else:
            await say(cast(SlackSayResponse, {"text": response}))
    except JSONDecodeError:
        # If it's not valid JSON, treat it as a plain string
        await say(cast(SlackSayResponse, {"text": response}))


@app.command(command="/check")
async def fetch_server_status(
    ack: Callable[[], Awaitable[None]], say: Callable[[SlackSayResponse], Awaitable[Any]], command: dict[str, Any]
) -> None:
    """
    This function handles checking a game via the website instead of the db
    DEPRECATED: Use /dom check [game_name] instead
    """
    await ack()
    game_name = command["text"].strip()

    if not game_name:
        await say(cast(SlackSayResponse, {"text": "Please provide a game name. Usage: /check [game_name]"}))
        return

    try:
        # Show deprecation notice
        await say(
            cast(
                SlackSayResponse,
                {"text": "⚠️ `/check` is deprecated. Please use `/dom check [game_name]` instead.\nFetching status..."},
            )
        )

        command_obj = CommandFactory.get_command("check")
        response = await command_obj.execute(game_name)
        await send_response(say, response)
    except Exception as e:
        logger.error(f"Error fetching game details: {e}")
        await say(cast(SlackSayResponse, {"text": f"An error occurred while fetching game details: {e!s}"}))


@app.command(command="/turn")
async def turn_command(ack: Callable[[], Awaitable[None]], say: Callable[[SlackSayResponse], Awaitable[Any]]) -> None:
    """
    DEPRECATED: Use /dom turn instead
    """
    await ack()

    # Show deprecation notice
    await say(
        cast(SlackSayResponse, {"text": "⚠️ `/turn` is deprecated. Please use `/dom turn` instead.\nFetching status..."})
    )

    command_obj = CommandFactory.get_command("turn")
    response = await command_obj.execute()
    await send_response(say, response)


@app.event(event="message")
async def handle_message_events() -> None:
    """
    generic message handler to make sure messages get handled in some way
    """


# Interactive component handlers
@app.action({"action_id": "refresh_game_status"})
async def refresh_button_handler(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], say: Callable[[SlackSayResponse], Awaitable[Any]]
) -> None:
    """Handle refresh game status button clicks"""
    await handle_refresh_game_status(ack, body, say)


@app.action({"action_id": "set_primary_game"})
async def set_primary_button_handler(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], say: Callable[[SlackSayResponse], Awaitable[Any]]
) -> None:
    """Handle set primary game button clicks"""
    await handle_set_primary_game(ack, body, say)


# Modal view submission handlers
@app.view({"callback_id": "remove_game_modal_submit"})
async def remove_game_modal_submit_handler(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient
) -> None:
    """Handle remove game modal submission"""
    await handle_remove_game_modal_submit(ack, body, client)


@app.view({"callback_id": "set_primary_modal_submit"})
async def set_primary_modal_submit_handler(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient
) -> None:
    """Handle set primary game modal submission"""
    await handle_set_primary_modal_submit(ack, body, client)


@app.view({"callback_id": "add_game_modal_submit"})
async def add_game_modal_submit_handler(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], client: AsyncWebClient
) -> None:
    """Handle add game modal submission"""
    await handle_add_game_modal_submit(ack, body, client)


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
    install_uvloop()
    run(main=main())
