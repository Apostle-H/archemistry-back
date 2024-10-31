from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "referral" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "referred_by_user_fk_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE,
    "referred_user_fk_id" UUID NOT NULL REFERENCES "user" ("uuid") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_referral_referre_7edc15" ON "referral" ("referred_by_user_fk_id");
CREATE INDEX IF NOT EXISTS "idx_referral_referre_47a932" ON "referral" ("referred_user_fk_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "referral";"""
