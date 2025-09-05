from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents"""
    filename: str
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    content_type: str = "application/pdf"
    total_pages: Optional[int] = None
    total_chunks: Optional[int] = None

class DocumentInfo(BaseModel):
    """Information about a document"""
    filename: str
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    content_type: str = "application/pdf"
    total_pages: Optional[int] = None
    total_chunks: Optional[int] = None
    source: str = ""

class ProcessingResult(BaseModel):
    """Result of document processing"""
    success: bool
    document_info: Optional[DocumentInfo] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None

class EmbeddingModelInfo(BaseModel):
    """Information about the embedding model"""
    model_name: str
    dimension: Optional[int] = None
    initialized: bool = False

class TextChunk(BaseModel):
    """Represents a chunk of text from a document"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    document_source: str
    page_number: Optional[int] = None

class QueryRequest(BaseModel):
    """User query request"""
    question: str
    max_results: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class QueryResponse(BaseModel):
    """Response to user query"""
    answer: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None

class VectorStoreInfo(BaseModel):
    """Information about the vector store"""
    total_documents: int = 0
    total_chunks: int = 0
    last_updated: Optional[datetime] = None
    embedding_model: str
    vector_store_type: str

class AppState(BaseModel):
    """Application state management"""
    documents_loaded: bool = False
    vector_store_ready: bool = False
    current_documents: List[DocumentMetadata] = []
    vector_store_info: Optional[VectorStoreInfo] = None