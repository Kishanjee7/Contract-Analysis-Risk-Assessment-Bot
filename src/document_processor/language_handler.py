"""
Language Handler for Hindi/English detection and normalization
"""
from langdetect import detect, detect_langs
from typing import Dict, List, Optional
import re


class LanguageHandler:
    """Handle language detection and multilingual processing"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi'
        }
        
        # Common Hindi legal terms that might appear in contracts
        self.hindi_legal_terms = {
            'अनुबंध': 'contract',
            'करार': 'agreement',
            'पक्ष': 'party',
            'नियम': 'terms',
            'शर्तें': 'conditions',
            'दायित्व': 'liability',
            'अधिकार': 'rights',
            'समाप्ति': 'termination',
            'हस्ताक्षर': 'signature',
            'गवाह': 'witness',
            'तारीख': 'date',
            'राशि': 'amount',
            'भुगतान': 'payment',
            'अवधि': 'duration',
            'नोटिस': 'notice',
            'विवाद': 'dispute',
            'मध्यस्थता': 'arbitration',
            'क्षतिपूर्ति': 'indemnity',
            'गोपनीयता': 'confidentiality',
            'बौद्धिक संपदा': 'intellectual property'
        }
    
    def detect_language(self, text: str) -> Dict:
        """
        Detect the primary language of the text
        
        Returns:
            Dict with detected language info
        """
        try:
            if not text or len(text.strip()) < 10:
                return {
                    "primary_lang": "unknown",
                    "confidence": 0,
                    "detected_languages": []
                }
            
            # Clean text for detection
            clean_text = self._clean_for_detection(text)
            
            # Get primary language
            primary_lang = detect(clean_text)
            
            # Get all detected languages with probabilities
            detected_langs = detect_langs(clean_text)
            lang_probs = [{"lang": str(lang).split(':')[0], "prob": lang.prob} for lang in detected_langs]
            
            return {
                "primary_lang": primary_lang,
                "confidence": max([l["prob"] for l in lang_probs]) if lang_probs else 0,
                "detected_languages": lang_probs,
                "is_multilingual": len([l for l in lang_probs if l["prob"] > 0.1]) > 1
            }
            
        except Exception as e:
            return {
                "primary_lang": "unknown",
                "confidence": 0,
                "error": str(e)
            }
    
    def _clean_for_detection(self, text: str) -> str:
        """Clean text for better language detection"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common legal formatting
        text = re.sub(r'^\d+[\.\)]\s*', '', text, flags=re.MULTILINE)
        return text.strip()
    
    def is_hindi(self, text: str) -> bool:
        """Check if text is primarily in Hindi"""
        result = self.detect_language(text)
        return result.get("primary_lang") == "hi"
    
    def is_english(self, text: str) -> bool:
        """Check if text is primarily in English"""
        result = self.detect_language(text)
        return result.get("primary_lang") == "en"
    
    def get_hindi_segments(self, text: str) -> List[str]:
        """Extract Hindi text segments from mixed text"""
        # Hindi Unicode range: \u0900-\u097F
        hindi_pattern = r'[\u0900-\u097F]+'
        segments = re.findall(hindi_pattern, text)
        return segments
    
    def get_english_segments(self, text: str) -> List[str]:
        """Extract English text segments from mixed text"""
        # Basic Latin + Extended Latin
        english_pattern = r'[a-zA-Z]+'
        segments = re.findall(english_pattern, text)
        return segments
    
    def normalize_hindi_terms(self, text: str) -> str:
        """
        Replace common Hindi legal terms with English equivalents
        for better NLP processing
        """
        normalized = text
        for hindi, english in self.hindi_legal_terms.items():
            normalized = normalized.replace(hindi, f" {english} ")
        return normalized
    
    def prepare_for_nlp(self, text: str) -> Dict:
        """
        Prepare text for NLP processing with language-aware handling
        
        Returns:
            Dict with original text, normalized text, and language info
        """
        lang_info = self.detect_language(text)
        
        if lang_info["primary_lang"] == "hi":
            # Normalize Hindi terms for better processing
            normalized_text = self.normalize_hindi_terms(text)
        else:
            normalized_text = text
        
        return {
            "original_text": text,
            "normalized_text": normalized_text,
            "language_info": lang_info,
            "requires_translation": lang_info["primary_lang"] == "hi"
        }
