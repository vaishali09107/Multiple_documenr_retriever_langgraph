import asyncio
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from ..config.settings import settings

class EmbeddingService:
    def __init__(self):
        self.embedding_model = None
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        try:
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
        except Exception as e:
            print(f"Failed to initialize embedding model: {str(e)}")
            raise

    async def embed_documents_async(self, texts: List[str]) -> List[List[float]]:
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, 
                self.embedding_model.embed_documents, 
                texts
            )
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings asynchronously: {str(e)}")
            return []

    async def embed_query_async(self, query: str) -> List[float]:
        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.embedding_model.embed_query, 
                query
            )
            return embedding
        except Exception as e:
            print(f"Error generating query embedding asynchronously: {str(e)}")
            return []
    