from aiohttp.client import ClientSession
from pytest import mark
from json import loads

from src.controllers.server_status import query_game_server
from src.controllers.snek_status import (
    fetch_snek_game_details,
    parse_snek_player_details,
)
from pathlib import Path

from src.models.snek_server_details import SnekServerDetails

player_status_response = (
        Path.cwd() / "src" / "tests" / "responses" / "player_status.json"
)
server_status_response = (
        Path.cwd() / "src" / "tests" / "responses" / "server_status_running.json"
)


@mark.asyncio
@mark.skip(reason="Used for testing snek backend")
async def test__fetch_snek_status():
    """
    not a true test, just used for pulling a request in a standardized manner

    :return:
    """
    async with ClientSession() as session:
        response = await fetch_snek_game_details(port="3533", session=session)
    assert response is True


@mark.skip(reason="Used for testing direct server connections")
def test__query_game_server():
    response = query_game_server(address="snek.earth", port="33533")
    assert response.name == "middleagedbois"
    assert response.hours_remaining == "25.54"
    assert response.turn == "70"


def test__parse_snek_player_details():
    with open(player_status_response) as file:
        response = loads(file.read())
    parsed_response = parse_snek_player_details(player_status_response=response)
    assert 9 is len(parsed_response)


def test__parse_snek_server_status():
    with open(server_status_response) as file:
        response = loads(file.read())
    parsed_server_response = SnekServerDetails(**response)
    assert parsed_server_response.era.name is "Late_Age"
    assert parsed_server_response.name == "middle aged bois"
