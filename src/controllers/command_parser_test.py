from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from tortoise.exceptions import DBConnectionError

from src.controllers.command_parser import (
    PlayerCommandResult,
    add_game,
    command_parser_wrapper,
    game_command,
    handle_check_command,
    handle_turn_command,
    help_command,
    help_command_wrapper,
    list_games,
    nickname_game,
    player_command,
    set_game_status,
    set_primary,
    update_player,
)
from src.models.db import Game, Player


@pytest.mark.asyncio
async def test_should_return_help_command_output_when_help_command_is_given() -> None:
    command = "help"
    result = await command_parser_wrapper(command=command)
    assert "Dominions 6 Slack Bot Help" in result
    assert "Here are the available commands:" in result
    assert "Game:" in result
    assert "Player:" in result
    assert "Check:" in result
    assert "Turn:" in result
    assert "For more detailed information on a specific command, use: `/dom help [command]`" in result


@pytest.mark.asyncio
async def test_should_return_unknown_command_when_unknown_command_is_given() -> None:
    command = "unknown"
    result = await command_parser_wrapper(command=command)
    assert result == "command not recognised"


@pytest.mark.asyncio
async def test_should_return_unknown_command_when_empty_command_is_given() -> None:
    command = ""
    result = await command_parser_wrapper(command=command)
    assert result == "command not recognised"


@pytest.mark.asyncio
async def test_should_return_unknown_command_when_whitespace_command_is_given() -> None:
    command = " "
    result = await command_parser_wrapper(command=command)
    assert result == "command not recognised"


@pytest.mark.asyncio
async def test_should_return_invalid_command_when_game_command_is_incomplete() -> None:
    command = "game add"
    result = await command_parser_wrapper(command=command)
    assert result == "command is invalid please check spelling or help command and try again"


@pytest.mark.asyncio
async def test_should_return_invalid_command_when_player_command_is_incomplete() -> None:
    command = "player Handsomeboiz_MA"
    result = await command_parser_wrapper(command=command)
    assert result == "command is invalid please check spelling or help command and try again"


