from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    # game_player was created by the initial migration but never written to or read from;
    # the Game <-> Player link has always been the player.game_id foreign key.
    return """
        DROP TABLE IF EXISTS `game_player`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `game_player` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `game_id` CHAR(36) NOT NULL,
    `player_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`game_id`) REFERENCES `game` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`player_id`) REFERENCES `player` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""
