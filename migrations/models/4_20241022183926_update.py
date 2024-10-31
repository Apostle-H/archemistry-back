from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user_game_state" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "score" BIGINT NOT NULL  DEFAULT 0
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "user_game_state";"""
