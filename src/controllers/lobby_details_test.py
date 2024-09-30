from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponse, ClientSession

from src.controllers.lobby_details import format_lobby_details, get_lobby_details
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game, Player


class MockConnectionError(Exception):
    pass


@pytest.fixture
def mock_html_content():
    return """
    <html><body>
        <tr>Server Info, Turn 1 (1 day left)</tr>
        <tr><td>Player1</td><td>Turn played</td></tr>
    </body></html>
    """


@pytest.fixture
def mock_game():
    return MagicMock(spec=Game, name="TestGame", turn="1", time_left="1 day left")


@pytest.fixture
def mock_players():
    return [MagicMock(spec=Player, short_name="Player1", turn_status="Turn played")]


@pytest.mark.asyncio
async def test_get_lobby_details_web_source(mock_html_content):
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.text.return_value = mock_html_content
    mock_session = AsyncMock(spec=ClientSession)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with (
        patch("src.controllers.lobby_details.ClientSession") as mock_client_session,
        patch("src.controllers.lobby_details.fetch_lobby_details_from_web") as mock_fetch,
    ):
        mock_client_session.return_value.__aenter__.return_value = mock_session
        mock_fetch.return_value = LobbyDetails(
            server_info="Server Info, Turn 1 (1 day left)",
            player_status=[PlayerStatus(name="Player1", turn_status="Turn played")],
            turn="1",
            time_left="1 day left",
        )
        result = await get_lobby_details("server_name", use_db=False)

    assert isinstance(result, list)
    assert len(result) > 0
    assert any("Server Info, Turn 1" in str(block) for block in result)
    assert any("Player1" in str(block) for block in result)


@pytest.mark.asyncio
async def test_get_lobby_details_db_source(mock_game, mock_players):
    with (
        patch("src.controllers.lobby_details.Game.filter") as mock_game_filter,
        patch("src.controllers.lobby_details.fetch_lobby_details_from_db") as mock_fetch,
    ):
        mock_game_filter.return_value.first.return_value = mock_game
        mock_game.fetch_related = AsyncMock()
        mock_game.players = mock_players
        mock_fetch.return_value = LobbyDetails(
            server_info="TestGame - Turn 1",
            player_status=[PlayerStatus(name="Player1", turn_status="Turn played")],
            turn="1",
            time_left="1 day left",
        )
        result = await get_lobby_details("TestGame", use_db=True)

    assert isinstance(result, list)
    assert len(result) > 0
    assert any("TestGame" in str(block) for block in result)
    assert any("Player1" in str(block) for block in result)


@pytest.mark.asyncio
async def test_get_lobby_details_web_source_failure():
    with patch("src.controllers.lobby_details.fetch_lobby_details_from_web") as mock_fetch:
        mock_fetch.side_effect = ValueError("Failed to fetch lobby details from web source")
        result = await get_lobby_details("server_name", use_db=False)
        assert result == []  # Expect an empty list instead of raising an error


@pytest.mark.asyncio
async def test_get_lobby_details_db_source_failure():
    with patch("src.controllers.lobby_details.fetch_lobby_details_from_db") as mock_fetch:
        mock_fetch.return_value = None
        result = await get_lobby_details("NonexistentGame", use_db=True)
        assert result == []  # Expect an empty list instead of raising an error


def test_format_lobby_details():
    lobby_details = LobbyDetails(
        server_info="Test Server, Turn 1 (1 day left)",
        player_status=[PlayerStatus(name="Player1", turn_status="Turn played")],
        turn="1",
        time_left="1 day left",
    )
    result = format_lobby_details(lobby_details)

    assert isinstance(result, list)
    assert len(result) > 0
    assert any("Test Server, Turn 1" in str(block) for block in result)
    assert any("Player1" in str(block) for block in result)
