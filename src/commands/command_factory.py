from typing import ClassVar

from .base import Command
from .check_commands import CheckGameStatusCommand
from .game_commands import (
    AddGameCommand,
    ListGamesCommand,
    NicknameGameCommand,
    RemoveGameCommand,
    SetGameStatusCommand,
    SetPrimaryGameCommand,
)
from .help_commands import HelpCommand
from .player_commands import UpdatePlayerCommand
from .turn_commands import TurnStatusCommand


class CommandFactory:
    _commands: ClassVar[dict[str, type[Command]]] = {
        "game add": AddGameCommand,
        "game remove": RemoveGameCommand,
        "game nickname": NicknameGameCommand,
        "game list": ListGamesCommand,
        "game primary": SetPrimaryGameCommand,
        "game status": SetGameStatusCommand,
        "player": UpdatePlayerCommand,
        "check": CheckGameStatusCommand,
        "turn": TurnStatusCommand,
        "help": HelpCommand,
    }

    @classmethod
    def get_command(cls, command_name: str) -> Command:
        command_class = cls._commands.get(command_name)
        if command_class:
            return command_class()
        raise ValueError(f"Unknown command: {command_name}")
