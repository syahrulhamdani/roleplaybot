import os
from contextlib import asynccontextmanager

from common.models import Base
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

load_dotenv()


class DatabaseSessionFactory:
    _instance: "DatabaseSessionFactory | None" = None
    _engine: AsyncEngine | None = None
    _initialized: bool = False

    def __new__(cls) -> "DatabaseSessionFactory":
        if cls._instance is None:
            cls._instance = super(DatabaseSessionFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sesame.db")

        # Basic connection pool configuration
        self._engine = create_async_engine(
            db_url,
            pool_size=5,  # Default pool size
            max_overflow=10,  # Max overflow connections
            pool_timeout=30,  # 30 seconds timeout
            pool_recycle=300,  # Recycle connections after 5 minutes
            pool_pre_ping=True,  # Enable connection health checks
            echo=bool(int(os.getenv("DATABASE_ECHO_OUTPUT", "0"))),
        )
        self.session_maker = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            autocommit=False,  # Explicitly disable autocommit
            autoflush=False,  # Disable autoflush
        )
        self._initialized = True

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        return self._engine

    async def initialize_schema(self):
        """Initialize the database schema from SQLAlchemy models"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.debug("SQLite schema applied")

    @asynccontextmanager
    async def __call__(self):
        """Create a database session with automatic transaction management.

        The session will automatically handle transactions. Use it like:
        async with db() as session:
            # Your database operations here
            pass  # Session will be committed if no exceptions occur
        """
        session = self.session_maker()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Create a default session factory for convenience
default_session_factory = DatabaseSessionFactory()


async def init_db():
    logger.info("Initializing database...")
    async with default_session_factory() as db:
        await default_session_factory.initialize_schema()
    logger.info("Database initialized successfully")
