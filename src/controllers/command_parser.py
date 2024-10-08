from json import dumps

from loguru import logger

from src.commands.command_factory import CommandFactory


async def command_parser_wrapper(command: str) -> str:
    logger.info(f"Parsing command: {command}")

    if not command.strip():
        return "command not recognised"

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
            return "command not recognised"

        if isinstance(result, str):
            return result
        return dumps(result)

    except ValueError as e:
        logger.error(f"Error parsing command: {e}")
        return "command not recognised"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"An error occurred while processing the command: {e!s}"
