from typing import List
from langchain.schema import Document

from ..services.vector_service import VectorService
from ..schema.models import QueryRequest

class DocumentRetriever:
    """Simple document retriever for basic similarity search"""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
    
    def retrieve_relevant_documents(self, query_request: QueryRequest) -> List[Document]:
        """Retrieve relevant documents based on query"""
        
        if not self.vector_service.is_ready():
            print("Vector store not ready")
            return []
        
        try:
            relevant_docs = self.vector_service.search_similar_documents(
                query=query_request.question,
                k=query_request.max_results
            )
            
            print(f"Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs
            
        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            return []