import os
from typing import List
from dotenv import load_dotenv

load_dotenv()
class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL_NAME: str = "gemini-2.0-flash-exp"
    
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    VECTOR_STORE_TYPE: str = "faiss"
    VECTOR_STORE_PATH: str = "./vector_store"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    MAX_UPLOAD_SIZE: int = 200
    SUPPORTED_FILE_TYPES: List[str] = [".pdf"]
    
    MAX_QUERY_LENGTH: int = 500
    MIN_QUERY_LENGTH: int = 3
    
    DEFAULT_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    EMBEDDING_BATCH_SIZE: int = 5
    MAX_PARALLEL_BATCHES: int = 3
    
    CHAT_HISTORY_LIMIT: int = 50
    UI_CHAT_HISTORY_DISPLAY: int = 10

settings = Settings()