"""
File Utilities
Helper functions for file handling
"""
from pathlib import Path
from typing import Optional, Tuple
import os


class FileUtils:
    """Utility functions for file operations"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    MAX_FILE_SIZE_MB = 10
    
    @staticmethod
    def validate_file(file_path: str = None, 
                     file_bytes: bytes = None,
                     file_name: str = None) -> Tuple[bool, str]:
        """
        Validate a file for processing
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get extension
        if file_path:
            ext = Path(file_path).suffix.lower()
            file_size = os.path.getsize(file_path)
        elif file_name:
            ext = Path(file_name).suffix.lower()
            file_size = len(file_bytes) if file_bytes else 0
        else:
            return False, "No file provided"
        
        # Check extension
        if ext not in FileUtils.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type: {ext}. Allowed: {', '.join(FileUtils.ALLOWED_EXTENSIONS)}"
        
        # Check size
        size_mb = file_size / (1024 * 1024)
        if size_mb > FileUtils.MAX_FILE_SIZE_MB:
            return False, f"File too large: {size_mb:.2f} MB. Maximum: {FileUtils.MAX_FILE_SIZE_MB} MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, ""
    
    @staticmethod
    def get_file_info(file_path: str = None,
                     file_bytes: bytes = None,
                     file_name: str = None) -> dict:
        """Get basic file information"""
        info = {
            "name": "",
            "extension": "",
            "size_bytes": 0,
            "size_mb": 0
        }
        
        if file_path:
            path = Path(file_path)
            info["name"] = path.name
            info["extension"] = path.suffix.lower()
            info["size_bytes"] = os.path.getsize(file_path)
        elif file_name:
            path = Path(file_name)
            info["name"] = path.name
            info["extension"] = path.suffix.lower()
            info["size_bytes"] = len(file_bytes) if file_bytes else 0
        
        info["size_mb"] = round(info["size_bytes"] / (1024 * 1024), 2)
        
        return info
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        return safe_name
