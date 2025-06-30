from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv


load_dotenv()
class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://postgres:root@localhost:5432/CivBot'
    
    # GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    # CIV6_FANDOM_URL: str = os.getenv("CIV6_FANDOM_URL", "https://civilization.fandom.com/ru/wiki/Civilization_VI")
    # GEMINI_GENERATION_MODEL: str = os.getenv("GEMINI_GENERATION_MODEL", "gemini-1.5-flash-latest")
    # GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

    # PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    # PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT") 
    # PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME")
    # PINECONE_EMBEDDING_DIMENSION: int = int(os.getenv("PINECONE_EMBEDDING_DIMENSION", 768))

    SECRET_KEY: str = "your-256-bit-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CHAT_MODEL_NAME: str = "tinkoff-ai/ruDialoGpt3-medium"


    class Config:
        env_file = ".env"


settings = Settings()
