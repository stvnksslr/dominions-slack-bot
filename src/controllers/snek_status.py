from aiohttp.client import ClientSession

from src.controllers.formatting import (
    create_nations_block,
    create_game_details_block,
    format_server_details,
)
from src.controllers.server_status import query_game_server
from src.models.nation import Nation
from src.models.snek_server_details import SnekServerDetails
from typing import Dict, List


async def server_details_wrapper(port):
    game_id = port[1:]

    async with ClientSession() as session:
        response = await fetch_snek_game_details(port=game_id, session=session)
    formatted_response = format_server_details(response)
    return formatted_response


async def server_response_wrapper(port):
    raw_port = port
    game_id = port[1:]

    game_server_details = query_game_server(address="snek.earth", port=raw_port)
    async with ClientSession() as session:
        nation_status_response = await fetch_snek_nation_status(
            port=game_id, session=session
        )

    nation_block = create_nations_block(nation_status_response)
    game_details_block = create_game_details_block(
        game_name=game_server_details.name,
        turn=game_server_details.turn,
        remaining_time=game_server_details.hours_remaining,
        port=raw_port,
    )
    formatted_response = game_details_block + nation_block
    return formatted_response


async def fetch_snek_game_details(
    port: str, session: ClientSession
) -> SnekServerDetails:
    """
    makes a request to the snek.earth api and then parse the response into a python object

    :param port:
    :param session:
    :return:
    """
    response = await session.get(url=f"https://dom5.snek.earth/api/games/{port}")
    response_json = await response.json()
    parsed_response = SnekServerDetails(**response_json)
    return parsed_response


async def fetch_snek_nation_status(port: str, session: ClientSession) -> List[Nation]:
    """
    Fetches player status for a given game

    :param port:
    :param session:
    :return:
    """
    response = await session.get(url=f"https://dom5.snek.earth/api/games/{port}/status")
    response_json = await response.json()
    parsed_response = parse_snek_player_details(response_json)
    return parsed_response


def parse_snek_player_details(player_status_response: Dict) -> List[Nation]:
    """
    takes in a snek.earth player status response and returns a list of parsed nations

    :param player_status_response:
    :return:
    """
    nations_list = []
    for nation in player_status_response.get("nations"):
        temp_nation = Nation(
            id=nation.get("nationid"),
            name=nation.get("name"),
            epithet=nation.get("epithet"),
            pretender_id=nation.get("pretender_nationid"),
            controller=int(nation.get("controller")),
            ai_level=nation.get("ailevel"),
            turn_played=int(nation.get("turnplayed")),
            filename=nation.get("filename"),
        )
        nations_list.append(temp_nation)
    return nations_list
