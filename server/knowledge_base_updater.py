import os
from pinecone import Pinecone
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    Settings,
)
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "civbotvect"

def ingest_data():
    if not PINECONE_API_KEY:
        raise ValueError("API ключ для Pinecone должен быть установлен")
    print("Настройка модели эмбеддингов для русского языка...")

    Settings.embed_model = HuggingFaceEmbedding(model_name="cointegrated/rubert-tiny2")

    # Инициализируем Pinecone
    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pinecone.Index(INDEX_NAME)

    # Оборачиваем индекс в VectorStore от LlamaIndex
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Загружаем документы
    documents = SimpleDirectoryReader("data_civ6_ru").load_data()

    splitter = SemanticSplitterNodeParser(
        buffer_size=2,
        breakpoint_percentile_threshold=90,
        embed_model=Settings.embed_model,
    )

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True,
    )


ingest_data()
