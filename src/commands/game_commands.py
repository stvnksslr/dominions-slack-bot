from json import dumps
from typing import TYPE_CHECKING

from tortoise.transactions import in_transaction

from src.controllers.formatting import create_error_block, create_info_block, create_success_block
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
            return dumps(
                create_error_block(f"Game '{game_name}' already exists", "Use `/dom game list` to see all games")
            )

        try:
            game_details: LobbyDetails | None = await fetch_lobby_details_from_web(game_name=game_name)
            if game_details is None:
                return dumps(
                    create_error_block(
                        f"Failed to fetch game details for '{game_name}'",
                        "Check that the game name is correct and exists on the Dominions server",
                    )
                )

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

            return dumps(
                create_success_block(
                    "Game Added Successfully",
                    f"• Game: *{game_name}*\n"
                    f"• Players: {len(game_details.player_status)} nations tracked\n"
                    f"• Turn: {game_details.turn}\n"
                    f"• Next update: ~15 minutes",
                )
            )
        except Exception as e:
            return dumps(create_error_block(f"Error adding game: {e!s}"))


class RemoveGameCommand(Command):
    async def execute(self, game_name: str) -> str:
        game = await Game.filter(name=game_name, active=True).first()
        if not game:
            return dumps(
                create_error_block(f"Game '{game_name}' not found", "Use `/dom game list` to see active games")
            )

        await Game.filter(name=game_name).update(active=False)
        return dumps(
            create_success_block("Game Removed", f"*{game_name}* has been deactivated and will no longer be tracked")
        )


class NicknameGameCommand(Command):
    async def execute(self, game_name: str, nickname: str) -> str:
        game = await Game.filter(name=game_name, active=True).first()
        if not game:
            return dumps(
                create_error_block(f"Game '{game_name}' not found", "Use `/dom game list` to see active games")
            )

        await Game.filter(name=game_name).update(nickname=nickname)
        return dumps(create_success_block("Nickname Set", f"*{game_name}* will now display as *{nickname}*"))


class ListGamesCommand(Command):
    async def execute(self) -> str:
        all_games: list[Game] = await Game.filter(active=True)
        if not all_games:
            return dumps(
                create_info_block("No Active Games", "Use `/dom game add [game_name]` to start tracking a game")
            )

        blocks = [{"type": "header", "text": {"type": "plain_text", "text": "Active Games"}}, {"type": "divider"}]

        for game in all_games:
            display_name = game.nickname or game.name
            primary_badge = " :star:" if game.primary_game else ""
            turn_info = f"Turn {game.turn}" if game.turn else "Turn: Unknown"
            time_info = game.time_left if game.time_left else "Time remaining: Unknown"

            game_text = f"*{display_name}*{primary_badge}\n• Game ID: `{game.name}`\n• {turn_info}\n• {time_info}"

            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": game_text}})

        blocks.append({"type": "divider"})
        blocks.append(
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Total: {len(all_games)} game(s) | :star: = Primary game"}],
            }
        )

        return dumps(blocks)


class SetPrimaryGameCommand(Command):
    async def execute(self, game_name: str) -> str:
        existing_game = await Game.filter(name=game_name, active=True).first()
        if not existing_game:
            return dumps(
                create_error_block(
                    f"Game '{game_name}' not found or inactive", "Use `/dom game list` to see active games"
                )
            )

        # Use transaction to ensure atomic update
        async with in_transaction():
            # Unset all other primary games first
            await Game.all().update(primary_game=False)
            # Set this game as primary
            await Game.filter(id=existing_game.id).update(primary_game=True)

        return dumps(
            create_success_block(
                "Primary Game Set", f"*{game_name}* is now the primary game\n• Use `/dom turn` to see status quickly"
            )
        )


class SetGameStatusCommand(Command):
    async def execute(self, game_name: str, status: str) -> str:
        if status not in ["active", "inactive"]:
            return dumps(
                create_error_block(
                    "Invalid status value",
                    "Status must be either `active` or `inactive`\n"
                    "• Usage: `/dom game status [game_name] [active|inactive]`",
                )
            )

        game = await Game.filter(name=game_name).first()
        if not game:
            return dumps(create_error_block(f"Game '{game_name}' not found", "Use `/dom game list` to see all games"))

        game.active = status == "active"
        await game.save()

        status_emoji = ":white_check_mark:" if status == "active" else ":no_entry_sign:"
        return dumps(create_success_block("Game Status Updated", f"{status_emoji} *{game_name}* is now *{status}*"))
