from typing import Dict, List, Any, Optional, Annotated
from pydantic import BaseModel, Field

def add_documents(existing: List[Dict[str, Any]], new: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return existing + new

def update_metadata(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    existing.update(new)
    return existing

class QueryResponse(BaseModel):
    answer: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    relevant_chunks: Optional[List[str]] = None

class ResearchState(BaseModel):
    uploaded_files: Optional[List[Dict[str, Any]]] = None
    processed_documents: Annotated[List[Dict[str, Any]], add_documents] = Field(default_factory=list)
    document_metadata: Annotated[Dict[str, Any], update_metadata] = Field(default_factory=dict)
    index_built: bool = False
    query: Optional[str] = None
    retrieved_documents: Optional[List[Dict[str, Any]]] = None
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_status: str = "idle"
    human_feedback: Optional[str] = None
    approved_for_processing: bool = False
    max_results: int = 5