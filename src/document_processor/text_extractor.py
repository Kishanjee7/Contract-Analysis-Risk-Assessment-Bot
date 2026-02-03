"""
Plain Text File Extractor
"""
from pathlib import Path
from typing import Optional, Dict
import chardet


class TextExtractor:
    """Extract text content from plain text files"""
    
    def __init__(self):
        self.supported_extensions = ['.txt']
    
    def extract(self, file_path: Optional[str] = None, file_bytes: Optional[bytes] = None) -> Dict:
        """
        Extract text from a plain text file
        
        Args:
            file_path: Path to the text file
            file_bytes: Raw bytes of the text file
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if file_bytes:
                # Detect encoding
                detected = chardet.detect(file_bytes)
                encoding = detected.get('encoding', 'utf-8')
                text = file_bytes.decode(encoding)
            elif file_path:
                path = Path(file_path)
                # Try to detect encoding
                with open(path, 'rb') as f:
                    raw = f.read()
                    detected = chardet.detect(raw)
                    encoding = detected.get('encoding', 'utf-8')
                
                with open(path, 'r', encoding=encoding) as f:
                    text = f.read()
            else:
                raise ValueError("Either file_path or file_bytes must be provided")
            
            lines = text.split('\n')
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            metadata = {
                "num_lines": len(lines),
                "num_paragraphs": len(paragraphs),
                "encoding": encoding,
                "char_count": len(text)
            }
            
            return {
                "success": True,
                "text": text.strip(),
                "lines": lines,
                "paragraphs": paragraphs,
                "metadata": metadata,
                "format": "txt"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "format": "txt"
            }
