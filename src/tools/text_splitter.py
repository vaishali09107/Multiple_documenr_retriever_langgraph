from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from ..config.settings import settings

class DocumentTextSplitter:
    """Text splitter for processing documents into chunks"""
    
    def __init__(self, 
                    chunk_size: int = None, 
                    chunk_overlap: int = None,
                    separators: List[str] = None):
        
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        try:
            print(f"Splitting {len(documents)} documents into chunks...")
            
            chunks = self.text_splitter.split_documents(documents)
            
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'chunk_id': f"chunk_{i}",
                    'chunk_size': len(chunk.page_content),
                    'total_chunks': len(chunks)
                })
            
            print(f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks
            
        except Exception as e:
            print(f"Error splitting documents: {str(e)}")
            return []
    
    def split_text(self, text: str, metadata: dict = None) -> List[Document]:
        """Split raw text into document chunks"""
        try:
            doc = Document(page_content=text, metadata=metadata or {})
            
            chunks = self.text_splitter.split_documents([doc])
            
            return chunks
            
        except Exception as e:
            print(f"Error splitting text: {str(e)}")
            return []
    
    def get_chunk_stats(self, chunks: List[Document]) -> dict:
        """Get statistics about the chunks"""
        if not chunks:
            return {"total_chunks": 0, "avg_size": 0, "max_size": 0, "min_size": 0}
        
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_size": sum(chunk_sizes) / len(chunk_sizes),
            "max_size": max(chunk_sizes),
            "min_size": min(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }
    
    def update_settings(self, chunk_size: int = None, chunk_overlap: int = None):
        """Update splitter settings"""
        if chunk_size:
            self.chunk_size = chunk_size
        if chunk_overlap:
            self.chunk_overlap = chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len
        )