from typing import Optional

import bs4
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from loguru import logger

from src.controllers.formatting import create_game_details_block, create_nations_block
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus


def format_url(server_name: str) -> str:
    return f"http://ulm.illwinter.com/dom6/server/{server_name}.html"


async def fetch_lobby_details(server_name: str) -> Optional[LobbyDetails]:
    formatted_url = format_url(server_name)
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
            player_status_list.append(PlayerStatus(name=columns[0].text.strip(), turn_status=columns[1].text.strip()))

    return LobbyDetails(
        server_info=server_info,
        player_status=player_status_list,
        turn=turn,
        time_left=time_left,
    )


def format_lobby_details(lobby_details: LobbyDetails) -> list[dict]:
    game_details_block = create_game_details_block(lobby_details)
    nations_block = create_nations_block(lobby_details.player_status)

    return [
        *game_details_block,
        *nations_block,
    ]
