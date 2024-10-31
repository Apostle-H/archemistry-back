from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_state" ADD "match_combo_streak" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "user_game_state" ADD "last_move_match_combo_streak" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "user_game_state" ADD "in_clearing_match_combo_streak" INT NOT NULL  DEFAULT 0;
        CREATE TABLE IF NOT EXISTS "user_game_stats" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "energy_spend" BIGINT NOT NULL  DEFAULT 0,
    "matches_count" BIGINT NOT NULL  DEFAULT 0,
    "four_plus_matches_count" BIGINT NOT NULL  DEFAULT 0,
    "two_plus_matches_combo_count" BIGINT NOT NULL  DEFAULT 0,
    "max_match_combo_streak" BIGINT NOT NULL  DEFAULT 0
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_state" DROP COLUMN "match_combo_streak";
        ALTER TABLE "user_game_state" DROP COLUMN "last_move_match_combo_streak";
        ALTER TABLE "user_game_state" DROP COLUMN "in_clearing_match_combo_streak";
        DROP TABLE IF EXISTS "user_game_stats";"""
