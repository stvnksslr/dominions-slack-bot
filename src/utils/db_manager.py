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
    # pin the timezone: auto_now writes ORM-side timestamps, QuerySet.update() leaves them to MySQL
    "use_tz": True,
    "timezone": "UTC",
}


async def init() -> None:
    logger.info("connecting to db.....")
    # one config for both aerich and the runtime, so they can't drift apart
    await Tortoise.init(config=TORTOISE_ORM)
