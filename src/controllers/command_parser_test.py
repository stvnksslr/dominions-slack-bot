from unittest.mock import AsyncMock, patch

import pytest

from src.controllers.command_parser import command_parser_wrapper


@pytest.mark.parametrize(
    "command",
    [
        "",
        "   ",
        "bogus",
        "game",
        "game bogus",
        "game add",
        "game nickname onlygame",
        "game list extra",
        "game status mygame",
        "turn extra",
        "check",
        "player onlygame",
        "help game extra",
    ],
)
async def test_bad_input_never_leaks_python_internals(command: str) -> None:
    """Wrong arity used to raise TypeError and post the raw message to the channel."""
    blocks, ephemeral = await command_parser_wrapper(command)

    assert blocks, "an empty block list is rejected by Slack, so the user sees nothing"
    assert ephemeral, "errors and usage must not be broadcast to the channel"

    rendered = str(blocks)
    for leak in ("execute()", "positional argument", "Traceback", "Command object"):
        assert leak not in rendered, f"leaked {leak!r}: {rendered}"


async def test_bare_game_shows_game_help() -> None:
    blocks, ephemeral = await command_parser_wrapper("game")

    assert ephemeral
    assert "Game Commands Help" in str(blocks)


async def test_wrong_arity_shows_usage() -> None:
    blocks, _ = await command_parser_wrapper("game add")

    assert "`/dom game add [game_name]`" in str(blocks)


async def test_unknown_game_subcommand_lists_valid_ones() -> None:
    blocks, _ = await command_parser_wrapper("game frobnicate")

    rendered = str(blocks)
    assert "frobnicate" in rendered
    assert "primary" in rendered


async def test_routing_is_case_insensitive() -> None:
    upper, _ = await command_parser_wrapper("HELP GAME")
    lower, _ = await command_parser_wrapper("help game")

    assert upper == lower


async def test_status_commands_are_channel_visible() -> None:
    fake = AsyncMock(return_value=[{"type": "divider"}])
    with patch("src.commands.check_commands.get_lobby_details", new=fake):
        _, ephemeral = await command_parser_wrapper("check mygame")

    assert ephemeral is False


async def test_command_body_failure_is_reported_without_the_exception_text() -> None:
    fake = AsyncMock(side_effect=RuntimeError("mysql://user:hunter2@db/dominions unreachable"))
    with patch("src.commands.check_commands.get_lobby_details", new=fake):
        blocks, ephemeral = await command_parser_wrapper("check mygame")

    assert ephemeral
    assert "hunter2" not in str(blocks), "connection strings must never reach Slack"
    assert "Something went wrong" in str(blocks)
