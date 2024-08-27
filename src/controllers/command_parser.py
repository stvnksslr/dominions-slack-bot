from enum import Enum, auto
from typing import Any, Callable, Coroutine, Dict, List, TypedDict

from loguru import logger
from tortoise.exceptions import DBConnectionError, IntegrityError, OperationalError

from src.controllers.lobby_details import get_lobby_details
from src.models.app.player_status import GameDetails
from src.models.db import Game, Player

UNKNOWN_COMMAND = "command not recognised"
INVALID_COMMAND = "command is invalid please check spelling or help command and try again"

# Define help texts for each command
HELP_TEXTS: Dict[str, str] = {
    "game": """
    Game command usage: `/dom game [subcommand] [arguments]`
    Subcommands:
    - add [game_name]: Add a new game to track
    - remove [game_name]: Remove a game from tracking
    - nickname [game_name] [nickname]: Set a nickname for a game
    - list: List all active games
    - primary [game_name]: Set a game as the primary game
    - status [game_name] [active|inactive]: Set a game's active status
    """,
    "player": """
    Player command usage: `/dom player [game_name] [nation] [player_name]`
    Associate a player name with a nation in a specific game.
    """,
    "check": """
    Check command usage: `/check [game_name]`
    Fetch the current status of a game, including player statuses and turn timer.
    """,
    "turn": """
    Turn command usage: `/turn`
    Display the current turn status for all active games.
    """,
}


class PlayerOrNationError(Exception):
    pass


class PlayerCommandResult(Enum):
    INVALID_COMMAND = auto()
    GAME_NOT_FOUND = auto()
    PLAYER_UPDATED = auto()
    PLAYER_NOT_FOUND = auto()
    DATABASE_ERROR = auto()


def split_string_into_words(input_string: str) -> List[str]:
    return input_string.split()


async def unknown_command() -> str:
    logger.info("unknown command")
    return UNKNOWN_COMMAND


async def invalid_command() -> str:
    logger.info("invalid command")
    return INVALID_COMMAND


async def add_game(command_list: List[str]) -> str:
    if len(command_list) < 3:
        return INVALID_COMMAND

    game_name = command_list[2]
    existing_game = await Game.filter(name=game_name, active=True).first()

    if existing_game:
        logger.debug("game already exists")
        return f"game {game_name} already exists"

    try:
        game_details: List[Any] = await get_lobby_details(game_name, use_db=False)
    except ValueError as e:
        logger.error(f"Failed to fetch game details for {game_name}: {e!s}")
        return f"Failed to fetch game details for {game_name}"

    # Assuming the list structure is [turn, time_left, [player_status]]
    if len(game_details) != 3:
        return f"Unexpected game details format for {game_name}"

    turn, time_left, player_status = game_details

    current_game = await Game.create(name=game_name, turn=turn, time_left=time_left)
    logger.info(f"Created game with ID: {current_game.id}")

    for player in player_status:
        if isinstance(player, dict) and "name" in player and "turn_status" in player:
            new_player = await Player.create(
                nation=player["name"].strip(),
                short_name=player["name"].split(",")[0].strip(),
                turn_status=player["turn_status"],
            )
            await current_game.players.add(new_player)
        else:
            logger.warning(f"Unexpected player data format: {player}")

    return f"game {game_name} added"


async def remove_game(command_list: List[str]) -> str:
    if len(command_list) < 3:
        return INVALID_COMMAND

    game_name = command_list[2]
    await Game.filter(name=game_name).update(active=False)

    return f"game {game_name} deleted"


async def nickname_game(command_list: List[str]) -> str:
    if len(command_list) < 4:
        return INVALID_COMMAND

    game_name = command_list[2]
    game_nickname = command_list[3]
    await Game.filter(name=game_name).update(nickname=game_nickname)
    return f"game {game_name} nickname {game_nickname}"


async def set_game_status(command_list: List[str]) -> str:
    if len(command_list) < 4:
        return INVALID_COMMAND

    game_name = command_list[2]
    status = command_list[3].lower()

    if status not in ["active", "inactive"]:
        return "Invalid status. Use 'active' or 'inactive'."

    game = await Game.filter(name=game_name).first()
    if not game:
        return f"Game {game_name} not found"

    game.active = status == "active"
    await game.save()

    return f"Game {game_name} status set to {status}"


class SubcommandHandlers(TypedDict):
    add: Callable[[List[str]], Coroutine[Any, Any, str]]
    remove: Callable[[List[str]], Coroutine[Any, Any, str]]
    nickname: Callable[[List[str]], Coroutine[Any, Any, str]]
    list: Callable[[], Coroutine[Any, Any, str]]
    primary: Callable[[List[str]], Coroutine[Any, Any, str]]
    status: Callable[[List[str]], Coroutine[Any, Any, str]]


