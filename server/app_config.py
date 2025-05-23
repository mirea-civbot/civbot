from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://postgres:root@localhost:5432/CivBot'
    SECRET_KEY: str = "your-256-bit-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"

    class Config:
        env_file = ".env"


settings = Settings()
