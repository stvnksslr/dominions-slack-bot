from json import loads
from unittest.mock import AsyncMock, patch

import pytest
from tortoise import Tortoise

from src.commands.game_commands import AddGameCommand, RemoveGameCommand, SetPrimaryGameCommand
from src.models.app.lobby_details import LobbyDetails
from src.models.app.player_status import PlayerStatus
from src.models.db import Game, Player


@pytest.fixture
async def _db():  # noqa: ANN202
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["src.models.db"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


def _details(*nations: str) -> LobbyDetails:
    return LobbyDetails(
        server_info="g, turn 1 (1 day left)",
        player_status=[PlayerStatus(name=n, turn_status="Turn unfinished") for n in nations],
        turn="1",
        time_left="1 day left",
    )


def _patch_fetch(details: LobbyDetails | None):  # noqa: ANN202
    return patch("src.commands.game_commands.fetch_lobby_details_from_web", new=AsyncMock(return_value=details))


@pytest.mark.usefixtures("_db")
async def test_add_remove_add_reuses_the_row_instead_of_duplicating() -> None:
    """Remove is a soft delete — re-adding used to insert a second row with the same name."""
    with _patch_fetch(_details("Ermor, Ashen Empire")):
        await AddGameCommand().execute("MyGame")
    await RemoveGameCommand().execute("MyGame")
    with _patch_fetch(_details("Ermor, Ashen Empire", "Pangaea, Age of Revelry")):
        await AddGameCommand().execute("MyGame")

    assert await Game.filter(name="MyGame").count() == 1
    game = await Game.get(name="MyGame")
    assert game.active is True
    # roster is re-seeded from the fresh scrape, with no leftovers from the first add
    assert await Player.filter(game=game).count() == 2


@pytest.mark.usefixtures("_db")
async def test_adding_an_already_active_game_is_rejected() -> None:
    with _patch_fetch(_details("Ermor, Ashen Empire")):
        await AddGameCommand().execute("MyGame")
        result = await AddGameCommand().execute("MyGame")

    assert "already exists" in str(loads(result))
    assert await Game.filter(name="MyGame").count() == 1


@pytest.mark.usefixtures("_db")
async def test_failed_scrape_creates_nothing() -> None:
    with _patch_fetch(None):
        result = await AddGameCommand().execute("Ghost")

    assert "Failed to fetch" in str(loads(result))
    assert await Game.filter(name="Ghost").count() == 0


@pytest.mark.usefixtures("_db")
async def test_removing_a_game_clears_primary() -> None:
    """A removed game left as primary kept /dom turn serving a deactivated game."""
    with _patch_fetch(_details("Ermor, Ashen Empire")):
        await AddGameCommand().execute("MyGame")
    await SetPrimaryGameCommand().execute("MyGame")
    await RemoveGameCommand().execute("MyGame")

    game = await Game.get(name="MyGame")
    assert game.active is False
    assert game.primary_game is False


@pytest.mark.usefixtures("_db")
async def test_set_primary_leaves_exactly_one_primary() -> None:
    with _patch_fetch(_details("Ermor, Ashen Empire")):
        await AddGameCommand().execute("GameA")
        await AddGameCommand().execute("GameB")

    await SetPrimaryGameCommand().execute("GameA")
    await SetPrimaryGameCommand().execute("GameB")

    assert await Game.filter(primary_game=True).count() == 1
    assert (await Game.get(name="GameB")).primary_game is True
