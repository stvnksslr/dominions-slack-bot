from src.controllers.lobby_details import turn_command_wrapper

from .base import Command


class TurnStatusCommand(Command):
    async def execute(self) -> str:
        try:
            turn_status = await turn_command_wrapper()
            return str(turn_status)
        except ValueError as e:
            return str(e)
