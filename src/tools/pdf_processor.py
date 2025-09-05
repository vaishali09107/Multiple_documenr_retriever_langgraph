import os
import tempfile
from typing import List, Dict, Any
from pypdf import PdfReader

class PDFProcessor:
    """Advanced PDF processing utilities"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_pdf_metadata(self, uploaded_file) -> Dict[str, Any]:
        """Extract comprehensive metadata from PDF"""
        try:
            temp_path = self._save_temp_file(uploaded_file)
            
            reader = PdfReader(temp_path)
            
            metadata = {
                'filename': uploaded_file.name,
                'file_size': len(uploaded_file.getvalue()),
                'num_pages': len(reader.pages),
                'has_text': False,
                'total_characters': 0,
                'estimated_words': 0,
                'pdf_metadata': {}
            }
            
            if reader.metadata:
                metadata['pdf_metadata'] = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': str(reader.metadata.get('/CreationDate', '')),
                    'modification_date': str(reader.metadata.get('/ModDate', ''))
                }
            
            total_text = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    total_text += page_text
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {str(e)}")
            
            if total_text.strip():
                metadata['has_text'] = True
                metadata['total_characters'] = len(total_text)
                metadata['estimated_words'] = len(total_text.split())
            
            self._cleanup_temp_file(temp_path)
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting PDF metadata: {str(e)}")
            return {'error': str(e)}
    
    def validate_pdf_structure(self, uploaded_file) -> Dict[str, Any]:
        """Validate PDF structure and readability"""
        try:
            temp_path = self._save_temp_file(uploaded_file)
            reader = PdfReader(temp_path)
            
            validation_result = {
                'is_valid': True,
                'is_encrypted': reader.is_encrypted,
                'can_extract_text': False,
                'readable_pages': 0,
                'total_pages': len(reader.pages),
                'issues': []
            }
            
            if reader.is_encrypted:
                validation_result['issues'].append("PDF is encrypted/password protected")
                validation_result['is_valid'] = False
                return validation_result
            
            readable_pages = 0
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        readable_pages += 1
                except Exception as e:
                    validation_result['issues'].append(f"Cannot extract text from page {page_num + 1}")
            
            validation_result['readable_pages'] = readable_pages
            validation_result['can_extract_text'] = readable_pages > 0
            
            if readable_pages == 0:
                validation_result['issues'].append("No readable text found in PDF")
                validation_result['is_valid'] = False
            elif readable_pages < len(reader.pages) * 0.5:
                validation_result['issues'].append("Less than 50% of pages contain readable text")
            
            self._cleanup_temp_file(temp_path)
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'issues': [f"PDF validation error: {str(e)}"]
            }
    
    def extract_page_previews(self, uploaded_file, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Extract preview text from first few pages"""
        try:
            temp_path = self._save_temp_file(uploaded_file)
            reader = PdfReader(temp_path)
            
            previews = []
            for page_num in range(min(max_pages, len(reader.pages))):
                try:
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    preview = {
                        'page_number': page_num + 1,
                        'text_preview': text[:500] + "..." if len(text) > 500 else text,
                        'character_count': len(text),
                        'word_count': len(text.split()) if text else 0
                    }
                    previews.append(preview)
                    
                except Exception as e:
                    previews.append({
                        'page_number': page_num + 1,
                        'text_preview': f"Error extracting text: {str(e)}",
                        'character_count': 0,
                        'word_count': 0
                    })
            
            self._cleanup_temp_file(temp_path)
            return previews
            
        except Exception as e:
            return [{'error': f"Could not extract previews: {str(e)}"}]
    
    def _save_temp_file(self, uploaded_file) -> str:
        """Save uploaded file to temporary location"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_{uploaded_file.name}")
        
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        return temp_path
    
    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up temp file {file_path}: {str(e)}")
    
    def get_file_info_summary(self, uploaded_file) -> str:
        """Get a human-readable summary of PDF info"""
        metadata = self.extract_pdf_metadata(uploaded_file)
        
        if 'error' in metadata:
            return f"Error processing PDF: {metadata['error']}"
        
        summary = f"""
            {metadata['filename']}
            - Pages: {metadata['num_pages']}
            - Size: {metadata['file_size'] / 1024:.1f} KB
            - Text extractable: {metadata['has_text']}
            - Estimated words: {metadata['estimated_words']:,}
        """
        
        if metadata['pdf_metadata'].get('title'):
            summary += f"- Title: {metadata['pdf_metadata']['title']}\n"
        if metadata['pdf_metadata'].get('author'):
            summary += f"- Author: {metadata['pdf_metadata']['author']}\n"
        
        return summary.strip()