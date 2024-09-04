from src.controllers.lobby_details import turn_command_wrapper

from .base import Command


class TurnStatusCommand(Command):
    async def execute(self):
        try:
            turn_status = await turn_command_wrapper()
            return turn_status
        except ValueError as e:
            return str(e)
