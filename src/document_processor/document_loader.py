"""
Unified Document Loader
Handles loading and routing documents to appropriate extractors
"""
from pathlib import Path
from typing import Dict, Optional, Union
import os

from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor
from .text_extractor import TextExtractor
from .language_handler import LanguageHandler


class DocumentLoader:
    """
    Unified interface for loading and extracting text from various document formats
    """
    
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.text_extractor = TextExtractor()
        self.language_handler = LanguageHandler()
        
        self.supported_extensions = {
            '.pdf': self.pdf_extractor,
            '.docx': self.docx_extractor,
            '.doc': self.docx_extractor,
            '.txt': self.text_extractor
        }
    
    def load(self, 
             file_path: Optional[str] = None, 
             file_bytes: Optional[bytes] = None,
             file_name: Optional[str] = None) -> Dict:
        """
        Load and extract text from a document
        
        Args:
            file_path: Path to the document file
            file_bytes: Raw bytes of the document
            file_name: Original filename (required if using file_bytes)
            
        Returns:
            Dict containing extracted text, metadata, and language info
        """
        try:
            # Determine file extension
            if file_path:
                ext = Path(file_path).suffix.lower()
                file_name = Path(file_path).name
            elif file_name:
                ext = Path(file_name).suffix.lower()
            else:
                return {
                    "success": False,
                    "error": "file_name is required when using file_bytes"
                }
            
            # Check if format is supported
            if ext not in self.supported_extensions:
                return {
                    "success": False,
                    "error": f"Unsupported file format: {ext}. Supported formats: {list(self.supported_extensions.keys())}"
                }
            
            # Get appropriate extractor
            extractor = self.supported_extensions[ext]
            
            # Extract text
            result = extractor.extract(file_path=file_path, file_bytes=file_bytes)
            
            if not result["success"]:
                return result
            
            # Add language detection
            text = result.get("text", "")
            lang_info = self.language_handler.detect_language(text)
            nlp_prepared = self.language_handler.prepare_for_nlp(text)
            
            result.update({
                "file_name": file_name,
                "file_extension": ext,
                "language_info": lang_info,
                "normalized_text": nlp_prepared["normalized_text"],
                "requires_translation": nlp_prepared["requires_translation"]
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_file(self, file_path: Optional[str] = None, 
                      file_bytes: Optional[bytes] = None,
                      file_name: Optional[str] = None,
                      max_size_mb: int = 10) -> Dict:
        """
        Validate a file before processing
        
        Returns:
            Dict with validation status and any errors
        """
        errors = []
        
        # Check extension
        if file_path:
            ext = Path(file_path).suffix.lower()
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        elif file_name:
            ext = Path(file_name).suffix.lower()
            file_size = len(file_bytes) / (1024 * 1024) if file_bytes else 0
        else:
            return {"valid": False, "errors": ["No file provided"]}
        
        if ext not in self.supported_extensions:
            errors.append(f"Unsupported file format: {ext}")
        
        if file_size > max_size_mb:
            errors.append(f"File size ({file_size:.2f} MB) exceeds maximum ({max_size_mb} MB)")
        
        if file_size == 0:
            errors.append("File is empty")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "file_size_mb": file_size,
            "extension": ext
        }
    
    def get_supported_formats(self) -> list:
        """Return list of supported file formats"""
        return list(self.supported_extensions.keys())
