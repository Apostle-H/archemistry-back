from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "task" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "type" SMALLINT NOT NULL UNIQUE DEFAULT 0,
    "description" VARCHAR(64) NOT NULL,
    "target_value" INT NOT NULL  DEFAULT 0,
    "target_url" VARCHAR(128) NOT NULL,
    "icon_url" VARCHAR(128) NOT NULL,
    "reward_type" SMALLINT NOT NULL  DEFAULT 0,
    "reward" INT NOT NULL  DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_task_type_8d5f35" ON "task" ("type");
        CREATE TABLE IF NOT EXISTS "user_task" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "shift_value" INT NOT NULL  DEFAULT 0,
    "progress_value" INT NOT NULL  DEFAULT 0,
    "task_fk_id" UUID NOT NULL REFERENCES "task" ("uuid") ON DELETE CASCADE,
    "user_fk_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_user_task_task_fk_f32759" ON "user_task" ("task_fk_id");
CREATE INDEX IF NOT EXISTS "idx_user_task_user_fk_04dec1" ON "user_task" ("user_fk_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "task";
        DROP TABLE IF EXISTS "user_task";"""
