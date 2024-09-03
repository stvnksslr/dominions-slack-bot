from enum import Enum, auto
from typing import Any, Callable, Coroutine, Dict, List, TypedDict

from loguru import logger
from tortoise.exceptions import DBConnectionError, IntegrityError, OperationalError

from src.commands.command_factory import CommandFactory
from src.controllers.lobby_details import get_lobby_details
from src.models.app.player_status import GameDetails
from src.models.db import Game, Player


async def command_parser_wrapper(command: str) -> str:
    logger.info(f"Parsing command: {command}")

    if not command.strip():
        return "command not recognised"

    command_list = command.split()
    main_command = command_list[0]

    try:
        if main_command == "game" and len(command_list) > 1:
            command_obj = CommandFactory.get_command(f"game {command_list[1]}")
            return await command_obj.execute(*command_list[2:])
        if main_command in ["player", "check", "turn", "help"]:
            command_obj = CommandFactory.get_command(main_command)
            return await command_obj.execute(*command_list[1:])
        return "command not recognised"
    except ValueError as e:
        logger.error(f"Error parsing command: {e}")
        return "command not recognised"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"An error occurred while processing the command: {e!s}"
