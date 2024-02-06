from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `game` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` LONGTEXT NOT NULL,
    `primary_game` BOOL NOT NULL  DEFAULT 0,
    `nickname` LONGTEXT NOT NULL,
    `active` BOOL NOT NULL  DEFAULT 1,
    `turn` INT NOT NULL  DEFAULT 0,
    `time_left` LONGTEXT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `player` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `nation` LONGTEXT NOT NULL,
    `short_name` LONGTEXT NOT NULL,
    `player_name` LONGTEXT,
    `turn_status` LONGTEXT NOT NULL,
    `game_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_player_game_e1f48209` FOREIGN KEY (`game_id`) REFERENCES `game` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `game_player` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `game_id` CHAR(36) NOT NULL,
    `player_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`game_id`) REFERENCES `game` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`player_id`) REFERENCES `player` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
