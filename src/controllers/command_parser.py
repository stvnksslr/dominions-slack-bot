from enum import Enum, auto
from typing import Any, Callable, Coroutine, List, TypedDict

from loguru import logger
from tortoise.exceptions import DBConnectionError, IntegrityError, OperationalError

from src.controllers.lobby_details import fetch_lobby_details
from src.models.db import Game, Player

UNKNOWN_COMMAND = "command not recognised"
INVALID_COMMAND = "command is invalid please check spelling or help command and try again"


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
    logger.info("unknown command")
    return INVALID_COMMAND


async def help_command() -> str:
    help_text = """
        *Dominions 6 Slack Bot Help*

        Here are the available commands:

        1. */dom game add [game_name]*
        Add a new game to the bot's tracking.
        Example: `/dom game add Handsomeboiz_MA`

        2. */dom game remove [game_name]*
        Remove a game from the bot's tracking.
        Example: `/dom game remove Handsomeboiz_MA`

        3. */dom game nickname [game_name] [nickname]*
        Set a nickname for a game.
        Example: `/dom game nickname Handsomeboiz_MA HB_MA`

        4. */dom game list*
        List all active games in the database.
        Example: `/dom game list`

        5. */dom game primary [game_name]*
        Set a game as the primary game, that will be tracked automatically
        and returned from /turn
        Example: `/dom game primary Handsomeboiz_MA`

        6. */dom game status [game_name] [active|inactive]*
        Set a game's active status.
        Example: `/dom game status Handsomeboiz_MA active`

        7. */dom player [game_name] [nation] [player_name]*
        Associate a player name with a nation in a specific game.
        Example: `/dom player Handsomeboiz_MA arcosophale stebe`

        8. */check [game_name]*
        Fetch the current status of a game, including player statuses and turn timer.
        Example: `/check Handsomeboiz_MA`

        9. */turn*
        Display the current turn status for all active games.

        For more detailed information on a specific command, use: `/dom help [command]`
        """
    return help_text


async def add_game(command_list: List[str]) -> str:
    if len(command_list) < 3:
        return INVALID_COMMAND

    game_name = command_list[2]
    existing_game = await Game.filter(name=game_name, active=True).first()

    if existing_game:
        logger.debug("game already exists")
        return f"game {game_name} already exists"

    current_game = await Game.create(name=game_name)
    logger.info(current_game.id)

    game_details = await fetch_lobby_details(game_name)
    if game_details is None:
        logger.error(f"Failed to fetch game details for {game_name}")
        return f"Failed to fetch game details for {game_name}"

    for player in game_details.player_status:
        new_player = await Player.create(
            nation=player.name.strip(),
            short_name=player.short_name(),
            turn_status=player.turn_status,
        )
        await current_game.players.add(new_player)

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
        player = await Player.filter(games=game, short_name=nation_name).first()
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


async def command_parser_wrapper(command: str) -> str:
    logger.info(f"Parsing command, {command}")

    if not command.strip():
        return await unknown_command()

    command_list = split_string_into_words(command)

    match command_list[0]:
        case "help":
            if len(command_list) > 1:
                # Handle specific help requests
                specific_command = command_list[1]
                return await help_command_wrapper(specific_command)
            return await help_command()
        case "game":
            return await game_command(command_list)
        case "player":
            return await player_command(command_list)
        case _:
            return await unknown_command()


async def help_command_wrapper(command: str) -> str:
    match command:
        case "game":
            return "Game command usage: `/dom game [add|remove|nickname|list|primary|status] [game_name] [nickname/status]`"
        case "player":
            return "Player command usage: `/dom player [game_name] [nation] [player_name]`"
        case "check":
            return "Check command usage: `/check [game_name]`"
        case "turn":
            return "Turn command usage: `/turn` (no additional arguments needed)"
        case _:
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
