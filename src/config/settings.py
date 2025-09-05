import os
from dotenv import load_dotenv
from typing import Optional
import streamlit as st

load_dotenv()

class Settings:
    """Configuration settings for the application"""
    
    def __init__(self):
        self.GOOGLE_API_KEY: str = self._get_env_or_secrets("GOOGLE_API_KEY")
        self.MODEL_NAME: str = self._get_env_or_secrets("MODEL_NAME", "gemini-2.0-flash-exp")
        self.EMBEDDING_MODEL: str = self._get_env_or_secrets("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        self.VECTOR_STORE_TYPE: str = self._get_env_or_secrets("VECTOR_STORE_TYPE", "faiss")
        self.CHUNK_SIZE: int = int(self._get_env_or_secrets("CHUNK_SIZE", "1000"))
        self.CHUNK_OVERLAP: int = int(self._get_env_or_secrets("CHUNK_OVERLAP", "200"))
        
        self.MAX_UPLOAD_SIZE: int = int(self._get_env_or_secrets("MAX_UPLOAD_SIZE", "200"))
        self.DEBUG_MODE: bool = self._get_env_or_secrets("DEBUG_MODE", "False").lower() == "true"
        
        self.VECTOR_STORE_PATH: str = "./data/vector_store"
        self.TEMP_UPLOAD_PATH: str = "./data/temp_uploads"
        
        self._create_directories()
    
    def _get_env_or_secrets(self, key: str, default: Optional[str] = None) -> str:
        """Get value from environment variables or Streamlit secrets"""
        value = os.getenv(key)
        if value:
            return value
        
        try:
            return st.secrets[key]
        except (KeyError, FileNotFoundError):
            if default is not None:
                return default
            raise ValueError(f"Missing required configuration: {key}")
    
    def _create_directories(self):
        """Create necessary directories"""
        os.makedirs(self.VECTOR_STORE_PATH, exist_ok=True)
        os.makedirs(self.TEMP_UPLOAD_PATH, exist_ok=True)
    
    def validate(self):
        """Validate critical configuration"""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        return True

settings = Settings()