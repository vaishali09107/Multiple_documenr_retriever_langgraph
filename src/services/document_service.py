import os
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from ..config.settings import settings
from ..schema.models import DocumentMetadata
from ..utils.helpers import calculate_file_hash
from ..utils.validators import validate_pdf_file

class DocumentService:
    """Service for handling document operations"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_file_size = settings.MAX_UPLOAD_SIZE * 1024 * 1024
    
    async def load_documents_from_files(self, uploaded_files) -> Tuple[List[Document], List[DocumentMetadata]]:
        """Load documents from uploaded files"""
        documents = []
        metadata_list = []
        
        for uploaded_file in uploaded_files:
            try:
                validation_result = validate_pdf_file(uploaded_file, self.max_file_size)
                if not validation_result.is_valid:
                    raise ValueError(f"File validation failed for {uploaded_file.name}: {validation_result.error_message}")
                
                temp_file_path = await self._save_temp_file(uploaded_file)
                
                docs = await self._load_pdf_document(temp_file_path)
                
                doc_metadata = DocumentMetadata(
                    filename=uploaded_file.name,
                    file_size=len(uploaded_file.getvalue()),
                    content_type=uploaded_file.type,
                    total_pages=len(docs)
                )
                
                for doc in docs:
                    doc.metadata.update({
                        'source': uploaded_file.name,
                        'file_size': doc_metadata.file_size,
                        'upload_timestamp': doc_metadata.upload_timestamp.isoformat(),
                        'file_hash': calculate_file_hash(uploaded_file.getvalue())
                    })
                
                documents.extend(docs)
                metadata_list.append(doc_metadata)
                
                self._cleanup_temp_file(temp_file_path)
                
            except Exception as e:
                print(f"Error loading document {uploaded_file.name}: {str(e)}")
                continue
        
        return documents, metadata_list
    
    async def _save_temp_file(self, uploaded_file) -> str:
        """Save uploaded file to temporary location"""
        temp_dir = settings.TEMP_UPLOAD_PATH
        temp_file_path = os.path.join(temp_dir, f"temp_{uploaded_file.name}")
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        return temp_file_path
    
    async def _load_pdf_document(self, file_path: str) -> List[Document]:
        """Load PDF document using LangChain loader"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            for i, doc in enumerate(documents):
                doc.metadata['page'] = i + 1
            
            return documents
        except Exception as e:
            raise Exception(f"Failed to load PDF: {str(e)}")
    
    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up temp file {file_path}: {str(e)}")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.supported_formats
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported"""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.supported_formats