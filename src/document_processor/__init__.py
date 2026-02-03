"""
Document Processor Module
Handles extraction of text from PDF, DOCX, and TXT files
"""
from .document_loader import DocumentLoader
from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor
from .text_extractor import TextExtractor
from .language_handler import LanguageHandler

__all__ = [
    "DocumentLoader",
    "PDFExtractor",
    "DOCXExtractor",
    "TextExtractor",
    "LanguageHandler"
]
