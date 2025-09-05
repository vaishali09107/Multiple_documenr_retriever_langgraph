import hashlib
import os
import re
import time
from typing import List, Dict, Optional
from datetime import datetime

def calculate_file_hash(file_content: bytes) -> str:
    return hashlib.md5(file_content).hexdigest()

def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def sanitize_filename(filename: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\.+', '.', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    from collections import Counter
    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 
        'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use', 'that', 'with',
        'have', 'this', 'will', 'been', 'from', 'they', 'know', 'want', 'been',
        'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just',
        'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them',
        'well', 'were'
    }
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    word_counts = Counter(filtered_words)
    
    return [word for word, count in word_counts.most_common(top_n)]

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dictionaries(dict1: Dict, dict2: Dict) -> Dict:
    merged = dict1.copy()
    merged.update(dict2)
    return merged

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator != 0 else default

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None

def calculate_text_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:()\-"]', ' ', text)
    return text.strip()

def create_progress_bar(current: int, total: int, width: int = 30) -> str:
    if total == 0:
        return "[" + "=" * width + "]"
    
    progress = current / total
    filled_width = int(width * progress)
    bar = "=" * filled_width + "-" * (width - filled_width)
    return f"[{bar}] {current}/{total} ({progress*100:.1f}%)"

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_unique_id(prefix: str = "") -> str:
    timestamp = str(int(time.time() * 1000))
    if prefix:
        return f"{prefix}_{timestamp}"
    return timestamp

def count_tokens_estimate(text: str) -> int:
    return len(text) // 4

def create_backup_filename(original_filename: str) -> str:
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_backup_{timestamp}{ext}"