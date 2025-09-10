import os
import tempfile
from typing import List
from langchain.schema import Document
from pypdf import PdfReader

class DocumentService:
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def process_pdf(self, uploaded_file) -> List[Document]:
        documents = []
        try:
            temp_path = self._save_temp_file(uploaded_file)
            reader = PdfReader(temp_path)
            if reader.is_encrypted:
                raise ValueError("PDF is encrypted")
            
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        full_text += f"\n\nPage {page_num + 1}:\n{page_text}"
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {str(e)}")
            
            if full_text.strip():
                metadata = {
                    'source': uploaded_file.name,
                    'filename': uploaded_file.name,
                    'total_pages': len(reader.pages),
                    'file_size': len(uploaded_file.getvalue())
                }
                
                document = Document(page_content=full_text.strip(), metadata=metadata)
                documents.append(document)
            self._cleanup_temp_file(temp_path)
            return documents
            
        except Exception as e:
            print(f"Error processing PDF {uploaded_file.name}: {str(e)}")
            return []
    
    
    def validate_file(self, uploaded_file) -> bool:
        if not uploaded_file:
            return False
        if uploaded_file.type != "application/pdf":
            return False
        if len(uploaded_file.getvalue()) == 0:
            return False
        
        try:
            temp_path = self._save_temp_file(uploaded_file)
            reader = PdfReader(temp_path)
            
            if reader.is_encrypted:
                self._cleanup_temp_file(temp_path)
                return False
            
            has_text = False
            for page in reader.pages[:3]:
                try:
                    text = page.extract_text()
                    if text.strip():
                        has_text = True
                        break
                except:
                    continue
            
            self._cleanup_temp_file(temp_path)
            return has_text
            
        except Exception as e:
            print(f"File validation error: {str(e)}")
            return False
    
    def _save_temp_file(self, uploaded_file) -> str:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_{uploaded_file.name}")
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        return temp_path
    
    def _cleanup_temp_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up temp file {file_path}: {str(e)}")