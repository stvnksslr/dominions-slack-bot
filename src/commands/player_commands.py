from tortoise.exceptions import DBConnectionError

from src.models.db import Game, Player

from .base import Command


class UpdatePlayerCommand(Command):
    async def execute(self, game_name: str, nation_name: str, player_name: str) -> str:
        existing_game = await Game.filter(name=game_name, active=True).first()
        if not existing_game:
            return f"game {game_name} not found"

        try:
            player = await Player.filter(game=existing_game, short_name=nation_name).first()
            if player:
                player.player_name = player_name
                await player.save()
                return f"Updated {nation_name} with {player_name} in {game_name}"
            return f"Player with nation {nation_name} not found in game {game_name}"
        except DBConnectionError as e:
            return f"A database error occurred while updating the player: {e!s}"
        except Exception as e:
            return f"An unexpected error occurred: {e!s}"
