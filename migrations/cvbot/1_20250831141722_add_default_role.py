from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "profiles" ALTER COLUMN "role" SET DEFAULT 'user';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "profiles" ALTER COLUMN "role" DROP DEFAULT;"""
