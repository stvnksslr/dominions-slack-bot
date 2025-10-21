from json import dumps

from loguru import logger

from src.commands.command_factory import CommandFactory
from src.controllers.formatting import create_error_block, create_info_block


async def command_parser_wrapper(command: str) -> str:
    logger.info(f"Parsing command: {command}")

    if not command.strip():
        return dumps(
            create_info_block(
                "No command provided",
                "Use `/dom help` to see all available commands\n\n"
                "*Quick Start:*\n"
                "• `/dom game add [name]` - Track a new game\n"
                "• `/dom game list` - See all games\n"
                "• `/dom turn` - Check primary game status",
            )
        )

    command_list = command.split()
    main_command = command_list[0]

    try:
        if main_command == "game" and len(command_list) > 1:
            command_obj = CommandFactory.get_command(f"game {command_list[1]}")
            result = await command_obj.execute(*command_list[2:])
        elif main_command in ["player", "check", "turn", "help"]:
            command_obj = CommandFactory.get_command(main_command)
            result = await command_obj.execute(*command_list[1:])
        else:
            # Unknown main command
            suggestions = {
                "add": "`/dom game add [game_name]`",
                "remove": "`/dom game remove [game_name]`",
                "list": "`/dom game list`",
                "primary": "`/dom game primary [game_name]`",
            }
            suggestion_text = suggestions.get(main_command, "`/dom help` to see all commands")
            return dumps(
                create_error_block(
                    f"Unknown command: '{main_command}'", f"💡 Did you mean: {suggestion_text}?\n\nUse `/dom help` for all commands"
                )
            )

        if isinstance(result, str):
            return result
        return dumps(result)

    except ValueError as e:
        logger.error(f"Error parsing command: {e}")

        # Try to provide helpful suggestions based on the command
        if main_command == "game" and len(command_list) > 1:
            subcommand = command_list[1]
            suggestions = {
                "add": "Usage: `/dom game add [game_name]`",
                "remove": "Usage: `/dom game remove [game_name]`",
                "nickname": "Usage: `/dom game nickname [game_name] [nickname]`",
                "list": "Usage: `/dom game list`",
                "primary": "Usage: `/dom game primary [game_name]`",
                "status": "Usage: `/dom game status [game_name] [active|inactive]`",
            }
            suggestion = suggestions.get(subcommand, "Use `/dom help game` for game command help")
            return dumps(create_error_block(f"Invalid game subcommand: '{subcommand}'", suggestion))

        return dumps(
            create_error_block("Command not recognized", f"Error: {e!s}\n\nUse `/dom help` to see all available commands")
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return dumps(create_error_block("Unexpected Error", f"An error occurred while processing the command: {e!s}"))
