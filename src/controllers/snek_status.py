from aiohttp.client import ClientSession

from src.models.nation import Nation
from src.models.snek_server_details import SnekServerDetails
from typing import Dict, List


async def fetch_snek_status(port: str, session: ClientSession) -> SnekServerDetails:
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


async def fetch_snek_player_status(port: str, session: ClientSession) -> List[Nation]:
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
    for nation in player_status_response.get('nations'):
        temp_nation = Nation(
            id=nation.get('nationid'),
            name=nation.get('name'),
            epithet=nation.get('epithet'),
            pretender_id=nation.get('pretender_nationid'),
            controller=int(nation.get('controller')),
            ai_level=nation.get('ailevel'),
            turn_played=int(nation.get('turnplayed')),
            filename=nation.get('filename')
        )
        nations_list.append(temp_nation)
    return nations_list
