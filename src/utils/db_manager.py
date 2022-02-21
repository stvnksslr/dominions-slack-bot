from tortoise import Tortoise

from src.utils.constants import DATABASE_URI

MIGRATION_CONFIG = {
    "connections": {"default": DATABASE_URI},
    "apps": {
        "models": {
            "models": ["src.models.database", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    await Tortoise.init(
        db_url=DATABASE_URI, modules={"models": ["src.models.database"]}
    )
