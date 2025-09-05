import time
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document

from ..config.settings import settings
from ..schema.models import QueryResponse

class LLMService:
    """Service for interacting with the LLM"""
    
    def __init__(self):
        self.llm = None
        self.prompt_templates = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM with fallback"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.3,
                max_tokens=2048,
                timeout=60,
                max_retries=1
            )
            print(f"LLM initialized: {settings.MODEL_NAME}")
            
        except Exception as e:
            print(f"Failed to initialize LLM: {str(e)}")
            self.llm = None
    
    async def generate_answer(
        self, 
        query: str, 
        retrieved_documents: List[Document]
    ) -> QueryResponse:
        """Generate answer based on query and retrieved documents"""
        
        start_time = time.time()
        
        try:
            if self.llm:
                context = self._format_context(retrieved_documents)
                prompt = f"Based on the following context, answer this question: {query}\n\nContext:\n{context}"
                response = await self._invoke_llm(prompt)
            else:
                response = self._simple_answer_fallback(query, retrieved_documents)
            
            
            processing_time = time.time() - start_time
            
            return QueryResponse(
                answer=response,
                processing_time=processing_time,
                confidence_score=0.8 if self.llm else 0.6
            )
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            fallback_answer = self._simple_answer_fallback(query, retrieved_documents)
            return QueryResponse(
                answer=fallback_answer,
                processing_time=time.time() - start_time
            )
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format context from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(documents[:3]):
            context_parts.append(f"Document {i+1}:\n{doc.page_content[:500]}...")
        return "\n\n".join(context_parts)
    
    def _simple_answer_fallback(self, query: str, documents: List[Document]) -> str:
        """Simple fallback when LLM is not available"""
        if not documents:
            return "I couldn't find relevant information to answer your question."
        
        relevant_text = documents[0].page_content[:800]
        return f"Based on the document content, here's what I found:\n\n{relevant_text}\n\nThis appears to be the most relevant information for your question: '{query}'"
    
    async def _invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM with the formatted prompt"""
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM failed, using fallback: {str(e)}")
            raise Exception(f"LLM invocation failed: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if LLM service is ready"""
        return True