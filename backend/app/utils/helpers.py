"""
Utility helper functions.
"""
import os
import hashlib
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def is_text_file(file_path: str) -> bool:
    """
    Check if a file is likely a text file.

    Args:
        file_path: Path to the file

    Returns:
        True if file appears to be text
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            if b'\0' in chunk:
                return False
            # Try to decode as UTF-8
            chunk.decode('utf-8')
            return True
    except (UnicodeDecodeError, IOError):
        return False


def get_file_extension(file_path: str) -> str:
    """
    Get file extension in lowercase.

    Args:
        file_path: Path to the file

    Returns:
        File extension without the dot
    """
    return Path(file_path).suffix.lower().lstrip('.')


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def sanitize_path(path: str, base_path: Optional[str] = None) -> str:
    """
    Sanitize a file path to prevent directory traversal attacks.

    Args:
        path: Path to sanitize
        base_path: Optional base path to restrict to

    Returns:
        Sanitized path

    Raises:
        ValueError: If path tries to escape base_path
    """
    clean_path = os.path.normpath(path)

    if base_path:
        base = os.path.abspath(base_path)
        full_path = os.path.abspath(os.path.join(base, clean_path))

        if not full_path.startswith(base):
            raise ValueError(f"Path {path} tries to escape base directory")

        return full_path

    return clean_path


def match_patterns(path: str, patterns: List[str]) -> bool:
    """
    Check if a path matches any of the given patterns.

    Args:
        path: Path to check
        patterns: List of patterns (supports wildcards)

    Returns:
        True if path matches any pattern
    """
    from fnmatch import fnmatch

    path_str = str(path)
    path_parts = Path(path).parts

    for pattern in patterns:
        # Direct match
        if fnmatch(path_str, f"*{pattern}*"):
            return True
        # Check if pattern is in any path component
        if any(fnmatch(part, pattern) for part in path_parts):
            return True

    return False


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp
    """
    return datetime.utcnow().isoformat()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
