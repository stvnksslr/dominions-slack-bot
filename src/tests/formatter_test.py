import pytest

from src.controllers.formatting import create_game_details_block, create_nations_block
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus


def test_create_game_details_block_with_valid_lobby_details():
    mock_player_status = PlayerStatus(name="some nation", turn_status="not played", turn_emoji=":sun:")
    lobby_details = LobbyDetails(server_info="Server Info", player_status=[mock_player_status], turn_status="Turn played", time_left="1 hour", turn="2")
    result = create_game_details_block(lobby_details)
    assert len(result) == 6
    assert result[3]["text"]["text"] == "Server Info"


def test_create_game_details_block_with_empty_lobby_details():
    lobby_details = LobbyDetails(server_info="", player_status=[], turn_status="Turn played", time_left="1 hour", turn="2")
    result = create_game_details_block(lobby_details)
    assert len(result) == 6
    assert result[3]["text"]["text"] == ""


def test_create_nations_block_with_valid_player_list():
    player_list = [
        PlayerStatus(name="Player1", turn_status="Turn played"),
        PlayerStatus(name="Player2", turn_status="-"),
    ]
    result = create_nations_block(player_list)
    assert len(result) == 2
    assert result[0]["text"]["text"] == ":white_check_mark: - *Player1*"
    assert result[1]["text"]["text"] == ":x: - *Player2*"


def test_create_nations_block_with_empty_player_list():
    player_list = []
    result = create_nations_block(player_list)
    assert len(result) == 0


def test_create_nations_block_with_none_player_list():
    with pytest.raises(TypeError):
        create_nations_block(None)
