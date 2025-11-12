"""Initialize database schema for tests (runs in CI).

Creates all tables defined in SQLAlchemy models using the async engine.
"""
import asyncio

from src.db.session import get_engine
from src.db.base import Base
import src.models  # noqa: F401 ensure model registration


async def main():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
