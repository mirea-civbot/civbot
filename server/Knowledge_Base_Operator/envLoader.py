import os
from dotenv import load_dotenv


class EnvLoader:
    def __init__(self):
        self.load_env_variables()

    def load_env_variables(self):
        load_dotenv()
        self.PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        self.LLAMA_API_KEY = os.getenv("LLAMA_API")
        self.PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
