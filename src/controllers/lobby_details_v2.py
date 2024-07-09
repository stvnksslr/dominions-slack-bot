from typing import Any

from src.controllers.formatting import create_game_details_block_from_db, create_nations_block_from_db
from src.models.db import Game, Player


def format_lobby_details_from_db(game: Game, players: list[Player]) -> list[Any]:
    nation_block = create_nations_block_from_db(player_list=players)
    game_details_block = create_game_details_block_from_db(game_details=game)
    formatted_response = game_details_block + nation_block
    return formatted_response


async def turn_command_wrapper() -> list[Any]:
    current_game = await Game.filter(primary_game=True).first()
    current_players = await Player.filter(game=current_game).all()
    if current_game is not None:
        formatted_response = format_lobby_details_from_db(game=current_game, players=current_players)
    else:
        raise ValueError("current_game cannot be None")
    return formatted_response
