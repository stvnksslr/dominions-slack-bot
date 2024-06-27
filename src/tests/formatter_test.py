from src.controllers.formatting import create_game_details_block, create_nations_block
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus


def create_lobby_details(server_info, player_status, turn_status, time_left, turn):
    return LobbyDetails(server_info=server_info, player_status=player_status, turn=turn_status, time_left=time_left)


def create_player_status(name, turn_status, turn_emoji=None):
    return PlayerStatus(name=name, turn_status=turn_status, turn_emoji=turn_emoji)


def test_create_game_details_block_length():
    lobby_details = create_lobby_details(
        "Server Info", [create_player_status("some nation", "not played", ":sun:")], "Turn played", "1 hour", "2"
    )
    result = create_game_details_block(lobby_details)
    assert len(result) == 6


def test_create_game_details_block_text():
    lobby_details = create_lobby_details(
        "Server Info", [create_player_status("some nation", "not played", ":sun:")], "Turn played", "1 hour", "2"
    )
    result = create_game_details_block(lobby_details)
    assert result[3]["text"]["text"] == "Server Info"


def test_create_game_details_block_length_empty():
    lobby_details = create_lobby_details("", [], "Turn played", "1 hour", "2")
    result = create_game_details_block(lobby_details)
    assert len(result) == 6


def test_create_game_details_block_text_empty():
    lobby_details = create_lobby_details("", [], "Turn played", "1 hour", "2")
    result = create_game_details_block(lobby_details)
    assert result[3]["text"]["text"] == ""


def test_create_nations_block_length():
    player_list = [create_player_status("Player1", "Turn played"), create_player_status("Player2", "-")]
    result = create_nations_block(player_list)
    assert len(result) == 2


def test_create_nations_block_text_player1():
    player_list = [create_player_status("Player1", "Turn played"), create_player_status("Player2", "-")]
    result = create_nations_block(player_list)
    assert result[0]["text"]["text"] == ":white_check_mark: - *Player1*"


def test_create_nations_block_text_player2():
    player_list = [create_player_status("Player1", "Turn played"), create_player_status("Player2", "-")]
    result = create_nations_block(player_list)
    assert result[1]["text"]["text"] == ":x: - *Player2*"


def test_create_nations_block_empty():
    result = create_nations_block([])
    assert len(result) == 0
