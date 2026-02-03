"""
Obligation Analyzer
Identifies obligations, rights, and prohibitions in contract clauses
"""
import re
from typing import Dict, List, Tuple


class ObligationAnalyzer:
    """Analyze contract text to identify obligations, rights, and prohibitions"""
    
    def __init__(self):
        # Linguistic markers for different obligation types
        self.markers = {
            "obligation": {
                "strong": ["shall", "must", "will", "agrees to", "undertakes to", 
                          "is required to", "commits to", "is obligated to"],
                "moderate": ["should", "is expected to", "is responsible for",
                            "has the duty to", "needs to"],
                "conditional": ["shall, upon", "must, if", "will, provided that"]
            },
            "right": {
                "strong": ["may", "is entitled to", "has the right to", 
                          "reserves the right to", "can", "is permitted to"],
                "moderate": ["could", "might", "is allowed to"],
                "exclusive": ["sole right", "exclusive right", "sole discretion"]
            },
            "prohibition": {
                "strong": ["shall not", "must not", "will not", "cannot", 
                          "may not", "is prohibited from", "is not permitted to"],
                "moderate": ["should not", "is not allowed to"],
                "exceptions": ["except as", "unless", "provided however"]
            }
        }
        
        # Party role indicators
        self.party_roles = {
            "first_party": ["party of the first part", "first party", "company", 
                           "employer", "lessor", "vendor", "service provider", "licensor"],
            "second_party": ["party of the second part", "second party", "employee",
                            "lessee", "tenant", "client", "customer", "licensee"],
            "both_parties": ["both parties", "either party", "each party", "parties"]
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze text to extract obligations, rights, and prohibitions
        
        Args:
            text: Contract clause or full contract text
            
        Returns:
            Dict with categorized statements
        """
        sentences = self._split_sentences(text)
        
        obligations = []
        rights = []
        prohibitions = []
        
        for sentence in sentences:
            classification = self._classify_sentence(sentence)
            
            if classification["type"] == "obligation":
                obligations.append({
                    "text": sentence,
                    "strength": classification["strength"],
                    "affected_party": classification["affected_party"],
                    "markers_found": classification["markers"]
                })
            elif classification["type"] == "right":
                rights.append({
                    "text": sentence,
                    "strength": classification["strength"],
                    "affected_party": classification["affected_party"],
                    "markers_found": classification["markers"]
                })
            elif classification["type"] == "prohibition":
                prohibitions.append({
                    "text": sentence,
                    "strength": classification["strength"],
                    "affected_party": classification["affected_party"],
                    "markers_found": classification["markers"]
                })
        
        return {
            "obligations": obligations,
            "rights": rights,
            "prohibitions": prohibitions,
            "summary": {
                "total_obligations": len(obligations),
                "total_rights": len(rights),
                "total_prohibitions": len(prohibitions),
                "strong_obligations": len([o for o in obligations if o["strength"] == "strong"]),
                "exclusive_rights": len([r for r in rights if r["strength"] == "exclusive"])
            }
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle common abbreviations to avoid false splits
        text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Ltd|Pvt|Inc|Corp|vs|etc)\.\s', r'\1<DOT> ', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Restore periods
        sentences = [s.replace('<DOT>', '.') for s in sentences]
        
        # Filter empty and very short sentences
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _classify_sentence(self, sentence: str) -> Dict:
        """Classify a sentence as obligation, right, or prohibition"""
        sentence_lower = sentence.lower()
        
        # Check for prohibitions first (they often contain obligation markers too)
        for strength, markers in self.markers["prohibition"].items():
            for marker in markers:
                if marker in sentence_lower:
                    return {
                        "type": "prohibition",
                        "strength": strength,
                        "markers": [marker],
                        "affected_party": self._identify_affected_party(sentence)
                    }
        
        # Check for obligations
        for strength, markers in self.markers["obligation"].items():
            for marker in markers:
                if marker in sentence_lower:
                    return {
                        "type": "obligation",
                        "strength": strength,
                        "markers": [marker],
                        "affected_party": self._identify_affected_party(sentence)
                    }
        
        # Check for rights
        for strength, markers in self.markers["right"].items():
            for marker in markers:
                if marker in sentence_lower:
                    return {
                        "type": "right",
                        "strength": strength,
                        "markers": [marker],
                        "affected_party": self._identify_affected_party(sentence)
                    }
        
        # No clear classification
        return {
            "type": "neutral",
            "strength": None,
            "markers": [],
            "affected_party": "unknown"
        }
    
    def _identify_affected_party(self, sentence: str) -> str:
        """Identify which party is affected by the obligation/right"""
        sentence_lower = sentence.lower()
        
        for role, indicators in self.party_roles.items():
            for indicator in indicators:
                if indicator in sentence_lower:
                    return role
        
        return "unspecified"
    
    def get_one_sided_terms(self, analysis_result: Dict) -> Dict:
        """
        Identify potentially one-sided terms in the contract
        
        Returns:
            Dict with analysis of one-sided terms
        """
        one_sided = {
            "first_party_favored": [],
            "second_party_favored": [],
            "concerns": []
        }
        
        # Check for exclusive rights
        for right in analysis_result.get("rights", []):
            if right["strength"] == "exclusive":
                if right["affected_party"] == "first_party":
                    one_sided["first_party_favored"].append({
                        "type": "exclusive_right",
                        "text": right["text"]
                    })
                    one_sided["concerns"].append(
                        f"Exclusive right favoring first party: {right['text'][:100]}..."
                    )
        
        # Check for strong prohibitions
        for prohibition in analysis_result.get("prohibitions", []):
            if prohibition["strength"] == "strong":
                if prohibition["affected_party"] == "second_party":
                    one_sided["first_party_favored"].append({
                        "type": "strong_prohibition",
                        "text": prohibition["text"]
                    })
        
        # Calculate balance score
        first_party_score = len(one_sided["first_party_favored"])
        second_party_score = len(one_sided["second_party_favored"])
        
        if first_party_score > second_party_score + 3:
            one_sided["assessment"] = "Contract appears to favor the first party (Company/Employer/Lessor)"
        elif second_party_score > first_party_score + 3:
            one_sided["assessment"] = "Contract appears to favor the second party"
        else:
            one_sided["assessment"] = "Contract appears relatively balanced"
        
        return one_sided
