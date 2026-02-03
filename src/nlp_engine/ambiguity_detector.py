"""
Ambiguity Detector
Identifies ambiguous, vague, or unclear language in contracts
"""
import re
from typing import Dict, List


class AmbiguityDetector:
    """Detect ambiguous and unclear language in contract text"""
    
    def __init__(self):
        # Vague terms that may lead to interpretation disputes
        self.vague_terms = {
            "high_ambiguity": [
                "reasonable", "reasonably", "appropriate", "appropriately",
                "adequate", "adequately", "sufficient", "sufficiently",
                "material", "materially", "substantial", "substantially",
                "promptly", "timely", "as soon as possible", "in due course",
                "best efforts", "commercially reasonable efforts",
                "good faith", "fair", "fairly"
            ],
            "medium_ambiguity": [
                "may", "might", "could", "possibly", "potentially",
                "generally", "usually", "typically", "normally",
                "including but not limited to", "such as", "for example",
                "or otherwise", "and/or", "etc", "et cetera",
                "from time to time", "as needed", "as required",
                "similar", "comparable", "equivalent"
            ],
            "low_ambiguity": [
                "approximately", "about", "around", "roughly",
                "more or less", "up to", "at least", "no less than"
            ]
        }
        
        # Patterns that indicate potential ambiguity
        self.ambiguity_patterns = [
            (r"at\s+(?:the|its)\s+(?:sole\s+)?discretion", "Discretionary clause - outcome depends on one party's judgment"),
            (r"to\s+be\s+determined\s+(?:later|subsequently)?", "Undefined terms requiring future specification"),
            (r"as\s+(?:may\s+be\s+)?(?:mutually\s+)?agreed", "Requires future agreement - terms not fixed"),
            (r"(?:any|all)\s+other\s+(?:\w+\s+)?(?:matters?|issues?|items?)", "Catch-all provision - scope unclear"),
            (r"(?:any|all)\s+(?:relevant|applicable|related)", "Broad scope reference"),
            (r"(?:customary|standard|normal)\s+(?:practice|procedure)", "Reference to undefined standard"),
            (r"without\s+limitation", "Non-exhaustive list"),
            (r"whatsoever", "Extremely broad scope"),
        ]
        
        # Missing essential terms indicators
        self.essential_terms = {
            "payment": ["payment", "compensation", "fee", "price", "cost", "amount"],
            "timeline": ["date", "day", "month", "year", "period", "term", "duration"],
            "deliverables": ["deliver", "provide", "perform", "complete", "service"],
            "termination": ["terminate", "end", "cancel", "expire"],
            "liability": ["liability", "responsible", "liable", "indemnify"]
        }
    
    def detect(self, text: str) -> Dict:
        """
        Detect ambiguities in contract text
        
        Args:
            text: Contract text to analyze
            
        Returns:
            Dict with ambiguity findings
        """
        findings = {
            "vague_terms": self._find_vague_terms(text),
            "ambiguous_patterns": self._find_ambiguous_patterns(text),
            "undefined_references": self._find_undefined_references(text),
            "missing_specifics": self._check_missing_specifics(text)
        }
        
        # Calculate overall ambiguity score
        findings["ambiguity_score"] = self._calculate_score(findings, len(text))
        findings["risk_level"] = self._get_risk_level(findings["ambiguity_score"])
        findings["recommendations"] = self._generate_recommendations(findings)
        
        return findings
    
    def _find_vague_terms(self, text: str) -> List[Dict]:
        """Find vague terms in the text"""
        text_lower = text.lower()
        findings = []
        
        for severity, terms in self.vague_terms.items():
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                
                if matches:
                    for match in matches:
                        context = self._get_context(text, match.start(), match.end())
                        findings.append({
                            "term": term,
                            "severity": severity,
                            "context": context,
                            "position": match.start()
                        })
        
        return findings
    
    def _find_ambiguous_patterns(self, text: str) -> List[Dict]:
        """Find ambiguous patterns in the text"""
        findings = []
        
        for pattern, description in self.ambiguity_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end())
                findings.append({
                    "pattern": match.group(0),
                    "description": description,
                    "context": context,
                    "position": match.start()
                })
        
        return findings
    
    def _find_undefined_references(self, text: str) -> List[Dict]:
        """Find references to undefined terms or documents"""
        findings = []
        
        # Look for "as defined in/by" patterns without clear reference
        undefined_patterns = [
            r"as\s+defined\s+(?:in|by)\s+(?:the\s+)?(\w+)",
            r"pursuant\s+to\s+(?:the\s+)?(\w+)",
            r"in\s+accordance\s+with\s+(?:the\s+)?(\w+)",
            r"subject\s+to\s+(?:the\s+)?(\w+)",
        ]
        
        for pattern in undefined_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                reference = match.group(1)
                # Check if it's a defined term (appears in quotes or caps elsewhere)
                if not self._is_defined_term(text, reference):
                    context = self._get_context(text, match.start(), match.end())
                    findings.append({
                        "reference": reference,
                        "full_match": match.group(0),
                        "context": context
                    })
        
        return findings
    
    def _is_defined_term(self, text: str, term: str) -> bool:
        """Check if a term is defined somewhere in the contract"""
        # Look for definition patterns
        definition_patterns = [
            rf'"{re.escape(term)}"',
            rf"'{re.escape(term)}'",
            rf'"{re.escape(term)}"\s+means',
            rf"'{re.escape(term)}'\s+means",
            rf'\b{re.escape(term)}\b\s+(?:shall\s+)?mean',
        ]
        
        for pattern in definition_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _check_missing_specifics(self, text: str) -> Dict:
        """Check for potentially missing specific terms"""
        text_lower = text.lower()
        missing = {}
        
        for category, indicators in self.essential_terms.items():
            found = any(ind in text_lower for ind in indicators)
            if not found:
                missing[category] = f"No clear {category} terms found in contract"
        
        # Check for specific numeric requirements
        specificity_checks = {
            "amounts_specified": bool(re.search(r'(?:Rs\.?|INR|₹|\$)\s*[\d,]+', text)),
            "dates_specified": bool(re.search(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}', text)),
            "durations_specified": bool(re.search(r'\d+\s*(?:days?|months?|years?)', text))
        }
        
        return {
            "missing_categories": missing,
            "specificity_checks": specificity_checks
        }
    
    def _calculate_score(self, findings: Dict, text_length: int) -> float:
        """Calculate overall ambiguity score (0-10)"""
        score = 0.0
        
        # Weight vague terms
        vague_terms = findings.get("vague_terms", [])
        high_count = len([v for v in vague_terms if v["severity"] == "high_ambiguity"])
        medium_count = len([v for v in vague_terms if v["severity"] == "medium_ambiguity"])
        
        score += min(3.0, high_count * 0.5)
        score += min(2.0, medium_count * 0.2)
        
        # Weight ambiguous patterns
        patterns_count = len(findings.get("ambiguous_patterns", []))
        score += min(2.0, patterns_count * 0.4)
        
        # Weight undefined references
        undefined_count = len(findings.get("undefined_references", []))
        score += min(1.5, undefined_count * 0.3)
        
        # Weight missing specifics
        missing = findings.get("missing_specifics", {}).get("missing_categories", {})
        score += len(missing) * 0.5
        
        return min(10.0, round(score, 1))
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score <= 3:
            return "low"
        elif score <= 6:
            return "medium"
        else:
            return "high"
    
    def _generate_recommendations(self, findings: Dict) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        vague_terms = findings.get("vague_terms", [])
        high_severity = [v for v in vague_terms if v["severity"] == "high_ambiguity"]
        
        if high_severity:
            recommendations.append(
                f"Define specific criteria for vague terms like '{high_severity[0]['term']}' "
                "to avoid interpretation disputes."
            )
        
        patterns = findings.get("ambiguous_patterns", [])
        if patterns:
            recommendations.append(
                "Replace discretionary clauses with objective criteria where possible."
            )
        
        missing = findings.get("missing_specifics", {}).get("missing_categories", {})
        for category in missing:
            recommendations.append(f"Add specific {category} terms to the contract.")
        
        if not findings.get("missing_specifics", {}).get("specificity_checks", {}).get("dates_specified"):
            recommendations.append("Include specific dates for key milestones and deadlines.")
        
        return recommendations
    
    def _get_context(self, text: str, start: int, end: int, window: int = 75) -> str:
        """Get surrounding context for a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end].strip()
        
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."
        
        return context
