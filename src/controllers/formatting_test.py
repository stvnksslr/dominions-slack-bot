from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientResponse, ClientSession
from tortoise import Tortoise

from src.controllers.formatting import (
    create_game_details_block,
    create_nations_block,
    get_emoji,
)
from src.controllers.lobby_details import (
    fetch_lobby_details_from_db,
    fetch_lobby_details_from_web,
    fetch_lobby_details_live,
    format_lobby_details,
    get_lobby_details,
)
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game, Player


@pytest.fixture
async def _initialize_tortoise():  # noqa: ANN202
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["src.models.db"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


def _patched_session(html: str):  # noqa: ANN202
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.text.return_value = html
    mock_session = AsyncMock(spec=ClientSession)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    patcher = patch("src.controllers.lobby_details.ClientSession")
    mock_client_session = patcher.start()
    mock_client_session.return_value.__aenter__.return_value = mock_session
    return patcher


async def test_get_lobby_details_web_source_failure() -> None:
    """A failure must render as blocks — Slack rejects a message with an empty blocks array."""
    with patch("src.controllers.lobby_details.fetch_lobby_details_from_web") as mock_fetch:
        mock_fetch.side_effect = ValueError("boom")
        result = await get_lobby_details("server_name", use_db=False)

    assert result, "empty block list would be silently dropped by Slack"
    assert "Error" in str(result)
    assert "boom" not in str(result), "internal error text must not reach the channel"


async def test_get_lobby_details_db_source_failure() -> None:
    with patch("src.controllers.lobby_details.fetch_lobby_details_from_db") as mock_fetch:
        mock_fetch.return_value = None
        result = await get_lobby_details("NonexistentGame", use_db=True)

    assert result
    assert "NonexistentGame" in str(result)


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


async def test_fetch_lobby_details_from_web() -> None:
    mock_html = """
    <html><body>
        <tr>Server Info, Turn 2 (2 days left)</tr>
        <tr><td>Player1</td><td>Turn played</td></tr>
        <tr><td>Player2</td><td>Turn unfinished</td></tr>
    </body></html>
    """
    patcher = _patched_session(mock_html)
    try:
        result = await fetch_lobby_details_from_web("test_server")
    finally:
        patcher.stop()

    assert isinstance(result, LobbyDetails)
    assert result.server_info == "server info, turn 2 (2 days left)"
    assert result.turn == "2"
    assert result.time_left == "2 days left"
    assert len(result.player_status) == 2
    assert result.player_status[0].name == "Player1"
    assert result.player_status[0].turn_status == "Turn played"
    assert result.player_status[1].name == "Player2"
    assert result.player_status[1].turn_status == "Turn unfinished"


@pytest.mark.parametrize(
    ("server_info", "expected_turn", "expected_time"),
    [
        ("Nocturne, Turn 42 (2 hours left)", "42", "2 hours left"),
        ("Saturnalia, Turn 7 (1 day left)", "7", "1 day left"),
        ("Blitz (fast), Turn 3 (12 hours left)", "3", "12 hours left"),
        ("Plain, Turn 1 (finished)", "1", "finished"),
    ],
)
async def test_fetch_lobby_details_turn_parsing(server_info: str, expected_turn: str, expected_time: str) -> None:
    """A game name containing 'turn' or parentheses must not be mistaken for the turn counter/timer."""
    patcher = _patched_session(f"<html><body><tr>{server_info}</tr></body></html>")
    try:
        result = await fetch_lobby_details_from_web("nocturne")
    finally:
        patcher.stop()

    assert result is not None
    assert result.turn == expected_turn
    assert result.time_left == expected_time


async def test_fetch_lobby_details_from_web_no_turn_returns_none() -> None:
    patcher = _patched_session("<html><body><tr>lobby is not started yet</tr></body></html>")
    try:
        result = await fetch_lobby_details_from_web("test_server")
    finally:
        patcher.stop()

    assert result is None


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


@pytest.mark.usefixtures("_initialize_tortoise")
async def test_fetch_lobby_details_live_keeps_nicknames() -> None:
    """Refreshing a tracked game must not drop the player names only the db knows about."""
    game = await Game.create(name="TestGame", turn=1, time_left="1 day left")
    await Player.create(
        nation="Ermor, Ashen Empire", short_name="Ermor", turn_status="-", player_name="Nick1", game=game
    )

    patcher = _patched_session(
        "<html><body><tr>TestGame, Turn 2 (2 days left)</tr>"
        "<tr><td>Ermor, Ashen Empire</td><td>Turn played</td></tr></body></html>"
    )
    try:
        result = await fetch_lobby_details_live("TestGame")
    finally:
        patcher.stop()

    assert result is not None
    assert result.turn == "2", "live data, not the stale cached turn"
    assert result.player_status[0].nickname == "Nick1"


@pytest.mark.usefixtures("_initialize_tortoise")
async def test_cached_turn_card_has_refresh_button() -> None:
    game = await Game.create(name="TestGame", turn=3, time_left="3 days left")
    await Player.create(nation="Nation1", short_name="Player1", turn_status="Turn played", game=game)

    blocks = await get_lobby_details("TestGame", use_db=True)

    actions = [block for block in blocks if block["type"] == "actions"]
    assert len(actions) == 1
    assert "refresh_game_status" in {element["action_id"] for element in actions[0]["elements"]}
    assert any("Cached" in str(block) for block in blocks)


def test_get_emoji() -> None:
    assert get_emoji("Turn played") == ":white_check_mark:"
    assert get_emoji("Turn unfinished") == ":question:"
    assert get_emoji("Eliminated") == ":dom_rip:"
    assert get_emoji("-") == ":x:"
    assert get_emoji("Unknown status") == ":gungoose:"


def test_create_game_details_block() -> None:
    lobby_details = LobbyDetails(
        server_info="Test Server, Turn 1 (1 day left)",
        player_status=[],
        turn="1",
        time_left="1 day left",
    )
    result = create_game_details_block(lobby_details)
    assert result[0]["type"] == "header"
    assert result[0]["text"]["text"] == "Dominions Times"
    assert "Test Server, Turn 1 (1 day left)" in result[1]["text"]["text"]
    assert "Turn 1 · 1 day left" in result[1]["text"]["text"]
    assert not [block for block in result if block["type"] == "actions"]


def test_create_game_details_block_adds_buttons_when_named() -> None:
    lobby_details = LobbyDetails(server_info="info", player_status=[], turn="1", time_left="1 day left")
    result = create_game_details_block(lobby_details, game_name="MyGame")

    actions = [block for block in result if block["type"] == "actions"]
    assert len(actions) == 1
    action_ids = {element["action_id"] for element in actions[0]["elements"]}
    assert action_ids == {"refresh_game_status", "set_primary_game"}
    assert all(element["value"] == "MyGame" for element in actions[0]["elements"])


def test_create_game_details_block_hides_set_primary_on_primary_game() -> None:
    lobby_details = LobbyDetails(
        server_info="info", player_status=[], turn="1", time_left="1 day left", is_primary=True
    )
    result = create_game_details_block(lobby_details, game_name="MyGame")

    actions = [block for block in result if block["type"] == "actions"]
    assert len(actions) == 1
    assert {element["action_id"] for element in actions[0]["elements"]} == {"refresh_game_status"}


def test_create_game_details_block_is_identical_for_cached_and_live() -> None:
    """The cached card must offer the same refresh/primary buttons as the live one."""
    cached = LobbyDetails(server_info="MyGame - Turn 2", player_status=[], turn="2", time_left="2 days left")
    live = LobbyDetails(server_info="mygame, turn 2 (2 days left)", player_status=[], turn="2", time_left="2 days left")

    assert create_game_details_block(cached, "MyGame") == create_game_details_block(live, "MyGame")


def test_create_game_details_block_omits_missing_time_left() -> None:
    lobby_details = LobbyDetails(server_info="info", player_status=[], turn="9", time_left=None)
    result = create_game_details_block(lobby_details, game_name="MyGame")

    assert result[1]["text"]["text"].endswith("Turn 9")
    assert "None" not in result[1]["text"]["text"]


def test_create_nations_block() -> None:
    player_list = [
        PlayerStatus(name="Player1", turn_status="Turn played", nickname="Nick1"),
        PlayerStatus(name="Player2", turn_status="Turn unfinished", nickname=None),
        PlayerStatus(name="Ermor, Ashen Empire", turn_status="Turn played", nickname=None),
    ]
    result = create_nations_block(player_list)
    assert len(result) == 3
    assert result[0]["type"] == "section"
    assert ":white_check_mark: - *Player1* - Nick1" in result[0]["text"]["text"]
    assert ":question: - *Player2*" in result[1]["text"]["text"]
    # scraped nation titles get trimmed to the short name the db card already shows
    assert ":white_check_mark: - *Ermor*" in result[2]["text"]["text"]
