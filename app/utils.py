import re
import hashlib
import logging
from typing import Dict, Any, List, Tuple
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def normalize_query(query: str) -> str:
    """
    Normalizes the query string by trimming whitespace and converting to lowercase
    
    Args:
        query: The query string to normalize
        
    Returns:
        Normalized query string
    """
    return query.strip().lower()

def generate_query_hash(query: str) -> str:
    """
    Generates a hash for the query string
    
    Args:
        query: The query string
        
    Returns:
        SHA-256 hash of the query
    """
    return hashlib.sha256(query.encode()).hexdigest()

def sanitize_input(input_str: str) -> str:
    """
    Sanitizes user input to prevent injection attacks
    
    Args:
        input_str: The input string to sanitize
        
    Returns:
        Sanitized input string
    """
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[<>&\'";]', '', input_str)
    return sanitized.strip()

def format_timestamp(dt: datetime) -> str:
    """
    Formats a datetime object as a string
    
    Args:
        dt: The datetime object
        
    Returns:
        Formatted timestamp string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def merge_results(results_lists: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges multiple result dictionaries into one
    
    Args:
        results_lists: List of result dictionaries to merge
        
    Returns:
        Merged results dictionary
    """
    merged = {}
    
    for results in results_lists:
        for key, value in results.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged[key], list):
                # For lists, concatenate
                merged[key].extend(value)
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                # For dicts, merge recursively
                merged[key].update(value)
    
    return merged

def truncate_long_text(text: str, max_length: int = 200) -> str:
    """
    Truncates long text to the specified maximum length
    
    Args:
        text: The text to truncate
        max_length: The maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."

def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serializes objects to JSON, handling objects that aren't directly serializable
    
    Args:
        obj: The object to serialize
        
    Returns:
        JSON-serializable representation of the object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return str(obj)