@patch("src.controllers.command_parser.add_game", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_game_command_add_game(mock_add_game) -> None:
    mock_add_game.return_value = "game added"
    result = await game_command(command_list=["game", "add", "game_name"])
    assert result == "game added"


@patch("src.controllers.command_parser.remove_game", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_game_command_remove_game(mock_remove_game):
    mock_remove_game.return_value = "game removed"
    result = await game_command(["game", "remove", "game_name"])
    assert result == "game removed"


@patch("src.controllers.command_parser.nickname_game", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_game_command_nickname_game(mock_nickname_game) -> None:
    mock_nickname_game.return_value = "game nickname updated"
    result = await game_command(command_list=["game", "nickname", "game_name", "game_nickname"])
    assert result == "game nickname updated"


@patch("src.controllers.command_parser.unknown_command", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_game_command_unknown_command(mock_unknown_command) -> None:
    mock_unknown_command.return_value = "unknown command"
    result = await game_command(command_list=["game", "unknown", "game_name"])
    assert result == "unknown command"


@patch("src.models.db.Game.filter", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_nickname_game_updates_nickname_on_valid_command(mock_filter) -> None:
    mock_filter.return_value.update = AsyncMock()
    result = await nickname_game(command_list=["game", "nickname", "game_name", "game_nickname"])
    assert result == "game game_name nickname game_nickname"


@patch("src.models.db.Game.filter", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_nickname_game_returns_invalid_command_on_insufficient_arguments(mock_filter) -> None:
    result = await nickname_game(command_list=["game", "nickname", "game_name"])
    assert result == "command is invalid please check spelling or help command and try again"


@pytest.mark.asyncio
async def test_command_parser_wrapper():
    # Test various commands
    assert await command_parser_wrapper("help") == await help_command()
    assert await command_parser_wrapper("unknown") == "command not recognised"
    assert await command_parser_wrapper("") == "command not recognised"
    assert await command_parser_wrapper(" ") == "command not recognised"


@pytest.mark.asyncio
async def test_game_command():
    # Test add game
    with patch("src.controllers.command_parser.add_game", new_callable=AsyncMock) as mock_add_game:
        mock_add_game.return_value = "game test_game added"
        result = await game_command(["game", "add", "test_game"])
        assert result == "game test_game added"
        mock_add_game.assert_called_once_with(["game", "add", "test_game"])

    # Test remove game
    with patch("src.controllers.command_parser.remove_game", new_callable=AsyncMock) as mock_remove_game:
        mock_remove_game.return_value = "game test_game removed"
        result = await game_command(["game", "remove", "test_game"])
        assert result == "game test_game removed"
        mock_remove_game.assert_called_once_with(["game", "remove", "test_game"])

    # Test invalid subcommand
    result = await game_command(["game", "invalid", "test_game"])
    assert result == "command not recognised"


@pytest.mark.asyncio
async def test_player_command():
    with patch("src.controllers.command_parser.Game.filter") as mock_game_filter:
        mock_game = AsyncMock(spec=Game)
        mock_game_filter.return_value.first = AsyncMock(return_value=mock_game)

        with patch("src.controllers.command_parser.Player.filter") as mock_player_filter:
            mock_player = AsyncMock(spec=Player)
            mock_player_filter.return_value.first = AsyncMock(return_value=mock_player)

            result = await player_command(["player", "test_game", "nation", "player_name"])
            assert result == "Updated nation with player_name in test_game"

        # Test game not found
        mock_game_filter.return_value.first = AsyncMock(return_value=None)
        result = await player_command(["player", "nonexistent_game", "nation", "player_name"])
        assert result == "game nonexistent_game not found"


@pytest.mark.asyncio
async def test_set_game_status():
    with patch("src.controllers.command_parser.Game.filter") as mock_game_filter:
        mock_game = AsyncMock(spec=Game)
        mock_game_filter.return_value.first = AsyncMock(return_value=mock_game)

        result = await set_game_status(["game", "status", "test_game", "active"])
        assert result == "Game test_game status set to active"

        result = await set_game_status(["game", "status", "test_game", "inactive"])
        assert result == "Game test_game status set to inactive"

        result = await set_game_status(["game", "status", "test_game", "invalid"])
        assert result == "Invalid status. Use 'active' or 'inactive'."

        mock_game_filter.return_value.first = AsyncMock(return_value=None)
        result = await set_game_status(["game", "status", "nonexistent_game", "active"])
        assert result == "Game nonexistent_game not found"


@pytest.mark.asyncio
async def test_list_games():
    with patch("src.controllers.command_parser.Game") as mock_game:
        # Create mock games
        mock_game1 = MagicMock(spec=Game)
        mock_game1.name = "game1"
        mock_game1.nickname = "nick1"
        mock_game1.primary_game = True
        mock_game1.active = True

        mock_game2 = MagicMock(spec=Game)
        mock_game2.name = "game2"
        mock_game2.nickname = None
        mock_game2.primary_game = False
        mock_game2.active = True

        # Set up the mock filter method
        mock_filter = AsyncMock()
        mock_filter.return_value = [mock_game1, mock_game2]
        mock_game.filter = mock_filter

        result = await list_games()
        assert "game1 (Nickname: nick1) [PRIMARY] - Active" in result
        assert "game2 - Active" in result

        # Test no games
        mock_filter.return_value = []
        result = await list_games()
        assert result == "No games found."


@pytest.mark.asyncio
async def test_set_primary():
    with patch("src.controllers.command_parser.Game.filter") as mock_game_filter:
        mock_game = AsyncMock(spec=Game)
        mock_game.id = uuid4()
        mock_game_filter.return_value.first = AsyncMock(return_value=mock_game)
        mock_game_filter.return_value.update = AsyncMock()

        result = await set_primary(["game", "primary", "test_game"])
        assert result == "Game test_game has been set as the primary game"

        mock_game_filter.return_value.first = AsyncMock(return_value=None)
        result = await set_primary(["game", "primary", "nonexistent_game"])
        assert result == "Game nonexistent_game not found or not active"

        result = await set_primary(["game", "primary"])
        assert result == "command is invalid please check spelling or help command and try again"


@pytest.mark.asyncio
async def test_add_game():
    with patch("src.controllers.command_parser.Game.filter") as mock_game_filter, patch(
        "src.controllers.command_parser.get_lobby_details"
    ) as mock_get_lobby_details, patch("src.controllers.command_parser.Game.create") as mock_game_create, patch(
        "src.controllers.command_parser.Player.create"
    ) as mock_player_create:
        # Test case: Adding a new game
        mock_game_filter.return_value.first = AsyncMock(return_value=None)
        mock_get_lobby_details.return_value = ["1", "1 day left", [{"name": "Player1", "turn_status": "Turn played"}]]

        mock_game = AsyncMock(spec=Game)
        mock_game.id = uuid4()
        mock_game.players = AsyncMock()
        mock_game.players.add = AsyncMock()
        mock_game_create.return_value = mock_game

        mock_player = AsyncMock(spec=Player)
        mock_player_create.return_value = mock_player

        result = await add_game(["game", "add", "test_game"])
        assert result == "game test_game added"

        # Test case: Attempting to add an existing game
        mock_game_filter.return_value.first = AsyncMock(return_value=AsyncMock(spec=Game))
        result = await add_game(["game", "add", "existing_game"])
        assert result == "game existing_game already exists"

        # Test case: Error fetching game details
        mock_game_filter.return_value.first = AsyncMock(return_value=None)  # Reset to simulate new game
        mock_get_lobby_details.side_effect = ValueError("Test error")
        result = await add_game(["game", "add", "error_game"])
        assert result == "Failed to fetch game details for error_game"

        # Test case: Invalid game details format
        mock_get_lobby_details.side_effect = None
        mock_get_lobby_details.return_value = ["1", "1 day left"]  # Invalid format
        result = await add_game(["game", "add", "invalid_game"])
        assert result == "Unexpected game details format for invalid_game"


@pytest.mark.asyncio
async def test_update_player():
    mock_game = AsyncMock(spec=Game)
    mock_player = AsyncMock(spec=Player)

    with patch("src.controllers.command_parser.Player.filter") as mock_player_filter:
        # Test case: Successful update
        mock_player_filter.return_value.first = AsyncMock(return_value=mock_player)
        result = await update_player(mock_game, "nation1", "player1")
        assert result == PlayerCommandResult.PLAYER_UPDATED

        # Test case: Player not found
        mock_player_filter.return_value.first = AsyncMock(return_value=None)
        result = await update_player(mock_game, "nonexistent_nation", "player1")
        assert result == PlayerCommandResult.PLAYER_NOT_FOUND

        # Test case: Database error
        mock_player_filter.side_effect = DBConnectionError("Test database error")
        result = await update_player(mock_game, "nation1", "player1")
        assert result == PlayerCommandResult.DATABASE_ERROR

        # Reset side_effect after testing the error case
        mock_player_filter.side_effect = None


@pytest.mark.asyncio
async def test_handle_check_command():
    with patch("src.controllers.command_parser.get_lobby_details") as mock_get_lobby_details:
        mock_get_lobby_details.return_value = "Mocked lobby details"
        result = await handle_check_command(["check", "test_game"])
        assert result == "Mocked lobby details"

        mock_get_lobby_details.side_effect = ValueError("Test error")
        result = await handle_check_command(["check", "error_game"])
        assert result == "Test error"

        result = await handle_check_command(["check"])
        assert result == "command is invalid please check spelling or help command and try again"


@pytest.mark.asyncio
async def test_handle_turn_command():
    with patch("src.controllers.command_parser.get_lobby_details") as mock_get_lobby_details:
        mock_get_lobby_details.return_value = "Mocked turn status"
        result = await handle_turn_command()
        assert result == "Mocked turn status"

        mock_get_lobby_details.side_effect = ValueError("Test error")
        result = await handle_turn_command()
        assert result == "Test error"


@pytest.mark.asyncio
async def test_help_command_wrapper():
    result = await help_command_wrapper("game")
    assert result.startswith("Game command help:")
    assert "Game command usage:" in result

    result = await help_command_wrapper("player")
    assert result.startswith("Player command help:")
    assert "Player command usage:" in result

    result = await help_command_wrapper("nonexistent_command")
    assert result == "No specific help available for 'nonexistent_command'. Please use `/dom help` for general help."
