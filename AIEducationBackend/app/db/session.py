# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the async engine
# pool_pre_ping=True helps handle connections that might have timed out
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)  # Set echo=True for debugging SQL

# Create a configured "Session" class
# expire_on_commit=False prevents attributes from being expired after commit,
# useful when background tasks need the committed object.
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency to get DB session (to be used in app/api/deps.py)
async def get_async_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Commit changes if no exceptions occurred
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()

# Optional: Function to create tables (useful for initial setup or testing)
# You would typically use Alembic for migrations in production.
# from .base_class import Base # Assuming you have a Base declarative base
# async def init_db():
#     async with engine.begin() as conn:
#         # await conn.run_sync(Base.metadata.drop_all) # Uncomment to drop tables first
#         await conn.run_sync(Base.metadata.create_all)