async def game_command(command_list: List[str]) -> str:
    if len(command_list) < 2:
        return await invalid_command()

    subcommand = command_list[1]
    subcommand_handlers: SubcommandHandlers = {
        "add": add_game,
        "remove": remove_game,
        "nickname": nickname_game,
        "list": list_games,
        "primary": set_primary,
        "status": set_game_status,
    }

    handler = subcommand_handlers.get(subcommand)
    if handler and callable(handler):
        if subcommand == "list":
            return await handler()
        return await handler(command_list)
    return await unknown_command()


async def set_primary(command_list: List[str]) -> str:
    if len(command_list) < 3:
        return INVALID_COMMAND

    game_name = command_list[2]
    existing_game = await Game.filter(name=game_name, active=True).first()

    if not existing_game:
        return f"Game {game_name} not found or not active"

    # Set all games to non-primary
    await Game.filter(active=True).update(primary_game=False)

    # Set the specified game as primary
    await Game.filter(id=existing_game.id).update(primary_game=True)

    return f"Game {game_name} has been set as the primary game"


async def update_player(game: Game, nation_name: str, player_name: str) -> PlayerCommandResult:
    try:
        player = await Player.filter(game=game, short_name=nation_name).first()
        if player:
            player.player_name = player_name
            await player.save()
            return PlayerCommandResult.PLAYER_UPDATED
        return PlayerCommandResult.PLAYER_NOT_FOUND
    except (IntegrityError, DBConnectionError, OperationalError) as e:
        logger.error(f"Database error updating player: {e}")
        return PlayerCommandResult.DATABASE_ERROR


async def player_command(command_list: List[str]) -> str:
    if len(command_list) < 4:
        return INVALID_COMMAND

    game_name, nation_name, player_name = command_list[1], command_list[2].lower().strip(), command_list[3]

    existing_game = await Game.filter(name=game_name, active=True).first()
    if not existing_game:
        return f"game {game_name} not found"

    result = await update_player(existing_game, nation_name, player_name)

    match result:
        case PlayerCommandResult.PLAYER_UPDATED:
            return f"Updated {nation_name} with {player_name} in {game_name}"
        case PlayerCommandResult.PLAYER_NOT_FOUND:
            return f"Player with nation {nation_name} not found in game {game_name}"
        case PlayerCommandResult.DATABASE_ERROR:
            return "A database error occurred while updating the player"
        case _:
            return "An unexpected error occurred"


async def help_command() -> str:
    help_text = """
    *Dominions 6 Slack Bot Help*

    Here are the available commands:
    """
    for command, text in HELP_TEXTS.items():
        help_text += f"\n{command.capitalize()}:\n{text.strip()}\n"

    help_text += "\nFor more detailed information on a specific command, use: `/dom help [command]`"
    return help_text


async def handle_help_command(command_list: List[str]) -> str:
    if len(command_list) > 1:
        specific_command = command_list[1]
        return await help_command_wrapper(specific_command)
    return await help_command()


async def handle_check_command(command_list: List[str]) -> str:
    if len(command_list) > 1:
        game_name = command_list[1]
        try:
            game_details = await get_lobby_details(game_name, use_db=True)
            return str(game_details)  # You might want to format this better
        except ValueError as e:
            return str(e)
    return INVALID_COMMAND


async def handle_turn_command() -> str:
    try:
        turn_status = await get_lobby_details(game_name="", use_db=True)  # Assuming this gets the primary game
        return str(turn_status)  # You might want to format this better
    except ValueError as e:
        return str(e)


async def command_parser_wrapper(command: str) -> str:
    logger.info(f"Parsing command: {command}")

    if not command.strip():
        return await unknown_command()

    command_list = split_string_into_words(command)

    command_handlers = {
        "help": handle_help_command,
        "game": game_command,
        "player": player_command,
        "check": handle_check_command,
        "turn": lambda _: handle_turn_command(),
    }

    handler = command_handlers.get(command_list[0])
    if handler:
        return await handler(command_list)

    return await unknown_command()


async def help_command_wrapper(command: str) -> str:
    if command in HELP_TEXTS:
        return f"{command.capitalize()} command help:\n{HELP_TEXTS[command].strip()}"
    return f"No specific help available for '{command}'. Please use `/dom help` for general help."


async def list_games() -> str:
    all_games = await Game.all()
    if not all_games:
        return "No games found."

    game_list = "Games:\n"
    for game in all_games:
        nickname = f" (Nickname: {game.nickname})" if game.nickname else ""
        primary = " [PRIMARY]" if game.primary_game else ""
        status = "Active" if game.active else "Inactive"
        game_list += f"- {game.name}{nickname}{primary} - {status}\n"

    return game_list
