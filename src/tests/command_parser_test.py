import pytest

from src.controllers.command_parser import command_parser_wrapper


@pytest.mark.asyncio()
async def test_should_return_help_command_output_when_help_command_is_given():
    command = "help"
    result = await command_parser_wrapper(command)
    assert result == "this should return a dynamic string based on specific command"


@pytest.mark.asyncio()
async def test_should_return_unknown_command_when_unknown_command_is_given():
    command = "unknown"
    result = await command_parser_wrapper(command)
    assert result == "command not recognised"


@pytest.mark.asyncio()
async def test_should_return_unknown_command_when_empty_command_is_given():
    command = ""
    result = await command_parser_wrapper(command)
    assert result == "command not recognised"


@pytest.mark.asyncio()
async def test_should_return_invalid_command_when_game_command_is_incomplete():
    command = "game add"
    result = await command_parser_wrapper(command)
    assert result == "command is invalid please check spelling or help command and try again"


@pytest.mark.asyncio()
async def test_should_return_invalid_command_when_player_command_is_incomplete():
    command = "player Handsomeboiz_MA"
    result = await command_parser_wrapper(command)
    assert result == "command is invalid please check spelling or help command and try again"
