from typing import Any

from src.controllers.lobby_details import turn_command_wrapper

from .base import Command


class TurnStatusCommand(Command):
    async def execute(self) -> list[Any]:
        # turn_command_wrapper already renders its own failures as blocks
        return await turn_command_wrapper()
