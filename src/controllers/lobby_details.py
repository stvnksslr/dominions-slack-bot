import re
from typing import Any

import bs4
from aiohttp import ClientError, ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from loguru import logger

from src.controllers.formatting import (
    create_error_block,
    create_game_details_block,
    create_game_details_block_from_db,
    create_nations_block_from_db,
)
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game
from src.models.db.players import Player

REQUEST_TIMEOUT = ClientTimeout(total=15)

# requires whitespace + digits, so a game named "nocturne" or "saturnalia" can't match
TURN_PATTERN = re.compile(r"turn\s+(\d+)")


def format_url(game_name: str) -> str:
    return f"http://ulm.illwinter.com/dom6/server/{game_name}.html"


async def fetch_lobby_details_from_web(game_name: str) -> LobbyDetails | None:
    """Scrape a game's status page. Returns None on any failure — never raises."""
    formatted_url = format_url(game_name)
    try:
        async with ClientSession(timeout=REQUEST_TIMEOUT) as session, session.get(url=formatted_url) as response:
            html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        first_row = soup.find("tr")

        if not isinstance(first_row, bs4.Tag):
            logger.error(f"Failed to find table row in HTML content for game {game_name}")
            return None

        server_info = first_row.text.strip().lower()
        # page reads "<game name>, turn N (time left)" — take the last match, the game name comes first
        turn_matches = TURN_PATTERN.findall(server_info)
        if not turn_matches:
            logger.error(f"Failed to extract turn information for game {game_name}")
            return None

        turn = turn_matches[-1]

        time_left: str | None = None
        if "(" in server_info and ")" in server_info:
            # rsplit so a game named "Blitz (fast)" doesn't shadow the real timer
            time_left = server_info.rsplit("(", 1)[1].split(")")[0]

        player_status_list = []
        for row in soup.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) >= 2:
                player_status_list.append(
                    PlayerStatus(name=columns[0].text.strip(), turn_status=columns[1].text.strip()),
                )

        return LobbyDetails(
            server_info=server_info,
            player_status=player_status_list,
            turn=turn,
            time_left=time_left,
        )

    except (ClientError, TimeoutError) as e:
        logger.error(f"HTTP request failed for game {game_name}: {e}")
    except (IndexError, ValueError) as e:
        logger.error(f"Failed to extract required information from HTML for game {game_name}: {e}")

    return None


async def fetch_lobby_details_from_db(game_name: str) -> LobbyDetails | None:
    # newest row wins: names aren't unique, so a re-added game must not resolve to a stale row
    game = await Game.filter(name=game_name).order_by("-created_at").first()
    if game is None:
        logger.error(f"Game '{game_name}' not found in the database")
        return None

    player_list = await Player.filter(game=game)

    player_status_list = [
        PlayerStatus(name=player.short_name, turn_status=player.turn_status, nickname=player.player_name)
        for player in player_list
    ]

    logger.debug(f"retrieved status for: {len(player_status_list)} players")

    return LobbyDetails(
        server_info=f"{game.name} - Turn {game.turn}",
        player_status=player_status_list,
        turn=str(game.turn),
        time_left=game.time_left,
    )


def format_lobby_details(lobby_details: LobbyDetails, use_db: bool = False, game_name: str | None = None) -> list[dict]:
    if use_db:
        game_details_block = create_game_details_block_from_db(lobby_details)
    else:
        game_details_block = create_game_details_block(lobby_details, game_name)

    nations_block = create_nations_block_from_db(lobby_details.player_status)

    logger.debug("format_lobby_details run")
    return [
        *game_details_block,
        *nations_block,
    ]


async def get_lobby_details(game_name: str, use_db: bool = False) -> list[Any]:
    """Always returns a non-empty block list — Slack rejects a message with zero blocks."""
    try:
        if use_db:
            fetch_function = fetch_lobby_details_from_db
            logger.debug("Using database to fetch lobby details")
        else:
            fetch_function = fetch_lobby_details_from_web
            logger.debug("Using web scraping to fetch lobby details")

        lobby_details = await fetch_function(game_name)

        if lobby_details is None:
            logger.error(f"No lobby details found for game '{game_name}'")
            return create_error_block(
                f"No details found for game '{game_name}'",
                "Check the name with `/dom game list`, or confirm the game exists on the Dominions server",
            )

        return format_lobby_details(lobby_details, use_db, game_name)

    except Exception:
        logger.exception(f"Error fetching lobby details for game '{game_name}'")
        return create_error_block(
            f"Could not load status for '{game_name}'",
            "The Dominions server may be unreachable. Try again in a moment.",
        )


async def turn_command_wrapper() -> list[Any]:
    current_game = await Game.filter(primary_game=True).first()
    if current_game is None:
        logger.error("No primary game found")
        return create_error_block("No primary game set", "Set one with `/dom game primary [game_name]`")
    return await get_lobby_details(current_game.name, use_db=True)
