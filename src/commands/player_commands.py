from json import dumps

from tortoise.exceptions import DBConnectionError

from src.controllers.formatting import create_error_block, create_success_block
from src.models.db import Game, Player

from .base import Command


class UpdatePlayerCommand(Command):
    async def execute(self, game_name: str, nation_name: str, player_name: str) -> str:
        existing_game = await Game.filter(name=game_name, active=True).first()
        if not existing_game:
            return dumps(
                create_error_block(f"Game '{game_name}' not found", "Use `/dom game list` to see active games")
            )

        try:
            player = await Player.filter(game=existing_game, short_name=nation_name).first()
            if player:
                player.player_name = player_name
                await player.save()
                return dumps(
                    create_success_block(
                        "Player Updated",
                        f"• Game: *{game_name}*\n• Nation: *{nation_name}*\n• Player: *{player_name}*",
                    )
                )
            return dumps(
                create_error_block(
                    f"Nation '{nation_name}' not found in game '{game_name}'",
                    "Check the nation name and try again. Use `/dom check [game_name]` to see all nations",
                )
            )
        except DBConnectionError as e:
            return dumps(create_error_block("Database Error", f"A database error occurred: {e!s}"))
        except Exception as e:
            return dumps(create_error_block("Unexpected Error", f"An unexpected error occurred: {e!s}"))
