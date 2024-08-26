from loguru import logger

from src.controllers.lobby_details import fetch_lobby_details
from src.models.db import Game, Player

UNKNOWN_COMMAND = "command not recognised"
INVALID_COMMAND = "command is invalid please check spelling or help command and try again"


class PlayerOrNationError(Exception):
    pass


def split_string_into_words(input_string) -> list:
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

        5. */dom player [game_name] [nation] [player_name]*
        Associate a player name with a nation in a specific game.
        Example: `/dom player Handsomeboiz_MA arcosophale stebe`

        6. */check [game_name]*
        Fetch the current status of a game, including player statuses and turn timer.
        Example: `/check Handsomeboiz_MA`

        7. */turn*
        Display the current turn status for all active games.

        For more detailed information on a specific command, use: `/dom help [command]`
        """
    return help_text


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
            nation=player.name.strip(),
            short_name=player.short_name(),
            turn_status=player.turn_status,
            game=current_game,
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
            return await add_game(command_list=command_list)
        case "remove":
            return await remove_game(command_list=command_list)
        case "nickname":
            return await nickname_game(command_list=command_list)
        case "list":
            return await list_games()
        case _:
            return await unknown_command()


async def player_command(command_list: list):
    # ./dom player Handsomeboiz_MA arcosophale stebe
    if len(command_list) < 4:
        return INVALID_COMMAND

    game_name = command_list[1]
    existing_game = await Game.filter().filter(name=game_name, active=True).first()

    if not existing_game:
        return f"game {game_name} not found"

    nation_name = command_list[2].lower().strip()
    player_name = command_list[3]

    try:
        await Player.filter(game=existing_game.id, short_name=nation_name).update(player_name=player_name)
        return f"Updated {nation_name} with {player_name} in {game_name}"
    except PlayerOrNationError as error:
        logger.error(f"player or nation not found {error}")
        return "player or nation not found"


async def command_parser_wrapper(command: str):
    logger.info("Parsing command")

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
            return "Game command usage: `/dom game [add|remove|nickname|list] [game_name] [nickname (for nickname command)]`"
        case "player":
            return "Player command usage: `/dom player [game_name] [nation] [player_name]`"
        case "check":
            return "Check command usage: `/check [game_name]`"
        case "turn":
            return "Turn command usage: `/turn` (no additional arguments needed)"
        case _:
            return f"No specific help available for '{command}'. Please use `/dom help` for general help."


async def list_games():
    active_games = await Game.filter(active=True).all()
    if not active_games:
        return "No active games found."

    game_list = "Active games:\n"
    for game in active_games:
        nickname = f" (Nickname: {game.nickname})" if game.nickname else ""
        game_list += f"- {game.name}{nickname}\n"

    return game_list
