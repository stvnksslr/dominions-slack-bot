from loguru import logger
from tortoise import Tortoise

from src.utils.constants import DB_URI

TORTOISE_ORM = {
    "connections": {"default": DB_URI},
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "src.models.db",
            ],
            "default_connection": "default",
        },
    },
}


async def init() -> None:
    logger.info("connecting to db.....")
    await Tortoise.init(db_url=DB_URI, modules={"models": ["src.models.db"]})
