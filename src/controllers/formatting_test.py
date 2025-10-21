from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponse, ClientSession
from tortoise import Tortoise

from src.controllers.formatting import (
    create_game_details_block,
    create_game_details_block_from_db,
    create_nations_block,
    create_nations_block_from_db,
    get_emoji,
)
from src.controllers.lobby_details import (
    fetch_lobby_details_from_db,
    fetch_lobby_details_from_web,
    format_lobby_details,
    get_lobby_details,
)
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game, Player


class MockConnectionError(Exception):
    pass


@pytest.fixture
async def _initialize_tortoise():  # noqa: ANN202
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["src.models.db"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
def mock_html_content() -> str:
    return """
    <html><body>
        <tr>Server Info, Turn 1 (1 day left)</tr>
        <tr><td>Player1</td><td>Turn played</td></tr>
    </body></html>
    """


@pytest.fixture
def mock_game() -> MagicMock:
    return MagicMock(spec=Game, name="TestGame", turn="1", time_left="1 day left")


@pytest.fixture
def mock_players() -> list[MagicMock]:
    return [MagicMock(spec=Player, short_name="Player1", turn_status="Turn played")]


@pytest.mark.asyncio
async def test_get_lobby_details_web_source(mock_html_content: str) -> None:
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
async def test_get_lobby_details_db_source(mock_game: MagicMock, mock_players: list[MagicMock]) -> None:
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
async def test_get_lobby_details_web_source_failure() -> None:
    with patch("src.controllers.lobby_details.fetch_lobby_details_from_web") as mock_fetch:
        mock_fetch.side_effect = ValueError("Failed to fetch lobby details from web source")
        result = await get_lobby_details("server_name", use_db=False)
        assert result == []  # Expect an empty list instead of raising an error


@pytest.mark.asyncio
async def test_get_lobby_details_db_source_failure() -> None:
    with patch("src.controllers.lobby_details.fetch_lobby_details_from_db") as mock_fetch:
        mock_fetch.return_value = None
        result = await get_lobby_details("NonexistentGame", use_db=True)
        assert result == []  # Expect an empty list instead of raising an error


def test_format_lobby_details() -> None:
    lobby_details = LobbyDetails(
        server_info="Test Server, Turn 1 (1 day left)",
        player_status=[PlayerStatus(name="Player1", turn_status="Turn played", nickname="Nick1")],
        turn="1",
        time_left="1 day left",
    )
    result = format_lobby_details(lobby_details)

    assert isinstance(result, list)
    assert len(result) > 0
    assert any("Test Server, Turn 1" in str(block) for block in result)
    assert any("Player1" in str(block) for block in result)
    assert any("Nick1" in str(block) for block in result)


@pytest.mark.asyncio
async def test_fetch_lobby_details_from_web() -> None:
    mock_html = """
    <html><body>
        <tr>Server Info, Turn 2 (2 days left)</tr>
        <tr><td>Player1</td><td>Turn played</td></tr>
        <tr><td>Player2</td><td>Turn unfinished</td></tr>
    </body></html>
    """
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.text.return_value = mock_html
    mock_session = AsyncMock(spec=ClientSession)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch("src.controllers.lobby_details.ClientSession") as mock_client_session:
        mock_client_session.return_value.__aenter__.return_value = mock_session

        result = await fetch_lobby_details_from_web("test_server")

    assert isinstance(result, LobbyDetails)
    assert result.server_info == "server info, turn 2 (2 days left)"
    assert result.turn == "2"
    assert result.time_left == "2 days left"
    assert len(result.player_status) == 2
    assert result.player_status[0].name == "Player1"
    assert result.player_status[0].turn_status == "Turn played"
    assert result.player_status[1].name == "Player2"
    assert result.player_status[1].turn_status == "Turn unfinished"


@pytest.mark.asyncio
@pytest.mark.usefixtures("_initialize_tortoise")
async def test_fetch_lobby_details_from_db() -> None:
    mock_game = await Game.create(name="TestGame", turn=3, time_left="3 days left")
    await Player.create(
        nation="Nation1",
        short_name="Player1",
        turn_status="Turn played",
        player_name="Nick1",
        game=mock_game,
    )
    await Player.create(
        nation="Nation2",
        short_name="Player2",
        turn_status="Turn unfinished",
        player_name=None,
        game=mock_game,
    )

    result = await fetch_lobby_details_from_db("TestGame")

    assert isinstance(result, LobbyDetails)
    assert result.server_info == "TestGame - Turn 3"
    assert result.turn == "3"
    assert result.time_left == "3 days left"
    assert len(result.player_status) == 2
    assert result.player_status[0].name == "Player1"
    assert result.player_status[0].turn_status == "Turn played"
    assert result.player_status[0].nickname == "Nick1"
    assert result.player_status[1].name == "Player2"
    assert result.player_status[1].turn_status == "Turn unfinished"
    assert result.player_status[1].nickname is None


def test_get_emoji() -> None:
    assert get_emoji("Turn played") == ":white_check_mark:"
    assert get_emoji("Turn unfinished") == ":question:"
    assert get_emoji("Eliminated") == ":dom_rip:"
    assert get_emoji("-") == ":x:"
    assert get_emoji("Unknown status") == ":gungoose:"


def test_create_nations_block() -> None:
    player_list = [
        PlayerStatus(name="Player1", turn_status="Turn played"),
        PlayerStatus(name="Player2", turn_status="Turn unfinished"),
    ]
    result = create_nations_block(player_list)
    assert len(result) == 2
    assert result[0]["type"] == "section"
    assert ":white_check_mark: - *Player1*" in result[0]["text"]["text"]
    assert ":question: - *Player2*" in result[1]["text"]["text"]


def test_create_game_details_block() -> None:
    lobby_details = LobbyDetails(
        server_info="Test Server, Turn 1 (1 day left)",
        player_status=[],
        turn="1",
        time_left="1 day left",
    )
    result = create_game_details_block(lobby_details)
    assert len(result) == 7
    assert result[0]["type"] == "header"
    assert result[0]["text"]["text"] == "Dominions Times"
    assert "Test Server, Turn 1 (1 day left)" in result[4]["text"]["text"]


def test_create_game_details_block_from_db() -> None:
    lobby_details = LobbyDetails(
        server_info="Test Server - Turn 2",
        player_status=[],
        turn="2",
        time_left="2 days left",
    )
    result = create_game_details_block_from_db(lobby_details)
    assert len(result) == 9
    assert result[0]["type"] == "header"
    assert result[0]["text"]["text"] == "Dominions Times"
    assert "Test Server - Turn 2" in result[4]["text"]["text"]
    assert "Turn: 2" in result[5]["text"]["text"]
    assert "2 days left" in result[6]["text"]["text"]


def test_create_nations_block_from_db() -> None:
    player_list = [
        PlayerStatus(name="Player1", turn_status="Turn played", nickname="Nick1"),
        PlayerStatus(name="Player2", turn_status="Turn unfinished", nickname=None),
    ]
    result = create_nations_block_from_db(player_list)
    assert len(result) == 2
    assert result[0]["type"] == "section"
    assert ":white_check_mark: - *Player1* - Nick1" in result[0]["text"]["text"]
    assert ":question: - *Player2*" in result[1]["text"]["text"]
