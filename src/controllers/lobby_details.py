from aiohttp import ClientSession
from bs4 import BeautifulSoup as beatiful_soup  # noqa: N813

from src.controllers.formatting import create_game_details_block, create_nations_block
from src.models import LobbyDetails, PlayerStatus


async def fetch_lobby_details(server_name: str) -> LobbyDetails:
    formatted_url = f"http://ulm.illwinter.com/dom6/server/{server_name}.html"

    async with ClientSession() as session, session.get(formatted_url) as response:
        parsed_response = beatiful_soup(await response.text(), "html.parser")

    game_info = parsed_response.find_all("tr")
    current_game = LobbyDetails(server_info=game_info[0].text, player_status=[])

    # the first line is always the server status so its skipped here
    for player in game_info[1:]:
        name, turn_status = player.find_all("td")[:2]
        current_game.player_status.append(PlayerStatus(name=name.text, turn_status=turn_status.text))

    return current_game


def format_lobby_details(lobby_details: LobbyDetails):
    nation_block = create_nations_block(lobby_details.player_status)
    game_details_block = create_game_details_block(lobby_details)
    formatted_response = game_details_block + nation_block
    return formatted_response
