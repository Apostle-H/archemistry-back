from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_state" ADD "soft_currency" BIGINT NOT NULL  DEFAULT 0;
        ALTER TABLE "user_game_state" ADD "hard_currency" BIGINT NOT NULL  DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_state" DROP COLUMN "soft_currency";
        ALTER TABLE "user_game_state" DROP COLUMN "hard_currency";"""
