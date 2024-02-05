from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "game" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT NOT NULL,
    "primary_game" INT NOT NULL  DEFAULT 0,
    "nickname" TEXT NOT NULL,
    "active" INT NOT NULL  DEFAULT 1,
    "turn" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "player" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "nation" TEXT NOT NULL,
    "short_name" TEXT NOT NULL,
    "player_name" TEXT,
    "turn_status" TEXT NOT NULL,
    "game_id" CHAR(36) NOT NULL REFERENCES "game" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "game_player" (
    "game_id" CHAR(36) NOT NULL REFERENCES "game" ("id") ON DELETE CASCADE,
    "player_id" CHAR(36) NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
