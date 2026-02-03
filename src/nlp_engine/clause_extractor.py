"""
Clause Extractor
Extracts individual clauses and sub-clauses from contract text
"""
import re
from typing import Dict, List, Tuple, Optional


class ClauseExtractor:
    """Extract and categorize clauses from contract documents"""
    
    def __init__(self):
        # Common clause heading patterns
        self.clause_patterns = [
            # Numbered clauses: 1., 1.1, 1.1.1, etc.
            r'^(\d+(?:\.\d+)*)\s*[\.:\-]?\s*(.+)',
            # Article/Section format
            r'^(?:Article|Section|Clause)\s+(\d+(?:\.\d+)*)[\.:\-]?\s*(.+)',
            # Roman numerals
            r'^([IVXivx]+)\s*[\.:\-]\s*(.+)',
            # Alphabetic: a), b), (a), (b)
            r'^(?:\()?([a-z])\)?[\.:\-]?\s*(.+)',
        ]
        
        # Clause type indicators
        self.clause_type_indicators = {
            "definitions": ["definition", "definitions", "interpretation", "meanings"],
            "obligations": ["shall", "must", "agrees to", "undertakes to", "is required to", "will provide"],
            "rights": ["may", "is entitled to", "has the right to", "reserves the right"],
            "prohibitions": ["shall not", "must not", "may not", "is prohibited from", "cannot"],
            "payment_terms": ["payment", "fee", "compensation", "invoice", "remuneration", "salary"],
            "termination": ["termination", "terminate", "cancellation", "end of agreement"],
            "indemnity": ["indemnify", "indemnification", "hold harmless", "indemnity"],
            "confidentiality": ["confidential", "non-disclosure", "proprietary", "trade secret"],
            "intellectual_property": ["intellectual property", "ip rights", "copyright", "patent", "trademark"],
            "dispute_resolution": ["dispute", "arbitration", "mediation", "litigation", "jurisdiction"],
            "governing_law": ["governing law", "applicable law", "laws of", "jurisdiction"],
            "force_majeure": ["force majeure", "act of god", "unforeseeable", "beyond control"],
            "amendment": ["amendment", "modification", "variation", "change to this agreement"],
            "notice": ["notice", "notification", "written notice", "days notice"],
            "assignment": ["assignment", "assign", "transfer rights", "novation"],
            "entire_agreement": ["entire agreement", "whole agreement", "supersedes"],
            "severability": ["severability", "severable", "invalid provision"],
            "warranty": ["warranty", "warranties", "represents and warrants", "representation"]
        }
    
    def extract_clauses(self, text: str) -> List[Dict]:
        """
        Extract all clauses from contract text
        
        Args:
            text: Full contract text
            
        Returns:
            List of clause dictionaries
        """
        lines = text.split('\n')
        clauses = []
        current_clause = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try to match clause patterns
            clause_match = self._match_clause_pattern(line)
            
            if clause_match:
                # Save previous clause
                if current_clause:
                    current_clause["text"] = current_clause["text"].strip()
                    current_clause["clause_type"] = self._identify_clause_type(current_clause["text"])
                    clauses.append(current_clause)
                
                # Start new clause
                current_clause = {
                    "clause_number": clause_match["number"],
                    "heading": clause_match["heading"],
                    "text": line,
                    "start_line": i + 1,
                    "level": clause_match["level"]
                }
            elif current_clause:
                # Continue current clause
                current_clause["text"] += "\n" + line
        
        # Don't forget the last clause
        if current_clause:
            current_clause["text"] = current_clause["text"].strip()
            current_clause["clause_type"] = self._identify_clause_type(current_clause["text"])
            clauses.append(current_clause)
        
        # If no structured clauses found, split by paragraphs
        if not clauses:
            clauses = self._extract_by_paragraphs(text)
        
        return clauses
    
    def _match_clause_pattern(self, line: str) -> Optional[Dict]:
        """Match line against clause patterns"""
        for pattern in self.clause_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                number = match.group(1)
                heading = match.group(2).strip() if len(match.groups()) > 1 else ""
                
                # Determine nesting level
                level = 1
                if re.match(r'\d+\.\d+\.\d+', number):
                    level = 3
                elif re.match(r'\d+\.\d+', number):
                    level = 2
                elif re.match(r'[a-z]', number, re.IGNORECASE):
                    level = 2
                
                return {
                    "number": number,
                    "heading": heading,
                    "level": level
                }
        
        # Check for ALL CAPS headings (common in contracts)
        if line.isupper() and len(line) > 3 and len(line) < 100:
            return {
                "number": "",
                "heading": line,
                "level": 1
            }
        
        return None
    
    def _identify_clause_type(self, text: str) -> str:
        """Identify the type of clause based on content"""
        text_lower = text.lower()
        
        max_matches = 0
        best_type = "general"
        
        for clause_type, indicators in self.clause_type_indicators.items():
            matches = sum(1 for ind in indicators if ind in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_type = clause_type
        
        return best_type
    
    def _extract_by_paragraphs(self, text: str) -> List[Dict]:
        """Fallback: extract clauses based on paragraph breaks"""
        paragraphs = re.split(r'\n\s*\n', text)
        clauses = []
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) > 50:  # Minimum meaningful paragraph
                clauses.append({
                    "clause_number": str(i + 1),
                    "heading": "",
                    "text": para,
                    "start_line": 0,
                    "level": 1,
                    "clause_type": self._identify_clause_type(para)
                })
        
        return clauses
    
    def get_clauses_by_type(self, clauses: List[Dict], clause_type: str) -> List[Dict]:
        """Filter clauses by type"""
        return [c for c in clauses if c.get("clause_type") == clause_type]
    
    def get_clause_summary(self, clauses: List[Dict]) -> Dict:
        """Generate summary statistics about extracted clauses"""
        type_counts = {}
        for clause in clauses:
            ctype = clause.get("clause_type", "general")
            type_counts[ctype] = type_counts.get(ctype, 0) + 1
        
        return {
            "total_clauses": len(clauses),
            "by_type": type_counts,
            "max_depth": max((c.get("level", 1) for c in clauses), default=1)
        }
