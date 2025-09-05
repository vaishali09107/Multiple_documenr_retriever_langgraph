import os
import re
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

def validate_pdf_file(uploaded_file, max_size_bytes: int) -> ValidationResult:
    if uploaded_file is None:
        return ValidationResult(False, "No file uploaded")
    
    filename = uploaded_file.name.lower()
    if not filename.endswith('.pdf'):
        return ValidationResult(False, "File must be a PDF (.pdf extension)")
    
    file_size = len(uploaded_file.getvalue())
    if file_size == 0:
        return ValidationResult(False, "File is empty")
    
    if file_size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        current_mb = file_size / (1024 * 1024)
        return ValidationResult(
            False, 
            f"File too large ({current_mb:.1f}MB). Maximum size allowed: {max_mb:.0f}MB"
        )
    
    if len(filename) > 255:
        return ValidationResult(False, "Filename too long (maximum 255 characters)")
    
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in uploaded_file.name for char in invalid_chars):
        return ValidationResult(
            False, 
            f"Filename contains invalid characters: {', '.join(invalid_chars)}"
        )
    
    warnings = []
    
    if file_size > max_size_bytes * 0.8:  # 80% of max size
        warnings.append("Large file size may cause slower processing")

    if len(filename) > 100:
        warnings.append("Long filename may be truncated in displays")
    
    return ValidationResult(True, warnings=warnings)

def validate_query(query: str) -> ValidationResult:
    if not query or not query.strip():
        return ValidationResult(False, "Query cannot be empty")
    
    query = query.strip()
    
    if len(query) < 3:
        return ValidationResult(False, "Query must be at least 3 characters long")
    
    if len(query) > 1000:
        return ValidationResult(False, "Query too long (maximum 1000 characters)")
    
    warnings = []
    
    if len(query) < 10:
        warnings.append("Short queries may not provide optimal results")
    
    if not any(c.isalnum() for c in query):
        warnings.append("Query should contain some alphanumeric characters")
    
    if query.isupper() and len(query) > 10:
        warnings.append("Consider using mixed case for better readability")
    
    return ValidationResult(True, warnings=warnings)

def validate_chunk_parameters(chunk_size: int, chunk_overlap: int) -> ValidationResult:
    if chunk_size <= 0:
        return ValidationResult(False, "Chunk size must be positive")
    
    if chunk_overlap < 0:
        return ValidationResult(False, "Chunk overlap cannot be negative")
    
    if chunk_overlap >= chunk_size:
        return ValidationResult(False, "Chunk overlap must be less than chunk size")
    
    warnings = []
    
    if chunk_size < 100:
        warnings.append("Very small chunk size may result in fragmented context")
    elif chunk_size > 2000:
        warnings.append("Very large chunk size may exceed model context limits")
    
    if chunk_overlap > chunk_size * 0.5:
        warnings.append("High overlap ratio may cause redundant processing")
    
    return ValidationResult(True, warnings=warnings)

def validate_similarity_threshold(threshold: float) -> ValidationResult:
    if not isinstance(threshold, (int, float)):
        return ValidationResult(False, "Similarity threshold must be a number")
    
    if threshold < 0.0 or threshold > 1.0:
        return ValidationResult(False, "Similarity threshold must be between 0.0 and 1.0")
    
    warnings = []
    
    if threshold < 0.3:
        warnings.append("Very low threshold may return irrelevant results")
    elif threshold > 0.9:
        warnings.append("Very high threshold may return too few results")
    
    return ValidationResult(True, warnings=warnings)

def validate_max_results(max_results: int) -> ValidationResult:
    if not isinstance(max_results, int):
        return ValidationResult(False, "Maximum results must be an integer")
    
    if max_results <= 0:
        return ValidationResult(False, "Maximum results must be positive")
    
    if max_results > 50:
        return ValidationResult(False, "Maximum results cannot exceed 50")
    
    warnings = []
    
    if max_results < 3:
        warnings.append("Very few results may not provide sufficient context")
    elif max_results > 20:
        warnings.append("Many results may slow down processing")
    
    return ValidationResult(True, warnings=warnings)

def validate_api_key(api_key: str) -> ValidationResult:
    if not api_key or not api_key.strip():
        return ValidationResult(False, "API key cannot be empty")
    
    api_key = api_key.strip()
    
    if not api_key.startswith('AIza'):
        return ValidationResult(False, "Invalid Google API key format")
    
    if len(api_key) < 30:
        return ValidationResult(False, "API key too short")
    
    if len(api_key) > 50:
        return ValidationResult(False, "API key too long")
    
    return ValidationResult(True)

def validate_document_content(content: str) -> ValidationResult:
    if not content or not content.strip():
        return ValidationResult(False, "Document content is empty")
    
    content = content.strip()
    
    if len(content) < 50:
        return ValidationResult(False, "Document content too short (minimum 50 characters)")
    
    warnings = []
    
    printable_chars = sum(1 for c in content if c.isprintable())
    if printable_chars / len(content) < 0.8:
        warnings.append("Document contains significant non-text content")
    
    repeated_patterns = re.findall(r'(.)\1{10,}', content)
    if repeated_patterns:
        warnings.append("Document may contain OCR artifacts or formatting issues")
    
    return ValidationResult(True, warnings=warnings)

def validate_file_upload_batch(uploaded_files, max_files: int = 10) -> ValidationResult:    
    if not uploaded_files:
        return ValidationResult(False, "No files uploaded")
    
    if len(uploaded_files) > max_files:
        return ValidationResult(False, f"Too many files (maximum {max_files} allowed)")
    
    filenames = [f.name for f in uploaded_files]
    if len(filenames) != len(set(filenames)):
        return ValidationResult(False, "Duplicate filenames not allowed")
    
    warnings = []
    
    if len(uploaded_files) > 5:
        warnings.append("Processing many files may take longer")
    
    return ValidationResult(True, warnings=warnings)