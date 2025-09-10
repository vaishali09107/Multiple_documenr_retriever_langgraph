import asyncio
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from ..config.settings import settings
from ..services.embedding_service import EmbeddingService

class VectorService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> bool:
        try:
            print(f"Creating vector store with {len(documents)} documents...")
            
            self.vector_store = FAISS.from_documents(
                documents, 
                self.embedding_service.embedding_model
            )
            
            print("Vector store created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            return False

    async def create_vector_store_parallel(self, documents: List[Document], batch_size: int = None) -> bool:
        try:
            if batch_size is None:
                batch_size = settings.EMBEDDING_BATCH_SIZE
                
            print(f"Creating vector store with {len(documents)} documents using parallel processing (batch_size={batch_size})...")
            
            if not documents:
                return False
            
            async def process_batch(batch_docs: List[Document]) -> List[Document]:
                try:
                    embeddings = await self._generate_embeddings_parallel([doc.page_content for doc in batch_docs])
                    for i, doc in enumerate(batch_docs):
                        if i < len(embeddings):
                            doc.metadata['embedding'] = embeddings[i]
                    return batch_docs
                except Exception as e:
                    print(f"Error processing batch: {str(e)}")
                    return []
            
            batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
            tasks = [process_batch(batch) for batch in batches]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            processed_docs = []
            for result in results:
                if isinstance(result, list):
                    processed_docs.extend(result)
            
            if not processed_docs:
                print("No documents were successfully processed")
                return False
            
            self.vector_store = FAISS.from_documents(
                processed_docs, 
                self.embedding_service.embedding_model
            )
            
            print(f"Vector store created successfully with {len(processed_docs)} documents!")
            return True
            
        except Exception as e:
            print(f"Error creating vector store with parallel processing: {str(e)}")
            return False

    async def _generate_embeddings_parallel(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = await self.embedding_service.embed_documents_async(texts)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            return []
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Document]:
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            relevant_docs = self.vector_store.similarity_search(query, k=k)
            print(f"Found {len(relevant_docs)} documents for query: '{query[:50]}...'")
            return relevant_docs
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []

    async def search_similar_documents_async(self, query: str, k: int = 5) -> List[Document]:
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            relevant_docs = await loop.run_in_executor(
                None, 
                self.vector_store.similarity_search, 
                query, 
                k
            )
            print(f"Found {len(relevant_docs)} documents for query: '{query[:50]}...'")
            return relevant_docs
            
        except Exception as e:
            print(f"Error searching documents asynchronously: {str(e)}")
            return []
    
    def is_ready(self) -> bool:
        return self.vector_store is not None