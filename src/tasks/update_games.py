from loguru import logger
from slack_sdk.errors import SlackApiError

from src.controllers.lobby_details import fetch_lobby_details
from src.controllers.lobby_details_v2 import turn_command_wrapper
from src.models.db import Game, Player
from src.utils.slack_manager import client


class UpdateError(Exception):
    pass


class GameDetailsFetchError(Exception):
    pass


async def send_turn_update() -> None:
    formatted_response = await turn_command_wrapper()
    # TODO: move to a generic config
    channel_id = "#grog_hole"
    try:
        await client.chat_postMessage(channel=channel_id, text="status", blocks=formatted_response)
    except SlackApiError as e:
        logger.error(e)


async def update_games_wrapper() -> None:
    game_list = await Game.filter(active=True).all()
    for game in game_list:
        logger.info(f"querying {game.name} from dominions server")

        game_details = await fetch_lobby_details(server_name=game.name)

        logger.info("updating", f"fetched turn {game_details.turn}")

        for player in game_details.player_status:
            logger.debug(f"updating player {player.name}")
            await Player().filter(game=game, nation=player.name).update(turn_status=player.turn_status)

        if game.turn < int(game_details.turn):
            logger.info("new turn detected")
            await Game.filter(name=game.name).update(turn=game_details.turn, time_left=game_details.time_left)
            await send_turn_update()
        else:
            await Game.filter(name=game.name).update(time_left=game_details.time_left)

        logger.info("update complete")
