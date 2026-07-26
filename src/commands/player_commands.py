from json import dumps

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

        # iexact: nations are typed by hand, don't make people match the scraped casing
        player = await Player.filter(game=existing_game, short_name__iexact=nation_name).first()
        if not player:
            return dumps(
                create_error_block(
                    f"Nation '{nation_name}' not found in game '{game_name}'",
                    "Check the nation name and try again. Use `/dom check [game_name]` to see all nations",
                )
            )

        player.player_name = player_name
        await player.save()
        return dumps(
            create_success_block(
                "Player Updated",
                f"• Game: *{game_name}*\n• Nation: *{nation_name}*\n• Player: *{player_name}*",
            )
        )
