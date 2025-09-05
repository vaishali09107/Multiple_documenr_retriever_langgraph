import streamlit as st
from typing import List, Optional
from ...tools.pdf_processor import PDFProcessor
from ...utils.validators import validate_pdf_file, validate_file_upload_batch
from ...config.settings import settings

class DocumentUploader:
    """Component for handling document uploads"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.max_file_size = settings.MAX_UPLOAD_SIZE * 1024 * 1024
    
    def render(self) -> Optional[List]:
        """Render the document upload interface"""
        
        st.markdown("#### Upload PDF Documents")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help=f"Upload up to 10 PDF files (max {settings.MAX_UPLOAD_SIZE}MB each)"
        )
        
        if uploaded_files:
            return self._process_uploads(uploaded_files)
        
        return None
    
    def _process_uploads(self, uploaded_files) -> Optional[List]:
        """Process and validate uploaded files"""
        
        batch_validation = validate_file_upload_batch(uploaded_files, max_files=10)
        
        if not batch_validation.is_valid:
            st.error(f"{batch_validation.error_message}")
            return None
        
        for warning in batch_validation.warnings:
            st.warning(f"{warning}")
        
        st.markdown("File Information")
        
        valid_files = []
        total_size = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                validation_result = validate_pdf_file(uploaded_file, self.max_file_size)
                
                with col1:
                    if validation_result.is_valid:
                        st.success(f"{uploaded_file.name}")
                        valid_files.append(uploaded_file)
                        total_size += len(uploaded_file.getvalue())
                        
                        file_info = self.pdf_processor.get_file_info_summary(uploaded_file)
                        st.markdown(file_info)
                    else:
                        st.error(f"{uploaded_file.name}")
                        st.error(f"Error: {validation_result.error_message}")
                
                with col2:
                    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                    st.metric("Size", f"{file_size_mb:.1f}MB")
                
                with col3:
                    if validation_result.is_valid:
                        try:
                            metadata = self.pdf_processor.extract_pdf_metadata(uploaded_file)
                            st.metric("Pages", metadata.get('num_pages', 'N/A'))
                        except:
                            st.metric("Pages", "N/A")
                
                # Show warnings for this file
                for warning in validation_result.warnings:
                    st.warning(f"{uploaded_file.name}: {warning}")
        
        if valid_files:
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valid Files", len(valid_files))
            with col2:
                total_size_mb = total_size / (1024 * 1024)
                st.metric("Total Size", f"{total_size_mb:.1f}MB")
            with col3:
                invalid_count = len(uploaded_files) - len(valid_files)
                if invalid_count > 0:
                    st.metric("Invalid Files", invalid_count, delta_color="off")
            
            if st.button("Process Documents", type="primary", use_container_width=True):
                return valid_files
        
        return None
    
    def _show_file_preview(self, uploaded_file):
        """Show a preview of the uploaded file"""
        
        try:
            previews = self.pdf_processor.extract_page_previews(uploaded_file, max_pages=1)
            
            if previews and 'text_preview' in previews[0]:
                st.markdown("**Preview:**")
                preview_text = previews[0]['text_preview'][:300]
                st.text_area("", preview_text, height=100, disabled=True, key=f"preview_{uploaded_file.name}")
        
        except Exception as e:
            st.warning(f"Could not generate preview: {str(e)}")
    
    def get_upload_statistics(self) -> dict:
        """Get statistics about current uploads"""
        return {
            "supported_formats": self.pdf_processor.supported_extensions,
            "max_file_size_mb": settings.MAX_UPLOAD_SIZE,
            "max_files": 10
        }