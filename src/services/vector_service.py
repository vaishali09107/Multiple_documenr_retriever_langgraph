import os
from typing import List
from datetime import datetime
from langchain_community.vectorstores import FAISS, Chroma
from langchain.schema import Document
from ..config.settings import settings
from ..services.embedding_service import EmbeddingService
from ..schema.models import VectorStoreInfo

class VectorService:
    """Service for managing vector store operations"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = None
        self.vector_store_info = VectorStoreInfo(
            embedding_model=settings.EMBEDDING_MODEL,
            vector_store_type=settings.VECTOR_STORE_TYPE
        )
    
    async def create_vector_store(self, documents: List[Document]) -> bool:
        """Create vector store from documents"""
        try:
            print(f"Creating vector store with {len(documents)} documents...")
            
            if settings.VECTOR_STORE_TYPE.lower() == "faiss":
                self.vector_store = FAISS.from_documents(
                    documents, 
                    self.embedding_service.embedding_model
                )
            elif settings.VECTOR_STORE_TYPE.lower() == "chroma":
                self.vector_store = Chroma.from_documents(
                    documents, 
                    self.embedding_service.embedding_model,
                    persist_directory=settings.VECTOR_STORE_PATH
                )
            else:
                raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}")
            
            self.vector_store_info.total_documents = len(set(doc.metadata.get('source', '') for doc in documents))
            self.vector_store_info.total_chunks = len(documents)
            self.vector_store_info.last_updated = datetime.now()
            
            print(f"Vector store created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            return False
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """Add new documents to existing vector store"""
        try:
            if not self.vector_store:
                return await self.create_vector_store(documents)
            
            print(f"Adding {len(documents)} documents to vector store...")
            
            if hasattr(self.vector_store, 'add_documents'):
                self.vector_store.add_documents(documents)
            else:
                new_vector_store = FAISS.from_documents(
                    documents, 
                    self.embedding_service.embedding_model
                )
                self.vector_store.merge_from(new_vector_store)
            
            self.vector_store_info.total_chunks += len(documents)
            self.vector_store_info.last_updated = datetime.now()
            
            print(f"Documents added successfully!")
            return True
            
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            return False
    
    def search_similar_documents(self, query: str, k: int = 20, score_threshold: float = 0.7) -> List[Document]:
        """Search for similar documents"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            print(f"Searching for query: '{query}' with k={k}")
            print(f"Vector store type: {type(self.vector_store)}")
            print(f"Vector store ready: {self.vector_store is not None}")
            
            relevant_docs = self.vector_store.similarity_search(query, k=k)
            
            print(f"Found {len(relevant_docs)} documents for query: '{query[:50]}...'")
            
            for i, doc in enumerate(relevant_docs[:3]):
                print(f"  Doc {i+1}: {doc.page_content[:100]}...")
                print(f"  Metadata: {doc.metadata}")
            
            return relevant_docs
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_vector_store(self) -> bool:
        """Save vector store to disk"""
        try:
            if not self.vector_store:
                return False
            
            if settings.VECTOR_STORE_TYPE.lower() == "faiss":
                self.vector_store.save_local(settings.VECTOR_STORE_PATH)
            elif settings.VECTOR_STORE_TYPE.lower() == "chroma":
                pass
            
            print("Vector store saved successfully!")
            return True
            
        except Exception as e:
            print(f"Error saving vector store: {str(e)}")
            return False
    
    def load_vector_store(self) -> bool:
        """Load vector store from disk"""
        try:
            if not os.path.exists(settings.VECTOR_STORE_PATH):
                return False
            
            if settings.VECTOR_STORE_TYPE.lower() == "faiss":
                if os.path.exists(os.path.join(settings.VECTOR_STORE_PATH, "index.faiss")):
                    self.vector_store = FAISS.load_local(
                        settings.VECTOR_STORE_PATH, 
                        self.embedding_service.embedding_model,
                        allow_dangerous_deserialization=True
                    )
                else:
                    return False
            elif settings.VECTOR_STORE_TYPE.lower() == "chroma":
                self.vector_store = Chroma(
                    persist_directory=settings.VECTOR_STORE_PATH,
                    embedding_function=self.embedding_service.embedding_model
                )
            
            print("Vector store loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def clear_vector_store(self):
        """Clear the vector store"""
        self.vector_store = None
        self.vector_store_info = VectorStoreInfo(
            embedding_model=settings.EMBEDDING_MODEL,
            vector_store_type=settings.VECTOR_STORE_TYPE
        )
    
    def is_ready(self) -> bool:
        """Check if vector store is ready"""
        return self.vector_store is not None
    
    def get_stats(self) -> VectorStoreInfo:
        """Get vector store statistics"""
        return self.vector_store_info