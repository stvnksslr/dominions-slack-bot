from typing import Any, Optional

import bs4
from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup
from loguru import logger

from src.controllers.formatting import create_game_details_block, create_nations_block
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game


def format_url(server_name: str) -> str:
    return f"http://ulm.illwinter.com/dom6/server/{server_name}.html"


async def fetch_lobby_details_from_web(server_name: str) -> Optional[LobbyDetails]:
    formatted_url = format_url(server_name)
    try:
        async with ClientSession() as session, session.get(url=formatted_url) as response:
            html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        first_row = soup.find("tr")

        if not isinstance(first_row, bs4.Tag):
            logger.error(f"Failed to find table row in HTML content for server {server_name}")
            return None

        server_info = first_row.text.strip().lower()
        turn_parts = server_info.split("turn")
        if len(turn_parts) < 2:
            logger.error(f"Failed to extract turn information for server {server_name}")
            return None

        turn = turn_parts[1].split()[0]

        time_left: Optional[str] = None
        if "(" in server_info and ")" in server_info:
            time_left = server_info.split("(")[1].split(")")[0]

        player_status_list = []
        for row in soup.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) >= 2:
                player_status_list.append(
                    PlayerStatus(name=columns[0].text.strip(), turn_status=columns[1].text.strip())
                )

        return LobbyDetails(
            server_info=server_info,
            player_status=player_status_list,
            turn=turn,
            time_left=time_left,
        )

    except ClientError as e:
        logger.error(f"HTTP request failed for server {server_name}: {e}")
    except (IndexError, ValueError) as e:
        logger.error(f"Failed to extract required information from HTML for server {server_name}: {e}")

    raise ValueError(f"Failed to fetch lobby details from web source for server {server_name}")


async def fetch_lobby_details_from_db(game_name: str) -> Optional[LobbyDetails]:
    game = await Game.filter(name=game_name).first()
    if game is None:
        logger.error(f"Game '{game_name}' not found in the database")
        return None

    await game.fetch_related("players")

    player_status_list = [
        PlayerStatus(name=player.short_name, turn_status=player.turn_status) for player in game.players
    ]

    return LobbyDetails(
        server_info=f"{game.name} - Turn {game.turn}",
        player_status=player_status_list,
        turn=str(game.turn),
        time_left=game.time_left,
    )


def format_lobby_details(lobby_details: LobbyDetails) -> list[dict]:
    game_details_block = create_game_details_block(lobby_details)
    nations_block = create_nations_block(lobby_details.player_status)

    return [
        *game_details_block,
        *nations_block,
    ]


async def get_lobby_details(game_name: str, use_db: bool = False) -> list[Any]:
    fetch_function = fetch_lobby_details_from_db if use_db else fetch_lobby_details_from_web
    lobby_details = await fetch_function(game_name)

    if lobby_details is None:
        raise ValueError(f"Failed to fetch lobby details for game '{game_name}'")

    return format_lobby_details(lobby_details)


async def turn_command_wrapper() -> list[Any]:
    current_game = await Game.filter(primary_game=True).first()
    if current_game is None:
        raise ValueError("No primary game found")
    return await get_lobby_details(current_game.name, use_db=True)
