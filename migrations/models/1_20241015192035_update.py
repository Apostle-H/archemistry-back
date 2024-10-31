from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "tg_id" BIGINT NOT NULL UNIQUE,
    "is_premium" BOOL,
    "username" VARCHAR(128)
);
CREATE INDEX IF NOT EXISTS "idx_user_tg_id_ba6243" ON "user" ("tg_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "user";"""
