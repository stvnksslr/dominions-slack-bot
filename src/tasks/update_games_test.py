from unittest.mock import AsyncMock, patch

import pytest
from tortoise import Tortoise

from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game, Player
from src.tasks.update_games import update_games_wrapper

NATION = "Ermor, Ashen Empire"


@pytest.fixture
async def _db():  # noqa: ANN202
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["src.models.db"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


def _details(turn: str, time_left: str = "1 day left", nation: str = NATION) -> LobbyDetails:
    return LobbyDetails(
        server_info=f"game, turn {turn} ({time_left})",
        player_status=[PlayerStatus(name=nation, turn_status="Turn played")],
        turn=turn,
        time_left=time_left,
    )


@pytest.mark.usefixtures("_db")
async def test_notification_names_the_game_that_advanced_not_the_primary() -> None:
    """Regression: send_turn_update used to always report the primary game."""
    primary = await Game.create(name="PrimaryGame", turn=5, primary_game=True)
    other = await Game.create(name="OtherGame", turn=1)
    await Player.create(nation=NATION, short_name="Ermor", turn_status="Turn unfinished", game=other)

    async def fake_fetch(game_name: str) -> LobbyDetails:
        return _details("5") if game_name == "PrimaryGame" else _details("2")

    posted = AsyncMock()
    with (
        patch("src.tasks.update_games.fetch_lobby_details_from_web", new=fake_fetch),
        patch("src.tasks.update_games.client.chat_postMessage", new=posted),
    ):
        await update_games_wrapper()

    posted.assert_awaited_once()
    assert "OtherGame" in str(posted.await_args)
    assert "PrimaryGame" not in str(posted.await_args)

    assert (await Game.get(id=other.id)).turn == 2
    assert (await Game.get(id=primary.id)).turn == 5


@pytest.mark.usefixtures("_db")
async def test_same_turn_does_not_notify() -> None:
    game = await Game.create(name="Steady", turn=4)
    await Player.create(nation=NATION, short_name="Ermor", turn_status="Turn unfinished", game=game)

    posted = AsyncMock()
    with (
        patch("src.tasks.update_games.fetch_lobby_details_from_web", new=AsyncMock(return_value=_details("4"))),
        patch("src.tasks.update_games.client.chat_postMessage", new=posted),
    ):
        await update_games_wrapper()

    posted.assert_not_awaited()
    player = await Player.filter(game=game).first()
    assert player is not None
    assert player.turn_status == "Turn played", "player statuses still update on an unchanged turn"


@pytest.mark.usefixtures("_db")
async def test_finished_game_is_deactivated_and_unset_as_primary() -> None:
    game = await Game.create(name="Done", turn=9, primary_game=True)

    with (
        patch(
            "src.tasks.update_games.fetch_lobby_details_from_web",
            new=AsyncMock(return_value=_details("9", time_left="finished")),
        ),
        patch("src.tasks.update_games.client.chat_postMessage", new=AsyncMock()),
    ):
        await update_games_wrapper()

    refreshed = await Game.get(id=game.id)
    assert refreshed.active is False
    assert refreshed.primary_game is False


@pytest.mark.usefixtures("_db")
async def test_unparseable_turn_does_not_abort_the_cycle() -> None:
    """int('e,') used to raise every cycle forever, silently."""
    game = await Game.create(name="Nocturne", turn=3)
    garbage = LobbyDetails(server_info="junk", player_status=[], turn="e,", time_left=None)

    with (
        patch("src.tasks.update_games.fetch_lobby_details_from_web", new=AsyncMock(return_value=garbage)),
        patch("src.tasks.update_games.client.chat_postMessage", new=AsyncMock()),
    ):
        await update_games_wrapper()  # must not raise

    assert (await Game.get(id=game.id)).turn == 3


@pytest.mark.usefixtures("_db")
async def test_unmatched_nation_is_skipped_rather_than_crashing() -> None:
    game = await Game.create(name="Drifted", turn=1)
    await Player.create(nation="Ermor, Ashen Empre", short_name="Ermor", turn_status="Turn unfinished", game=game)

    with (
        patch("src.tasks.update_games.fetch_lobby_details_from_web", new=AsyncMock(return_value=_details("1"))),
        patch("src.tasks.update_games.client.chat_postMessage", new=AsyncMock()),
    ):
        await update_games_wrapper()

    player = await Player.filter(game=game).first()
    assert player is not None
    assert player.turn_status == "Turn unfinished"
