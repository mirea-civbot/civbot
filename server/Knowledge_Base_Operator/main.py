from pinecone import  Pinecone
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from envLoader import EnvLoader

env_loader = EnvLoader()

pinecone_client = Pinecone(
    api_key=env_loader.PINECONE_API_KEY,
)

pinecone_index = pinecone_client.Index("civbotvect")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

storage_context = StorageContext.from_defaults(
  vector_store=vector_store
)

documents = SimpleDirectoryReader("data_civ6_ru").load_data()
