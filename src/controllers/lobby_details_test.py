from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponse, ClientSession

from src.controllers.lobby_details import fetch_lobby_details, format_lobby_details
from src.models.app.lobby_details import LobbyDetails


class MockConnectionError(BaseException):
    pass


@pytest.mark.asyncio
async def test_fetch_lobby_details_returns_lobby_details_on_success():
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.text.return_value = (
        "<html><body><tr>Server Info, Turn 1 (1 day "
        "left)</tr><tr><td>Player1</td><td>Turn played</td></tr></body></html>"
    )

    mock_session = AsyncMock(spec=ClientSession)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch("src.controllers.lobby_details.ClientSession") as mock_client_session:
        mock_client_session.return_value.__aenter__.return_value = mock_session
        result = await fetch_lobby_details("server_name")

    assert isinstance(result, LobbyDetails)
    assert result.server_info == "server info, turn 1 (1 day left)"
    assert result.turn == "1"
    assert result.time_left == "1 day left"
    assert len(result.player_status) == 1
    assert result.player_status[0].name == "Player1"
    assert result.player_status[0].turn_status == "Turn played"


@pytest.mark.asyncio
async def test_fetch_lobby_details_raises_exception_on_failure():
    mock_session = AsyncMock(spec=ClientSession)
    mock_session.get.side_effect = MockConnectionError()

    with patch("src.controllers.lobby_details.ClientSession") as mock_client_session:
        mock_client_session.return_value.__aenter__.return_value = mock_session
        with pytest.raises(MockConnectionError):
            await fetch_lobby_details(server_name="server_name")


@patch("src.controllers.formatting.create_nations_block")
@patch("src.controllers.formatting.create_game_details_block")
def test_format_lobby_details_combines_blocks(mock_create_game_details_block, mock_create_nations_block):
    mock_create_game_details_block.return_value = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "Game Details"}}
    ]
    mock_create_nations_block.return_value = [{"type": "section", "text": {"type": "mrkdwn", "text": "Nations"}}]
    lobby_details = LobbyDetails(server_info="info", player_status=[], turn="turn", time_left="time_left")
    result = format_lobby_details(lobby_details=lobby_details)
    expected_response = [
        {"text": {"text": "Dominions Times", "type": "plain_text"}, "type": "header"},
        {"type": "divider"},
        {"text": {"text": " :freak_lord: *Update* :freak_lord:", "type": "mrkdwn"}, "type": "section"},
        {"text": {"text": "info", "type": "mrkdwn"}, "type": "section"},
        {"type": "divider"},
        {"text": {"text": "*Player List*", "type": "mrkdwn"}, "type": "section"},
    ]
    assert result == expected_response
