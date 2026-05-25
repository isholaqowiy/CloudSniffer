import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

engine = create_async_engine(
    "sqlite+aiosqlite:///./database/detector.db",
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"timeout": 30, "check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db():
    from database.models import Base
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database engine initialized and tables verified safely.")
    except Exception as e:
        logger.critical(f"Failed to bootstrap physical database schemas: {e}")
        raise e
