from src.controllers.lobby_details import get_lobby_details

from .base import Command


class CheckGameStatusCommand(Command):
    async def execute(self, game_name: str) -> str:
        try:
            game_details = await get_lobby_details(game_name, use_db=False)
            return str(game_details)
        except ValueError as e:
            return str(e)
