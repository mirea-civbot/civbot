from pydantic_settings import BaseSettings
import os
from pydantic import Extra
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://postgres:root@localhost:5432/CivBot'
    SECRET_KEY: str = "your-256-bit-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CHAT_MODEL_NAME: str = "tinkoff-ai/ruDialoGpt3-medium"
    

    class Config:
        extra = Extra.ignore
        env_file = ".env"


settings = Settings()
