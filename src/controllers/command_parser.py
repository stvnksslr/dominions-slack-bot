from inspect import signature
from json import loads
from typing import Any

from loguru import logger

from src.commands.command_factory import CommandFactory
from src.controllers.formatting import create_error_block, create_info_block

# only these post to the channel; everything else answers the caller privately
CHANNEL_VISIBLE = {"check", "turn"}

USAGE = {
    "game add": "`/dom game add [game_name]`",
    "game remove": "`/dom game remove [game_name]`",
    "game nickname": "`/dom game nickname [game_name] [nickname]`",
    "game list": "`/dom game list`",
    "game primary": "`/dom game primary [game_name]`",
    "game status": "`/dom game status [game_name] [active|inactive]`",
    "player": "`/dom player [game_name] [nation] [player_name]`",
    "check": "`/dom check [game_name]`",
    "turn": "`/dom turn`",
    "help": "`/dom help [game|player|check|turn]`",
}


async def command_parser_wrapper(command: str) -> tuple[list[dict[str, Any]], bool]:
    """Route a /dom command. Returns (slack blocks, ephemeral)."""
    logger.info(f"Parsing command: {command}")

    if not command.strip():
        return create_info_block(
            "No command provided",
            "Use `/dom help` to see all available commands\n\n"
            "*Quick Start:*\n"
            "• `/dom game add [name]` - Track a new game\n"
            "• `/dom game list` - See all games\n"
            "• `/dom turn` - Check primary game status",
        ), True

    command_list = command.split()
    main_command = command_list[0].lower()

    # bare `/dom game` is a request for help, not an error
    if main_command == "game" and len(command_list) == 1:
        main_command, command_list = "help", ["help", "game"]

    if main_command == "game":
        name = f"game {command_list[1].lower()}"
        args = command_list[2:]
    elif main_command in {"player", "check", "turn", "help"}:
        name = main_command
        args = command_list[1:]
    else:
        return create_error_block(
            f"Unknown command: '{command_list[0]}'",
            "Use `/dom help` to see all commands",
        ), True

    try:
        command_obj = CommandFactory.get_command(name)
    except ValueError:
        logger.error(f"Unknown command: {name}")
        return create_error_block(
            f"Unknown game subcommand: '{command_list[1]}'",
            "Valid subcommands: `add`, `remove`, `nickname`, `list`, `primary`, `status`\n"
            "Use `/dom help game` for details",
        ), True

    # check arity before calling, so a genuine TypeError inside the command isn't misreported as bad args
    try:
        signature(command_obj.execute).bind(*args)
    except TypeError:
        logger.info(f"Wrong argument count for '{name}': {args}")
        return create_error_block(
            f"Wrong arguments for `/dom {name}`",
            f"Usage: {USAGE.get(name, '`/dom help`')}",
        ), True

    try:
        result = await command_obj.execute(*args)
    except Exception:
        logger.exception(f"Error running '{name}'")
        return create_error_block(
            "Something went wrong",
            "The failure has been logged. Try again, or check the bot logs.",
        ), True

    blocks = loads(result) if isinstance(result, str) else result
    return blocks, name not in CHANNEL_VISIBLE
