from typing import List, Optional
import streamlit as st
from ...config.settings import settings
from ...utils.validators import validate_file_upload_batch, validate_pdf_file

class DocumentUploader:
    def __init__(self):
        self.max_file_size = settings.MAX_UPLOAD_SIZE * 1024 * 1024
    
    def render(self) -> Optional[List]:
        st.markdown("#### Upload PDF Documents")
        
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
        batch_validation = validate_file_upload_batch(uploaded_files, max_files=10)
        
        if not batch_validation.is_valid:
            st.error(f"{batch_validation.error_message}")
            return None
        
        for warning in batch_validation.warnings:
            st.warning(f"{warning}")
        
        st.markdown("**File Information**")
        
        valid_files = []
        total_size = 0
        
        for uploaded_file in uploaded_files:
            validation_result = validate_pdf_file(uploaded_file, self.max_file_size)
            
            if validation_result.is_valid:
                st.success(f"✓ {uploaded_file.name}")
                valid_files.append(uploaded_file)
                total_size += len(uploaded_file.getvalue())
                
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                st.text(f"  Size: {file_size_mb:.1f}MB")
                
            else:
                st.error(f"✗ {uploaded_file.name}")
                st.error(f"  Error: {validation_result.error_message}")
            
            for warning in validation_result.warnings:
                st.warning(f"  {uploaded_file.name}: {warning}")
        
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
                    st.metric("Invalid Files", invalid_count)
            
            if st.button("Process Documents", type="primary", use_container_width=True):
                return valid_files
        
        return None