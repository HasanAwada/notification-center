from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create an async engine
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Create a session factory
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
