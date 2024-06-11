from loguru import logger

from src.controllers.lobby_details import fetch_lobby_details
from src.models.db import Game, Player

UNKNOWN_COMMAND = "command not recognised"
INVALID_COMMAND = "command is invalid please check spelling or help command and try again"


class PlayerOrNationError(Exception):
    pass


def split_string_into_words(input_string) -> list:
    return input_string.split()


async def help_command() -> str:
    return "this should return a dynamic string based on specific command"


async def add_game(command_list: list):
    # /dom game add Handsomeboiz_MA
    if len(command_list) < 3:
        return INVALID_COMMAND

    game_name = command_list[2]
    existing_game = await Game.filter().filter(name=game_name, active=True).first()

    if existing_game:
        logger.debug("game already exists")
        return f"game {game_name} already exists"

    current_game = await Game.create(name=game_name)
    logger.info(current_game.id)

    game_details = await fetch_lobby_details(game_name)
    for player in game_details.player_status:
        await Player().create(
            nation=player.name.strip(), short_name=player.short_name(), turn_status=player.turn_status, game=current_game
        )

    return f"game {game_name} added"


async def remove_game(command_list: list):
    if len(command_list) < 3:
        return INVALID_COMMAND

    game_name = command_list[2]
    await Game.filter(name=game_name).update(active=False)

    return f"game {game_name} deleted"


async def nickname_game(command_list: list):
    if len(command_list) < 4:
        return INVALID_COMMAND

    game_name = command_list[2]
    game_nickname = command_list[3]
    await Game.filter(name=game_name).update(nickname=game_nickname)
    return f"game {game_name} nickname {game_nickname}"


async def game_command(command_list: list):
    match command_list[1]:
        case "add":
            return await add_game(command_list)
        case "remove":
            return await remove_game(command_list)
        case "nickname":
            return await nickname_game()
        case "_":
            return await unknown_command()


async def player_command(command_list: list):
    # ./dom player Handsomeboiz_MA arcosophale stebe
    if len(command_list) < 4:
        return INVALID_COMMAND

    game_name = command_list[1]
    existing_game = await Game.filter().filter(name=game_name, active=True).first()
    if not existing_game:
        return f"game {game_name} not found"
    nation_name = command_list[2].lower()
    player_name = command_list[3]
    try:
        await Player.filter(game=existing_game.id, short_name=nation_name).update(player_name=player_name)
        return f"Updated {nation_name} with {player_name} in {game_name}"
    except PlayerOrNationError as error:
        logger.error(f"player or nation not found {error}")
        return "player or nation not found"


async def unknown_command() -> str:
    logger.info("unknown command")
    return UNKNOWN_COMMAND


async def invalid_command() -> str:
    logger.info("unknown command")
    return INVALID_COMMAND


async def command_parser_wrapper(command: str):
    if not command.strip():
        return unknown_command()

    command_list = split_string_into_words(command)

    match command_list[0]:
        case "help":
            return await help_command()
        case "game":
            return await game_command(command_list)
        case "player":
            return await player_command(command_list)
        case _:
            return await unknown_command()
