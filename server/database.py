from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app_config import settings


# Асинхронный URL: добавляем +asyncpg
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# создаём асинхронный движок
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # включить SQL-логирование при желании
)

# фабрика асинхронных сессий
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# базовый класс для моделей
Base = declarative_base()
Base.metadata.drop_all(bind=engine)

# Создайте все таблицы заново
Base.metadata.create_all(bind=engine)
