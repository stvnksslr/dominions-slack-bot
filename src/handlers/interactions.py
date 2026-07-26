"""
Handlers for Slack interactive components (buttons)
"""

from collections.abc import Awaitable, Callable
from json import loads
from typing import Any

from loguru import logger

from src.commands.command_factory import CommandFactory
from src.controllers.lobby_details import get_lobby_details


async def handle_refresh_game_status(
    ack: Callable[[], Awaitable[None]], body: dict[str, Any], respond: Callable
) -> None:
    """
    Handle the refresh game status button click.
    Overwrites the existing card rather than posting a new one, so repeated clicks don't spam the channel.
    """
    await ack()

    game_name = body["actions"][0]["value"]
    logger.info(f"Refreshing game status for: {game_name}")

    blocks = await get_lobby_details(game_name, use_db=False)
    await respond(blocks=blocks, text=f"Status for {game_name}", replace_original=True)


async def handle_set_primary_game(ack: Callable[[], Awaitable[None]], body: dict[str, Any], respond: Callable) -> None:
    """
    Handle the set primary game button click.
    Confirms privately to the clicker and leaves the status card in the channel untouched.
    """
    await ack()

    game_name = body["actions"][0]["value"]
    logger.info(f"Setting primary game to: {game_name}")

    command_obj = CommandFactory.get_command("game primary")
    result = await command_obj.execute(game_name)
    blocks = loads(result) if isinstance(result, str) else result

    await respond(blocks=blocks, text=f"Primary game set to {game_name}", replace_original=False)
