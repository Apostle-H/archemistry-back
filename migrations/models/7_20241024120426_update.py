from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_user_game_s_score_cdc8b5" ON "user_game_state" ("score" DESC);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_user_game_s_score_cdc8b5";"""
