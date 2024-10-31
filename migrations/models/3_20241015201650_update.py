from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "match_element" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "title" VARCHAR(20) NOT NULL
);
        ALTER TABLE "match_slot" ADD "match_element_fk_id" UUID NOT NULL;
        CREATE INDEX "idx_match_slot_match_e_adb027" ON "match_slot" ("match_element_fk_id");
        ALTER TABLE "match_slot" ADD CONSTRAINT "fk_match_sl_match_el_9b5b8efc" FOREIGN KEY ("match_element_fk_id") REFERENCES "match_element" ("uuid") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "match_slot" DROP CONSTRAINT "fk_match_sl_match_el_9b5b8efc";
        DROP INDEX "idx_match_slot_match_e_adb027";
        ALTER TABLE "match_slot" DROP COLUMN "match_element_fk_id";
        DROP TABLE IF EXISTS "match_element";"""
