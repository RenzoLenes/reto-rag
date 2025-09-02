import uuid
import re
from datetime import datetime


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def sanitize_text_for_json(text: str) -> str:
    """
    Sanitize text by removing invalid control characters for JSON serialization.
    
    Args:
        text: Input text that may contain control characters
        
    Returns:
        str: Cleaned text safe for JSON serialization
    """
    if not text:
        return text
    
    # Remove control characters except \n, \r, \t
    # Keep only printable characters, whitespace, and common line breaks
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Replace problematic Unicode characters
    text = text.replace('\u0000', '')  # Null character
    text = text.replace('\ufeff', '')  # Byte order mark
    
    # Normalize whitespace while preserving line breaks
    text = re.sub(r'\r\n', '\n', text)  # Convert CRLF to LF
    text = re.sub(r'\r', '\n', text)    # Convert CR to LF
    
    return text.strip()