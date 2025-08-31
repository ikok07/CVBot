import os

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMADB_API_KEY"),
    database=os.getenv("VECTOR_STORE_DATABASE")
)

embedding_function = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("VECTOR_STORE_EMBEDDING_MODEL"),
    dimensions=int(os.getenv("VECTOR_STORE_DIMENSIONS"))
)

chroma_client.create_collection(os.getenv("VECTOR_STORE_COLLECTION"), embedding_function=embedding_function)