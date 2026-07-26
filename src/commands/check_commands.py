from typing import Any

from src.controllers.lobby_details import get_lobby_details

from .base import Command


class CheckGameStatusCommand(Command):
    async def execute(self, game_name: str) -> list[Any]:
        # get_lobby_details already renders its own failures as blocks
        return await get_lobby_details(game_name, use_db=False)
