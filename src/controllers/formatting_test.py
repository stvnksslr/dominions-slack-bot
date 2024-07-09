from unittest.mock import patch

import pytest

from src.controllers.formatting import (
    create_game_details_block,
    create_game_details_block_from_db,
    create_nations_block,
    create_nations_block_from_db,
    get_emoji,
)
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Player


def create_mock_player(turn_status, name):
    return type("Player", (object,), {"turn_status": turn_status, "name": name})


def create_mock_game(name, turn, time_left):
    return type("Game", (object,), {"name": name, "turn": turn, "time_left": time_left})


def create_mock_player_with_shortname(turn_status, short_name, player_name):
    return type("Player", (object,), {"turn_status": turn_status, "short_name": short_name, "player_name": player_name})


def test_get_emoji_returns_check_mark_for_turn_played():
    assert get_emoji("Turn played") == ":white_check_mark:"


def test_get_emoji_returns_question_for_turn_unfinished():
    assert get_emoji("Turn unfinished") == ":question:"


def test_get_emoji_returns_cross_for_no_turn():
    assert get_emoji("-") == ":x:"


def test_get_emoji_returns_gungoose_for_unknown_status():
    assert get_emoji("Unknown status") == ":gungoose:"


def test_get_emoji_returns_gungoose_for_empty_status():
    assert get_emoji("") == ":gungoose:"


@pytest.mark.parametrize("status", [None, 123, [], {}])
def test_get_emoji_returns_gungoose_for_invalid_status(status):
    assert get_emoji(status) == ":gungoose:"


def create_nations_block_creates_correct_block_for_single_player():
    player = create_mock_player("Turn played", "Player1")
    result = create_nations_block([player])
    expected = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":white_check_mark: - *Player1*"},
        }
    ]
    assert result == expected


def create_nations_block_creates_correct_block_for_multiple_players():
    players = [create_mock_player("Turn played", "Player1"), create_mock_player("-", "Player2")]
    result = create_nations_block(players)
    expected = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":white_check_mark: - *Player1*"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":x: - *Player2*"},
        },
    ]
    assert result == expected


def create_nations_block_handles_empty_player_list():
    result = create_nations_block([])
    assert result == []


def create_nations_block_handles_none_player_list():
    result = create_nations_block(None)
    assert result == []


def create_mock_lobby_details(server_info) -> LobbyDetails:
    return LobbyDetails(
        server_info=server_info, turn="1", time_left="", player_status=[PlayerStatus(name="name", turn_status="")]
    )


def create_game_details_block_creates_correct_block_for_valid_server_info():
    lobby_details = create_mock_lobby_details("Server Info")
    result = create_game_details_block(lobby_details)
    expected = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :freak_lord: *Update* :freak_lord:",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Server Info"},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    assert result == expected


def create_game_details_block_handles_empty_server_info():
    lobby_details = create_mock_lobby_details("")
    result = create_game_details_block(lobby_details)
    expected = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :freak_lord: *Update* :freak_lord:",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ""},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    assert result == expected


def create_game_details_block_from_db_creates_correct_block():
    game = create_mock_game("Game1", 1, "1 day left")
    result = create_game_details_block_from_db(game)  # type: ignore
    expected = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :freak_lord: *Update* :freak_lord:",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Game1"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Turn: 1"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "1 day left"},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    assert result == expected


def create_game_details_block_from_db_handles_none_game():
    result = create_game_details_block_from_db(None)  # type: ignore
    expected = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Dominions Times"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " :freak_lord: *Update* :freak_lord:",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ""},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Player List*"}},
    ]
    assert result == expected


def create_nations_block_from_db_creates_correct_block_for_single_player():
    player = create_mock_player_with_shortname("Turn played", "ShortName1", "Player1")
    result = create_nations_block_from_db([player])
    expected = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":white_check_mark: - *ShortName1* - Player1"},
        }
    ]
    assert result == expected


def create_nations_block_from_db_creates_correct_block_for_multiple_players():
    players = [
        create_mock_player_with_shortname("Turn played", "ShortName1", "Player1"),
        create_mock_player_with_shortname("-", "ShortName2", "Player2"),
    ]
    result = create_nations_block_from_db(players)
    expected = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":white_check_mark: - *ShortName1* - Player1"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":x: - *ShortName2* - Player2"},
        },
    ]
    assert result == expected


def create_nations_block_from_db_handles_empty_player_list():
    result = create_nations_block_from_db([])
    assert result == []


def create_nations_block_from_db_handles_none_player_list():
    result = create_nations_block_from_db(None)
    assert result == []


@patch("src.controllers.formatting.get_emoji")
def test_create_nations_block_from_db_formats_player_list(mock_get_emoji):
    mock_get_emoji.return_value = ":emoji:"
    player_list = [
        Player(turn_status="Turn played", player_name="Player1", short_name="P1"),
        Player(turn_status="Turn unfinished", player_name=None, short_name="P2"),
    ]
    result = create_nations_block_from_db(player_list)
    assert len(result) == 2
    assert result[0]["text"]["text"] == ":emoji: - *P1*  - Player1"
    assert result[1]["text"]["text"] == ":emoji: - *P2* "


@patch("src.controllers.formatting.get_emoji")
def test_create_nations_block_from_db_handles_empty_player_list(mock_get_emoji):
    mock_get_emoji.return_value = ":emoji:"
    player_list = []
    result = create_nations_block_from_db(player_list)
    assert len(result) == 0


@patch("src.controllers.formatting.get_emoji")
def test_create_nations_block_formats_player_list(mock_get_emoji):
    mock_get_emoji.return_value = ":emoji:"
    player_list = [
        PlayerStatus(turn_status="Turn played", name="Player1"),
        PlayerStatus(turn_status="Turn unfinished", name="Player2"),
    ]
    result = create_nations_block(player_list)
    assert len(result) == 2
    assert result[0]["text"]["text"] == ":emoji: - *Player1*"
    assert result[1]["text"]["text"] == ":emoji: - *Player2*"


@patch("src.controllers.formatting.get_emoji")
def test_create_nations_block_handles_empty_player_list(mock_get_emoji):
    mock_get_emoji.return_value = ":emoji:"
    player_list = []
    result = create_nations_block(player_list)
    assert len(result) == 0
