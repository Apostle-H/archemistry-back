from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "shop_energy_item" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "type" INT NOT NULL UNIQUE DEFAULT 0,
    "amount" INT NOT NULL  DEFAULT 0,
    "cost" INT NOT NULL  DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_shop_energy_type_c3bea3" ON "shop_energy_item" ("type");
        ALTER TABLE "user_game_stats" ADD "referrals_count" INT NOT NULL  DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_game_stats" DROP COLUMN "referrals_count";
        DROP TABLE IF EXISTS "shop_energy_item";"""
