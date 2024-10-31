from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task" ALTER COLUMN "target_tg_id" SET DEFAULT 'none';
        ALTER TABLE "task" ALTER COLUMN "target_value" SET DEFAULT 1;
        ALTER TABLE "task" ALTER COLUMN "target_url" SET DEFAULT 'none';
        ALTER TABLE "task" ALTER COLUMN "icon_url" SET DEFAULT 'none';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task" ALTER COLUMN "target_tg_id" DROP DEFAULT;
        ALTER TABLE "task" ALTER COLUMN "target_value" SET DEFAULT 0;
        ALTER TABLE "task" ALTER COLUMN "target_url" DROP DEFAULT;
        ALTER TABLE "task" ALTER COLUMN "icon_url" DROP DEFAULT;"""
