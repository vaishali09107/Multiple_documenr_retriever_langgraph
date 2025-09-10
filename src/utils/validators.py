from typing import List, Optional
from pydantic import BaseModel
from ..config.settings import settings

class ValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = []

def validate_query(query: str) -> ValidationResult:
    if not query or not query.strip():
        return ValidationResult(
            is_valid=False,
            error_message="Query cannot be empty"
        )
    
    query = query.strip()
    
    if len(query) < settings.MIN_QUERY_LENGTH:
        return ValidationResult(
            is_valid=False,
            error_message=f"Query must be at least {settings.MIN_QUERY_LENGTH} characters long"
        )
    
    if len(query) > settings.MAX_QUERY_LENGTH:
        return ValidationResult(
            is_valid=False,
            error_message=f"Query must be less than {settings.MAX_QUERY_LENGTH} characters long"
        )
    
    warnings = []
    if len(query) < 10:
        warnings.append("Very short queries may not return optimal results")
    
    return ValidationResult(is_valid=True, warnings=warnings)

def validate_pdf_file(uploaded_file, max_file_size: int) -> ValidationResult:
    if not uploaded_file:
        return ValidationResult(
            is_valid=False,
            error_message="No file provided"
        )
    
    if uploaded_file.type != "application/pdf":
        return ValidationResult(
            is_valid=False,
            error_message="Only PDF files are supported"
        )
    
    file_size = len(uploaded_file.getvalue())
    if file_size == 0:
        return ValidationResult(
            is_valid=False,
            error_message="File is empty"
        )
    
    if file_size > max_file_size:
        return ValidationResult(
            is_valid=False,
            error_message=f"File size exceeds limit of {max_file_size / (1024*1024):.1f}MB"
        )
    
    warnings = []
    if file_size > max_file_size * 0.8:
        warnings.append("Large file size may slow processing")
    
    return ValidationResult(is_valid=True, warnings=warnings)

def validate_file_upload_batch(uploaded_files: List, max_files: int = 10) -> ValidationResult:
    if not uploaded_files:
        return ValidationResult(
            is_valid=False,
            error_message="No files uploaded"
        )
    
    if len(uploaded_files) > max_files:
        return ValidationResult(
            is_valid=False,
            error_message=f"Maximum {max_files} files allowed"
        )
    
    total_size = sum(len(file.getvalue()) for file in uploaded_files)
    max_total_size = settings.MAX_UPLOAD_SIZE * 1024 * 1024 * max_files
    
    warnings = []
    if total_size > max_total_size * 0.8:
        warnings.append("Large total file size may impact processing speed")
    
    return ValidationResult(is_valid=True, warnings=warnings)