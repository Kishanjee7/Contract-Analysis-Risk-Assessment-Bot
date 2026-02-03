"""
Clause Detectors
Specialized detectors for specific risky clause types
"""
import re
from typing import Dict, List, Optional


class ClauseDetectors:
    """Detection of specific clause types that may pose risks"""
    
    def __init__(self):
        pass
    
    def detect_all(self, text: str) -> Dict:
        """
        Run all clause detectors on the text
        
        Returns:
            Dict with all detection results
        """
        return {
            "penalty_clauses": self.detect_penalty_clauses(text),
            "indemnity_clauses": self.detect_indemnity_clauses(text),
            "termination_clauses": self.detect_termination_clauses(text),
            "arbitration_clauses": self.detect_arbitration_clauses(text),
            "auto_renewal_clauses": self.detect_auto_renewal(text),
            "non_compete_clauses": self.detect_non_compete(text),
            "ip_transfer_clauses": self.detect_ip_transfer(text),
            "confidentiality_clauses": self.detect_confidentiality(text),
            "liability_caps": self.detect_liability_caps(text),
        }
    
    def detect_penalty_clauses(self, text: str) -> Dict:
        """Detect penalty and liquidated damages clauses"""
        patterns = [
            r"penalty\s+(?:of|amounting\s+to)\s+(?:Rs\.?|INR|₹)?\s*[\d,]+",
            r"liquidated\s+damages?\s+(?:of|amounting\s+to|equal\s+to)",
            r"forfeit(?:ure)?\s+of\s+(?:deposit|advance|amount)",
            r"damages?\s+(?:of|equal\s+to)\s+(?:\d+%|\d+\s+times)",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end())
                
                # Try to extract amount
                amount_match = re.search(r'(?:Rs\.?|INR|₹)?\s*([\d,]+)', context)
                amount = amount_match.group(1) if amount_match else None
                
                findings.append({
                    "type": "penalty",
                    "text": match.group(0),
                    "context": context,
                    "amount": amount,
                    "risk_level": "high"
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "recommendation": "Review penalty amounts and ensure they are proportionate to potential damages" if findings else None
        }
    
    def detect_indemnity_clauses(self, text: str) -> Dict:
        """Detect indemnification clauses and assess their scope"""
        patterns = [
            r"indemnif(?:y|ication|ies)\s+(?:and\s+)?(?:hold\s+harmless)?",
            r"hold\s+harmless\s+(?:and\s+)?indemnif",
            r"defend,?\s+indemnif(?:y|ication)",
        ]
        
        scope_indicators = {
            "broad": [
                r"all\s+claims",
                r"any\s+and\s+all",
                r"without\s+limitation",
                r"whatsoever",
                r"arising\s+out\s+of\s+or\s+relating\s+to",
            ],
            "narrow": [
                r"gross\s+negligence",
                r"willful\s+misconduct",
                r"material\s+breach",
                r"to\s+the\s+extent\s+caused\s+by",
            ]
        }
        
        findings = []
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=200)
                
                # Assess scope
                scope = "moderate"
                for indicator in scope_indicators["broad"]:
                    if re.search(indicator, context, re.IGNORECASE):
                        scope = "broad"
                        break
                for indicator in scope_indicators["narrow"]:
                    if re.search(indicator, context, re.IGNORECASE):
                        scope = "narrow"
                        break
                
                findings.append({
                    "type": "indemnity",
                    "text": match.group(0),
                    "context": context,
                    "scope": scope,
                    "risk_level": "high" if scope == "broad" else "medium"
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "has_broad_indemnity": any(f["scope"] == "broad" for f in findings),
            "recommendation": "Negotiate to limit indemnification scope and add caps" if findings else None
        }
    
    def detect_termination_clauses(self, text: str) -> Dict:
        """Detect termination clauses and assess fairness"""
        patterns = {
            "unilateral": [
                r"(?:party|company|employer)\s+may\s+terminate\s+(?:this\s+)?(?:agreement|contract)\s+(?:at\s+)?(?:any\s+time|without\s+cause)",
                r"terminate\s+(?:immediately|without\s+notice|with\s+immediate\s+effect)",
                r"sole\s+discretion\s+to\s+terminate",
            ],
            "mutual": [
                r"either\s+party\s+may\s+terminate",
                r"mutual\s+(?:agreement|consent)\s+to\s+terminate",
                r"both\s+parties\s+(?:may|agree\s+to)\s+terminate",
            ],
            "for_cause": [
                r"terminate\s+(?:for\s+)?(?:cause|breach|default)",
                r"material\s+breach.*terminate",
                r"cure\s+period\s+of\s+\d+\s+days",
            ]
        }
        
        findings = {
            "unilateral": [],
            "mutual": [],
            "for_cause": []
        }
        
        for term_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                for match in matches:
                    context = self._get_context(text, match.start(), match.end(), window=150)
                    
                    # Extract notice period if mentioned
                    notice_match = re.search(r'(\d+)\s*(?:days?|months?|weeks?)\s*(?:prior\s+)?notice', context, re.IGNORECASE)
                    notice_period = notice_match.group(0) if notice_match else None
                    
                    findings[term_type].append({
                        "text": match.group(0),
                        "context": context,
                        "notice_period": notice_period
                    })
        
        # Assess balance
        is_balanced = (
            len(findings["mutual"]) > 0 or 
            (len(findings["unilateral"]) == 0) or
            all(f.get("notice_period") for f in findings["unilateral"])
        )
        
        return {
            "found": any(len(v) > 0 for v in findings.values()),
            "findings": findings,
            "has_unilateral_termination": len(findings["unilateral"]) > 0,
            "is_balanced": is_balanced,
            "recommendation": "Ensure termination rights are mutual or include adequate notice periods" if findings["unilateral"] else None
        }
    
    def detect_arbitration_clauses(self, text: str) -> Dict:
        """Detect arbitration and dispute resolution clauses"""
        patterns = [
            r"arbitration\s+(?:clause|proceedings?|shall\s+be)",
            r"submit(?:ted)?\s+to\s+arbitration",
            r"(?:SIAC|ICC|LCIA|AAA)\s+(?:rules|arbitration)",
            r"Arbitration\s+and\s+Conciliation\s+Act",
            r"seat\s+of\s+(?:the\s+)?arbitration",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=200)
                
                # Extract seat/venue
                seat_match = re.search(r'seat\s+(?:of\s+(?:the\s+)?arbitration\s+)?(?:shall\s+be\s+)?(?:at\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', context)
                seat = seat_match.group(1) if seat_match else None
                
                # Extract governing rules
                rules_match = re.search(r'(SIAC|ICC|LCIA|AAA|Indian\s+Arbitration)', context, re.IGNORECASE)
                rules = rules_match.group(1) if rules_match else None
                
                findings.append({
                    "text": match.group(0),
                    "context": context,
                    "seat": seat,
                    "rules": rules
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "recommendation": "Verify arbitration seat and rules are convenient for your business" if findings else None
        }
    
    def detect_auto_renewal(self, text: str) -> Dict:
        """Detect automatic renewal and lock-in clauses"""
        patterns = [
            r"automatic(?:ally)?\s+renew(?:al|ed)?",
            r"auto-?renew(?:al)?",
            r"renew(?:ed)?\s+automatically",
            r"lock-?in\s+period\s+of\s+\d+",
            r"minimum\s+(?:term|period|commitment)\s+of\s+\d+",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=150)
                
                # Extract duration
                duration_match = re.search(r'(\d+)\s*(?:years?|months?|days?)', context)
                duration = duration_match.group(0) if duration_match else None
                
                # Check for opt-out notice
                opt_out_match = re.search(r'(\d+)\s*(?:days?|months?)\s*(?:prior\s+)?(?:written\s+)?notice', context)
                opt_out_notice = opt_out_match.group(0) if opt_out_match else None
                
                findings.append({
                    "text": match.group(0),
                    "context": context,
                    "duration": duration,
                    "opt_out_notice": opt_out_notice,
                    "risk_level": "high" if not opt_out_notice else "medium"
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "recommendation": "Set calendar reminders for renewal dates and negotiate opt-out terms" if findings else None
        }
    
    def detect_non_compete(self, text: str) -> Dict:
        """Detect non-compete and restrictive covenant clauses"""
        patterns = [
            r"non-?compete(?:tion)?\s+(?:clause|covenant|agreement|restriction)?",
            r"restrictive\s+covenant",
            r"shall\s+not\s+(?:directly\s+or\s+indirectly\s+)?(?:engage|compete|work|provide\s+services)",
            r"restraint\s+(?:of\s+)?trade",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=200)
                
                # Extract duration
                duration_match = re.search(r'(\d+)\s*(?:years?|months?)', context)
                duration = duration_match.group(0) if duration_match else None
                
                # Extract geographic scope
                geo_match = re.search(r'(?:within|throughout)\s+([A-Za-z\s,]+?)(?:\.|,|and)', context)
                geographic_scope = geo_match.group(1).strip() if geo_match else None
                
                findings.append({
                    "text": match.group(0),
                    "context": context,
                    "duration": duration,
                    "geographic_scope": geographic_scope,
                    "risk_level": "high"
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "recommendation": "Negotiate reasonable duration and geographic limits for non-compete" if findings else None
        }
    
    def detect_ip_transfer(self, text: str) -> Dict:
        """Detect intellectual property transfer clauses"""
        patterns = [
            r"(?:transfer|assign(?:ment)?|convey)\s+(?:of\s+)?(?:all\s+)?intellectual\s+property",
            r"intellectual\s+property\s+(?:rights?\s+)?(?:shall\s+)?(?:belong|vest)\s+(?:in|with)",
            r"work\s+(?:made\s+)?for\s+hire",
            r"assign\s+all\s+(?:right,?\s+title,?\s+and\s+interest)",
            r"(?:copyright|patent|trademark)\s+(?:shall\s+)?(?:belong|vest)",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=200)
                
                # Check if it's a full transfer or license
                is_full_transfer = not bool(re.search(r'license|non-?exclusive|limited', context, re.IGNORECASE))
                
                findings.append({
                    "text": match.group(0),
                    "context": context,
                    "is_full_transfer": is_full_transfer,
                    "risk_level": "high" if is_full_transfer else "medium"
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "has_full_transfer": any(f["is_full_transfer"] for f in findings),
            "recommendation": "Consider retaining license rights or limiting IP transfer scope" if findings else None
        }
    
    def detect_confidentiality(self, text: str) -> Dict:
        """Detect confidentiality and NDA clauses"""
        patterns = [
            r"confidential(?:ity)?\s+(?:information|agreement|obligation|clause)",
            r"non-?disclosure\s+(?:agreement|obligation)",
            r"proprietary\s+information",
            r"trade\s+secret",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=200)
                
                # Extract duration
                duration_match = re.search(r'(\d+)\s*(?:years?)', context)
                duration = duration_match.group(0) if duration_match else None
                
                findings.append({
                    "text": match.group(0),
                    "context": context,
                    "duration": duration
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "recommendation": "Ensure confidentiality requirements are mutual and have reasonable duration" if findings else None
        }
    
    def detect_liability_caps(self, text: str) -> Dict:
        """Detect limitation of liability clauses"""
        patterns = [
            r"limitation\s+(?:of\s+)?liability",
            r"(?:aggregate|total|maximum)\s+liability\s+(?:shall\s+)?(?:not\s+)?exceed",
            r"liability\s+(?:shall\s+be\s+)?limited\s+to",
            r"cap(?:ped)?\s+(?:at|to)\s+(?:Rs\.?|INR|₹|\$)?\s*[\d,]+",
        ]
        
        findings = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                context = self._get_context(text, match.start(), match.end(), window=200)
                
                # Extract cap amount
                amount_match = re.search(r'(?:Rs\.?|INR|₹|\$)\s*([\d,]+)', context)
                cap_amount = amount_match.group(1) if amount_match else None
                
                # Check for percentage-based cap
                pct_match = re.search(r'(\d+)%\s+of\s+(?:the\s+)?(?:contract|fees|amount)', context, re.IGNORECASE)
                pct_cap = pct_match.group(0) if pct_match else None
                
                findings.append({
                    "text": match.group(0),
                    "context": context,
                    "cap_amount": cap_amount,
                    "percentage_cap": pct_cap
                })
        
        return {
            "found": len(findings) > 0,
            "count": len(findings),
            "findings": findings,
            "has_cap": len(findings) > 0,
            "recommendation": "Verify liability cap is adequate for potential damages" if findings else "Consider negotiating a liability cap"
        }
    
    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Get surrounding context for a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end].strip()
        
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."
        
        return context
