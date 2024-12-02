from typing import TYPE_CHECKING, Literal

from src.controllers.lobby_details import fetch_lobby_details_from_web
from src.models.db import Game
from src.models.db.players import Player

from .base import Command

if TYPE_CHECKING:
    from src.models.app.lobby_details import LobbyDetails


class AddGameCommand(Command):
    async def execute(self, game_name: str) -> str:
        existing_game: Game | None = await Game.filter(name=game_name, active=True).first()
        if existing_game:
            return f"game {game_name} already exists"

        try:
            game_details: LobbyDetails | None = await fetch_lobby_details_from_web(game_name=game_name)
            if game_details is None:
                return f"Failed to fetch game details for {game_name}"

            # Create the game first
            current_game = await Game.create(name=game_name, turn=game_details.turn, time_left=game_details.time_left)

            # Create players with the game reference
            for player in game_details.player_status:
                await Player.create(
                    nation=player.name.strip(),
                    short_name=player.name.split(",")[0].strip(),
                    turn_status=player.turn_status,
                    game=current_game,  # Set the game reference directly
                )

            return f"game {game_name} added successfully with {len(game_details.player_status)} players"
        except Exception as e:
            return f"Error adding game: {e!s}"


class RemoveGameCommand(Command):
    async def execute(self, game_name: str) -> str:
        await Game.filter(name=game_name).update(active=False)
        return f"game {game_name} deleted"


class NicknameGameCommand(Command):
    async def execute(self, game_name: str, nickname: str) -> str:
        await Game.filter(name=game_name).update(nickname=nickname)
        return f"game {game_name} nickname {nickname}"


class ListGamesCommand(Command):
    async def execute(self) -> str:
        all_games: list[Game] = await Game.filter(active=True)
        if not all_games:
            return "No games found."

        game_list = "Games:\n"
        for game in all_games:
            nickname = f" (Nickname: {game.nickname})" if game.nickname else ""
            primary: Literal[" [PRIMARY]"] | Literal[""] = " [PRIMARY]" if game.primary_game else ""
            status: Literal["Active"] | Literal["Inactive"] = "Active" if game.active else "Inactive"
            game_list += f"- {game.name}{nickname}{primary} - {status}\n"

        return game_list


class SetPrimaryGameCommand(Command):
    async def execute(self, game_name: str) -> str:
        existing_game = await Game.filter(name=game_name, active=True).first()
        if not existing_game:
            return f"Game {game_name} not found or not active"

        await Game.filter(id=existing_game.id).update(primary_game=True)
        return f"Game {game_name} has been set as the primary game"


class SetGameStatusCommand(Command):
    async def execute(self, game_name: str, status: str) -> str:
        if status not in ["active", "inactive"]:
            return "Invalid status. Use 'active' or 'inactive'."

        game = await Game.filter(name=game_name).first()
        if not game:
            return f"Game {game_name} not found"

        game.active = status == "active"
        await game.save()
        return f"Game {game_name} status set to {status}"
