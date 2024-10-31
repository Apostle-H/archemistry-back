from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "match_slot" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "pos_x" INT NOT NULL  DEFAULT 0,
    "pos_y" INT NOT NULL  DEFAULT 0,
    "user_fk_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_match_slot_user_fk_ea265e" ON "match_slot" ("user_fk_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "match_slot";"""
