-- upgrade --
CREATE TABLE IF NOT EXISTS "game" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(120) NOT NULL,
    "port" SMALLINT NOT NULL
);
-- downgrade --
DROP TABLE IF EXISTS "game";
