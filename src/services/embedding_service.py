from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from ..config.settings import settings

class EmbeddingService:
    """Service for generating embeddings from text"""
    
    def __init__(self):
        self.embedding_model = None
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize the embedding model"""
        try:
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
            print(f"Embedding model initialized: {settings.EMBEDDING_MODEL}")
            
        except Exception as e:
            print(f"Failed to initialize embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
        
        try:
            embeddings = self.embedding_model.embed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
        
        try:
            embedding = self.embedding_model.embed_query(query)
            return embedding
        except Exception as e:
            print(f"Error generating query embedding: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
        
        test_embedding = self.generate_query_embedding("test")
        return len(test_embedding)
    
    def is_initialized(self) -> bool:
        """Check if embedding model is initialized"""
        return self.embedding_model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            "model_name": settings.EMBEDDING_MODEL,
            "dimension": self.get_embedding_dimension() if self.is_initialized() else None,
            "initialized": self.is_initialized()
        }