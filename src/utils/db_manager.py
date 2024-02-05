import tortoise
from loguru import logger
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {"default": "sqlite://dsb.sqlite3?journal_mode=OFF"},
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


async def init():
    logger.info("connecting to db.....")
    await Tortoise.init(db_url="sqlite://dsb.sqlite3?journal_mode=OFF", modules={"models": ["src.models.db"]})
