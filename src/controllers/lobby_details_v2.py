from src.controllers.formatting import create_game_details_block_from_db, create_nations_block_from_db
from src.models.db import Game, Player


def format_lobby_details_from_db(game: Game, players: list[Player]):
    nation_block = create_nations_block_from_db(players)
    game_details_block = create_game_details_block_from_db(game)
    formatted_response = game_details_block + nation_block
    return formatted_response


async def turn_command_wrapper():
    current_game = await Game.filter(primary_game=True).first()
    current_players = await Player.filter(game=current_game).all()
    formatted_response = format_lobby_details_from_db(current_game, current_players)
    return formatted_response
