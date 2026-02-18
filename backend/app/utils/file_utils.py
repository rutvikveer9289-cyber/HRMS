"""
File Utilities
Helper functions for file operations
"""
import hashlib
from typing import Tuple
from fastapi import UploadFile

def calculate_file_hash(content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content
    
    Args:
        content: File content as bytes
        
    Returns:
        64-character hexadecimal hash string
    """
    return hashlib.sha256(content).hexdigest()

def validate_file_type(file: UploadFile, allowed_extensions: Tuple[str, ...] = ('.xlsx', '.xls', '.csv')) -> bool:
    """
    Validate if file has allowed extension
    
    Args:
        file: Uploaded file
        allowed_extensions: Tuple of allowed extensions
        
    Returns:
        True if file type is valid, False otherwise
    """
    if not file.filename:
        return False
    return file.filename.lower().endswith(allowed_extensions)

def generate_safe_filename(original_filename: str) -> str:
    """
    Generate safe filename with timestamp prefix
    
    Args:
        original_filename: Original file name
        
    Returns:
        Safe filename with timestamp
    """
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{original_filename}"

def normalize_emp_id(raw_id: str) -> str:
    """
    Normalize employee ID to RBIS0000 format if it matches the pattern.
    """
    import re
    raw_id = str(raw_id).strip()
    
    if not raw_id or raw_id.lower() == 'nan':
        return ''
    
    # Check if it's the standard format: RBIS followed optionally by non-digits, then digits
    # Goal: 'RBIS1' -> 'RBIS0001', '1' -> 'RBIS0001'
    # But leave 'RBIS-CEO1' or 'ADMIN001' alone (just uppercase)
    
    # Check for pure digits first
    if raw_id.isdigit():
        return f"RBIS{raw_id.zfill(4)}"
        
    # Check for RBIS + digits ONLY (maybe with space or hyphen in between)
    match = re.search(r'^RBIS\s*[-_]?\s*(\d+)$', raw_id, re.IGNORECASE)
    if match:
        num_part = match.group(1)
        return f"RBIS{num_part.zfill(4)}"
    
    # Otherwise, just return uppercase to keep it consistent
    return raw_id.upper()
