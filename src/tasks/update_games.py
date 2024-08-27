from typing import Any, List

from loguru import logger
from slack_sdk.errors import SlackApiError

from src.controllers.lobby_details import get_lobby_details
from src.models.db import Game, Player
from src.utils.slack_manager import client


class UpdateError(Exception):
    pass


class GameDetailsFetchError(Exception):
    pass


async def send_turn_update(game_name: str) -> None:
    try:
        formatted_response = await get_lobby_details(game_name, use_db=True)
        channel_id = "#grog_hole"
        await client.chat_postMessage(channel=channel_id, text="status", blocks=formatted_response)
    except (ValueError, SlackApiError) as e:
        logger.error(f"Failed to send turn update for {game_name}: {e!s}")
        raise UpdateError(f"Failed to send turn update for {game_name}") from e


async def update_game(game: Game) -> None:
    logger.info(f"Querying {game.name} from dominions server")
    try:
        game_details_list: List[Any] = await get_lobby_details(game.name, use_db=False)
        if not game_details_list:
            raise ValueError("No game details returned")
        game_details = game_details_list[0]  # Assume the first item is the relevant game details
    except ValueError as e:
        logger.error(f"Failed to fetch game details for {game.name}: {e!s}")
        raise GameDetailsFetchError(f"Failed to fetch game details for {game.name}") from e

    logger.info(f"Fetched turn {game_details.turn} for {game.name}")

    # Check if the game is finished
    if game_details.turn.lower() == "finished":
        logger.info(f"Game {game.name} has finished. Setting to inactive.")
        await Game.filter(id=game.id).update(active=False)
        await send_turn_update(game.name)  # Notify about the game finishing
        return

    for player in game_details.player_status:
        logger.debug(f"Updating player {player.name}")
        db_player, created = await Player.get_or_create(
            game=game,
            nation=player.name,
            defaults={"short_name": player.name.split(",")[0], "turn_status": player.turn_status},
        )
        if not created:
            db_player.turn_status = player.turn_status
            await db_player.save()

    if game.turn < int(game_details.turn):
        logger.info(f"New turn detected for {game.name}")
        await Game.filter(id=game.id).update(turn=game_details.turn, time_left=game_details.time_left)
        await send_turn_update(game.name)
    else:
        await Game.filter(id=game.id).update(time_left=game_details.time_left)

    logger.info(f"Update complete for {game.name}")


async def update_games_wrapper() -> None:
    game_list = await Game.filter(active=True).all()
    for game in game_list:
        try:
            await update_game(game)
        except (UpdateError, GameDetailsFetchError) as e:
            logger.error(f"Failed to update game {game.name}: {e!s}")
            continue
