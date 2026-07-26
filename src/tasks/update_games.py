from os import getenv

from loguru import logger
from slack_sdk.errors import SlackApiError

from src.controllers.lobby_details import fetch_lobby_details_from_web, get_lobby_details
from src.models.db import Game, Player
from src.utils.slack_manager import client

TURN_UPDATE_CHANNEL = getenv("TURN_UPDATE_CHANNEL", "#grog_hole")


class GameDetailsFetchError(Exception):
    pass


async def send_turn_update(game: Game) -> None:
    """Post the status of the game whose turn just advanced — not whichever game happens to be primary."""
    formatted_response = await get_lobby_details(game.name, use_db=True)
    await client.chat_postMessage(
        channel=TURN_UPDATE_CHANNEL,
        text=f"New turn in {game.nickname or game.name}",
        blocks=formatted_response,
    )


async def update_games_wrapper() -> None:
    game_list = await Game.filter(active=True).all()
    for game in game_list:
        logger.info(f"querying {game.name} from dominions server")

        try:
            game_details = await fetch_lobby_details_from_web(game_name=game.name)
            if game_details is None:
                raise GameDetailsFetchError(f"Failed to fetch details for game {game.name}")

            logger.info(f"fetched turn {game_details.turn} for {game.name}")

            for player in game_details.player_status:
                updated = await Player.filter(game=game, nation=player.name).update(turn_status=player.turn_status)
                if not updated:
                    logger.warning(f"no row matched nation '{player.name}' in {game.name} — status left stale")

            new_turn = int(game_details.turn)
            if game.turn < new_turn:
                logger.info("new turn detected")
                await Game.filter(id=game.id).update(turn=new_turn, time_left=game_details.time_left)
                try:
                    await send_turn_update(game)
                except SlackApiError, OSError:
                    # rewind so the next cycle sees the turn as new again and retries the notification
                    logger.exception(f"turn notification failed for {game.name}; rewinding turn to retry")
                    await Game.filter(id=game.id).update(turn=game.turn)
            else:
                await Game.filter(id=game.id).update(time_left=game_details.time_left)

            # Check if the turn is finished
            if game_details.time_left and game_details.time_left.lower() == "finished":
                logger.info(f"Turn finished for game {game.name}. Setting game to inactive.")
                await Game.filter(id=game.id).update(active=False, primary_game=False)

            logger.info("update complete")
        except GameDetailsFetchError as e:
            logger.error(f"Error fetching game details: {e}")
        except Exception:
            logger.exception(f"Unexpected error updating game {game.name}")
