from src.models.database.game import Game


async def create_game(name: str, port: int) -> Game:
    """
    creates a new game given the following parameters

    :param name:
    :param port:
    :return:
    """
    try:
        return await Game.create(name=name, port=port, active=True)
    except Exception:
        raise


async def find_active_games():
    """
    returns a list of all active games

    :return:
    """
    return Game.filter(active=True)


async def find_game(name: str, port: int) -> Game:
    """
    finds an existing game based on either its name or its port

    :param name:
    :param port:
    :return:
    """
    try:
        if name:
            return await Game.filter(name=name).first()
        else:
            return await Game.filter(port=port).first()
    except Exception:
        raise


async def update_game(name: str, port: int, active: bool):
    """
    Updates an existing game

    :param name:
    :param port:
    :param active:
    :return:
    """
    try:
        return await Game.filter(name=name, port=port).update(active=active)
    except Exception:
        raise
