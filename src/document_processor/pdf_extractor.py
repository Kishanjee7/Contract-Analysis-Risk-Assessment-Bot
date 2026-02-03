"""
PDF Text Extractor using pdfplumber
"""
import pdfplumber
from pathlib import Path
from typing import Optional, Dict, List
import io


class PDFExtractor:
    """Extract text content from PDF files"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract(self, file_path: Optional[str] = None, file_bytes: Optional[bytes] = None) -> Dict:
        """
        Extract text from a PDF file
        
        Args:
            file_path: Path to the PDF file
            file_bytes: Raw bytes of the PDF file
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if file_bytes:
                pdf_source = io.BytesIO(file_bytes)
            elif file_path:
                pdf_source = file_path
            else:
                raise ValueError("Either file_path or file_bytes must be provided")
            
            pages_text = []
            metadata = {}
            
            with pdfplumber.open(pdf_source) as pdf:
                metadata = {
                    "num_pages": len(pdf.pages),
                    "metadata": pdf.metadata if pdf.metadata else {}
                }
                
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        pages_text.append({
                            "page_num": i + 1,
                            "text": text.strip()
                        })
            
            full_text = "\n\n".join([p["text"] for p in pages_text])
            
            return {
                "success": True,
                "text": full_text,
                "pages": pages_text,
                "metadata": metadata,
                "format": "pdf"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "format": "pdf"
            }
    
    def extract_tables(self, file_path: Optional[str] = None, file_bytes: Optional[bytes] = None) -> List[Dict]:
        """
        Extract tables from a PDF file
        
        Returns:
            List of tables found in the document
        """
        try:
            if file_bytes:
                pdf_source = io.BytesIO(file_bytes)
            elif file_path:
                pdf_source = file_path
            else:
                return []
            
            tables = []
            
            with pdfplumber.open(pdf_source) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for j, table in enumerate(page_tables):
                        tables.append({
                            "page_num": i + 1,
                            "table_num": j + 1,
                            "data": table
                        })
            
            return tables
            
        except Exception as e:
            return []
