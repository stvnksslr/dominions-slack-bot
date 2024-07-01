from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from bs4 import BeautifulSoup as beautiful_soup  # noqa: N813
from loguru import logger

from src.controllers.formatting import create_game_details_block, create_nations_block
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus


async def fetch_lobby_details(server_name: str) -> LobbyDetails:
    try:
        formatted_url = f"http://ulm.illwinter.com/dom6/server/{server_name}.html"

        async with ClientSession() as session:
            response = await session.get(formatted_url)
            parsed_response = beautiful_soup(await response.text(), "html.parser")

        game_info = parsed_response.find_all("tr")

        server_info_split = game_info[0].text.split(",")
        turn = server_info_split[1].split()[1] if len(server_info_split) > 1 else None
        time_left = server_info_split[1].split("(")[1].strip()[:-1] if len(server_info_split) > 1 else None

        current_game = LobbyDetails(
            server_info=game_info[0].text,
            player_status=[],
            turn=turn,
            time_left=time_left,
        )

        # the first line is always the server status so its skipped here
        for player in game_info[1:]:
            name, turn_status = player.find_all("td")[:2]
            current_game.player_status.append(PlayerStatus(name=name.text.strip(), turn_status=turn_status.text))

        return current_game

    except ClientConnectorError as e:
        logger.error(f"An error occurred: {e}")
        raise


def format_lobby_details(lobby_details: LobbyDetails):
    nation_block = create_nations_block(lobby_details.player_status)
    game_details_block = create_game_details_block(lobby_details)
    formatted_response = game_details_block + nation_block
    return formatted_response
