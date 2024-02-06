from loguru import logger

from src.controllers.lobby_details import fetch_lobby_details
from src.models.db import Game, Player


class UpdateError(Exception):
    pass


class GameDetailsFetchError(Exception):
    pass


async def update_games_wrapper():
    game_list = await Game.filter(active=True).all()
    for game in game_list:
        logger.info(f"querying {game.name} from dominions server")

        game_details = await fetch_lobby_details(game.name)

        logger.info("updating")

        logger.info(f"turn {game_details.turn}")
        logger.info(f"turn {game_details.time_left}")

        if game.turn < int(game_details.turn):
            logger.info("new turn")
            await Game.filter(name=game.name).update(turn=game_details.turn, time_left=game_details.time_left)
            # TODO: send message to slack channel

        for player in game_details.player_status:
            logger.info(f"updating player {player.name}")
            await Player().filter(game=game, nation=player.name).update(turn_status=player.turn_status)

        logger.info("update complete")
