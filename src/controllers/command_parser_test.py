from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.controllers.command_parser import command_parser_wrapper, game_command, nickname_game


@pytest.mark.asyncio()
async def test_should_return_help_command_output_when_help_command_is_given() -> None:
    command = "help"
    result = await command_parser_wrapper(command=command)
    assert result == "this should return a dynamic string based on specific command"


@pytest.mark.asyncio()
async def test_should_return_unknown_command_when_unknown_command_is_given() -> None:
    command = "unknown"
    result = await command_parser_wrapper(command=command)
    assert result == "command not recognised"


@pytest.mark.asyncio()
async def test_should_return_unknown_command_when_empty_command_is_given() -> None:
    command = ""
    result = await command_parser_wrapper(command=command)
    assert result == "command not recognised"


@pytest.mark.asyncio()
async def test_should_return_unknown_command_when_whitespace_command_is_given() -> None:
    command = " "
    result = await command_parser_wrapper(command=command)
    assert result == "command not recognised"


@pytest.mark.asyncio()
async def test_should_return_invalid_command_when_game_command_is_incomplete() -> None:
    command = "game add"
    result = await command_parser_wrapper(command=command)
    assert result == "command is invalid please check spelling or help command and try again"


@pytest.mark.asyncio()
async def test_should_return_invalid_command_when_player_command_is_incomplete() -> None:
    command = "player Handsomeboiz_MA"
    result = await command_parser_wrapper(command=command)
    assert result == "command is invalid please check spelling or help command and try again"


@patch("src.controllers.command_parser.add_game", new_callable=AsyncMock)
@pytest.mark.asyncio()
async def test_game_command_add_game(mock_add_game) -> None:
    mock_add_game.return_value = "game added"
    result = await game_command(command_list=["game", "add", "game_name"])
    assert result == "game added"


@patch("src.controllers.command_parser.remove_game", new_callable=AsyncMock)
@pytest.mark.asyncio()
async def test_game_command_remove_game(mock_remove_game):
    mock_remove_game.return_value = "game removed"
    result = await game_command(["game", "remove", "game_name"])
    assert result == "game removed"


@patch("src.controllers.command_parser.nickname_game", new_callable=AsyncMock)
@pytest.mark.asyncio()
async def test_game_command_nickname_game(mock_nickname_game) -> None:
    mock_nickname_game.return_value = "game nickname updated"
    result = await game_command(command_list=["game", "nickname", "game_name", "game_nickname"])
    assert result == "game nickname updated"


@patch("src.controllers.command_parser.unknown_command", new_callable=AsyncMock)
@pytest.mark.asyncio()
async def test_game_command_unknown_command(mock_unknown_command) -> None:
    mock_unknown_command.return_value = "unknown command"
    result = await game_command(command_list=["game", "unknown", "game_name"])
    assert result == "unknown command"


@patch("src.models.db.Game.filter", new_callable=MagicMock)
@pytest.mark.asyncio()
async def test_nickname_game_updates_nickname_on_valid_command(mock_filter) -> None:
    mock_filter.return_value.update = AsyncMock()
    result = await nickname_game(command_list=["game", "nickname", "game_name", "game_nickname"])
    assert result == "game game_name nickname game_nickname"


@patch("src.models.db.Game.filter", new_callable=AsyncMock)
@pytest.mark.asyncio()
async def test_nickname_game_returns_invalid_command_on_insufficient_arguments(mock_filter) -> None:
    result = await nickname_game(command_list=["game", "nickname", "game_name"])
    assert result == "command is invalid please check spelling or help command and try again"
