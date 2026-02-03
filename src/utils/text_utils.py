"""
Text Utilities
Helper functions for text processing
"""
import re
from typing import List


class TextUtils:
    """Utility functions for text processing"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text.strip()
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Handle common abbreviations
        text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Ltd|Pvt|Inc|Corp|vs|etc)\.\s', r'\1<DOT> ', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Restore periods
        sentences = [s.replace('<DOT>', '.') for s in sentences]
        
        # Filter empty sentences
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def get_word_count(text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        words = text.split()
        return len(words)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def highlight_keywords(text: str, keywords: List[str], 
                          before: str = "**", after: str = "**") -> str:
        """Highlight keywords in text"""
        result = text
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            result = pattern.sub(f"{before}{keyword}{after}", result)
        return result
    
    @staticmethod
    def extract_section(text: str, start_marker: str, end_marker: str = None) -> str:
        """Extract a section of text between markers"""
        start_idx = text.lower().find(start_marker.lower())
        if start_idx == -1:
            return ""
        
        if end_marker:
            end_idx = text.lower().find(end_marker.lower(), start_idx + len(start_marker))
            if end_idx == -1:
                return text[start_idx:]
            return text[start_idx:end_idx]
        
        return text[start_idx:]
