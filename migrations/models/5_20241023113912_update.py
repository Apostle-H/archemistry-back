from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_state" ADD "max_energy" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "user_game_state" ADD "energy" INT NOT NULL  DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_state" DROP COLUMN "max_energy";
        ALTER TABLE "user_game_state" DROP COLUMN "energy";"""
