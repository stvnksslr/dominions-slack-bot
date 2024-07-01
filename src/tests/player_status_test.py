from src.models.app.player_status import PlayerStatus


def test_player_status_short_name_returns_first_part_of_name():
    player_status = PlayerStatus(name="Player1, Player2", turn_status="Turn played")
    assert player_status.short_name() == "player1"


def test_player_status_short_name_handles_single_name():
    player_status = PlayerStatus(name="Player1", turn_status="Turn played")
    assert player_status.short_name() == "player1"


def test_player_status_short_name_handles_empty_name():
    player_status = PlayerStatus(name="", turn_status="Turn played")
    assert player_status.short_name() == ""
