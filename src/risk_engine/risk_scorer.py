"""
Risk Scorer
Calculates clause-level and contract-level risk scores
"""
from typing import Dict, List, Tuple
import re


class RiskScorer:
    """Calculate risk scores for contract clauses and overall contract"""
    
    def __init__(self):
        # Risk indicators with severity weights
        self.risk_indicators = {
            "critical": {  # Weight: 3
                "patterns": [
                    r"unlimited\s+liability",
                    r"waive\s+all\s+rights",
                    r"indemnify.*against\s+all\s+claims",
                    r"sole\s+and\s+absolute\s+discretion",
                    r"irrevocable\s+(?:and\s+)?unconditional",
                    r"perpetual\s+(?:and\s+)?irrevocable",
                    r"assign\s+all\s+(?:rights|intellectual\s+property)",
                    r"without\s+any\s+limitation\s+whatsoever",
                ],
                "weight": 3.0
            },
            "high": {  # Weight: 2
                "patterns": [
                    r"penalty\s+(?:of|amounting)",
                    r"liquidated\s+damages",
                    r"terminate\s+(?:immediately|without\s+notice|without\s+cause)",
                    r"unilateral\s+(?:termination|modification)",
                    r"non-compete(?:tion)?\s+(?:clause|covenant|agreement)",
                    r"automatic\s+renewal",
                    r"lock-?in\s+period",
                    r"exclusive\s+(?:rights|jurisdiction)",
                    r"forfeit(?:ure)?",
                    r"waiver\s+of\s+(?:rights|claims)",
                ],
                "weight": 2.0
            },
            "medium": {  # Weight: 1
                "patterns": [
                    r"arbitration\s+(?:clause|shall\s+be)",
                    r"confidential(?:ity)?\s+(?:clause|agreement|obligations)",
                    r"intellectual\s+property\s+(?:rights|transfer)",
                    r"notice\s+period\s+of\s+(?:less\s+than\s+)?\d+\s+days",
                    r"governing\s+law",
                    r"limitation\s+of\s+liability",
                    r"force\s+majeure",
                    r"assignment\s+(?:clause|rights)",
                    r"amendment\s+(?:clause|by\s+mutual)",
                ],
                "weight": 1.0
            },
            "low": {  # Weight: 0.5
                "patterns": [
                    r"reasonable\s+(?:efforts|time|notice)",
                    r"commercially\s+reasonable",
                    r"good\s+faith",
                    r"best\s+efforts",
                    r"material\s+breach",
                ],
                "weight": 0.5
            }
        }
        
        # SME-specific concerns (higher weight for small businesses)
        self.sme_concerns = {
            "cash_flow_risk": [
                r"payment\s+(?:within|after)\s+(?:6[0-9]|[7-9][0-9]|[1-9][0-9]{2,})\s+days",
                r"net\s+(?:6[0-9]|[7-9][0-9]|[1-9][0-9]{2,})",
                r"advance\s+payment\s+of\s+\d+%",
            ],
            "resource_risk": [
                r"dedicated\s+(?:team|resources|personnel)",
                r"minimum\s+(?:order|commitment|volume)",
                r"exclusive\s+(?:supply|service)",
            ],
            "exit_risk": [
                r"termination\s+fee",
                r"early\s+termination\s+penalty",
                r"exit\s+(?:fee|cost|charges)",
            ]
        }
    
    def score_clause(self, clause_text: str) -> Dict:
        """
        Calculate risk score for a single clause
        
        Args:
            clause_text: Text of the clause
            
        Returns:
            Dict with risk score and details
        """
        text_lower = clause_text.lower()
        findings = []
        total_weight = 0.0
        
        # Check all risk indicators
        for severity, config in self.risk_indicators.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        "pattern": match if isinstance(match, str) else pattern,
                        "severity": severity,
                        "weight": config["weight"]
                    })
                    total_weight += config["weight"]
        
        # Check SME-specific concerns
        sme_findings = []
        for concern_type, patterns in self.sme_concerns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    sme_findings.append({
                        "type": concern_type,
                        "pattern": pattern
                    })
                    total_weight += 1.5  # SME concerns have higher impact
        
        # Calculate normalized score (0-10)
        raw_score = min(10.0, total_weight)
        
        return {
            "score": round(raw_score, 1),
            "risk_level": self._get_risk_level(raw_score),
            "findings": findings,
            "sme_concerns": sme_findings,
            "requires_attention": raw_score >= 5.0
        }
    
    def score_contract(self, clauses: List[Dict]) -> Dict:
        """
        Calculate overall contract risk score
        
        Args:
            clauses: List of clause dictionaries with text
            
        Returns:
            Dict with contract-level risk assessment
        """
        clause_scores = []
        all_findings = []
        all_sme_concerns = []
        critical_clauses = []
        high_risk_clauses = []
        
        for clause in clauses:
            text = clause.get("text", "")
            clause_result = self.score_clause(text)
            
            clause_scores.append({
                "clause_number": clause.get("clause_number", ""),
                "heading": clause.get("heading", ""),
                "score": clause_result["score"],
                "risk_level": clause_result["risk_level"],
                "findings": clause_result["findings"]
            })
            
            all_findings.extend(clause_result["findings"])
            all_sme_concerns.extend(clause_result["sme_concerns"])
            
            if clause_result["score"] >= 7:
                critical_clauses.append(clause)
            elif clause_result["score"] >= 5:
                high_risk_clauses.append(clause)
        
        # Calculate composite score
        if clause_scores:
            avg_score = sum(c["score"] for c in clause_scores) / len(clause_scores)
            max_score = max(c["score"] for c in clause_scores)
            # Weighted: 40% average, 60% max (worst clause matters more)
            composite_score = (avg_score * 0.4) + (max_score * 0.6)
        else:
            composite_score = 0.0
        
        # Severity distribution
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in all_findings:
            severity = finding.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "composite_score": round(composite_score, 1),
            "risk_level": self._get_risk_level(composite_score),
            "clause_scores": clause_scores,
            "severity_distribution": severity_counts,
            "critical_clauses_count": len(critical_clauses),
            "high_risk_clauses_count": len(high_risk_clauses),
            "sme_concerns": all_sme_concerns,
            "total_findings": len(all_findings),
            "recommendation": self._get_recommendation(composite_score, severity_counts)
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score <= 3:
            return "low"
        elif score <= 6:
            return "medium"
        else:
            return "high"
    
    def _get_recommendation(self, score: float, severity_counts: Dict) -> str:
        """Generate recommendation based on score and findings"""
        if score >= 7:
            return ("[HIGH RISK] This contract contains significant risks. "
                   "We strongly recommend legal review before signing. "
                   "Consider negotiating terms or seeking alternatives.")
        elif score >= 5:
            return ("[MODERATE RISK] This contract has some concerning clauses. "
                   "Review highlighted sections carefully and consider negotiating "
                   "modifications to high-risk terms.")
        elif score >= 3:
            return ("[LOW-MODERATE RISK] Contract has some standard risk clauses. "
                   "Review the flagged items but overall risk is manageable.")
        else:
            return ("[LOW RISK] Contract appears to have balanced terms. "
                   "Standard review recommended but no major concerns identified.")
    
    def get_risk_summary_for_sme(self, contract_score: Dict) -> Dict:
        """Generate SME-friendly risk summary"""
        score = contract_score["composite_score"]
        
        summary = {
            "overall_assessment": "",
            "key_concerns": [],
            "action_items": [],
            "negotiation_points": []
        }
        
        # Overall assessment
        if score >= 7:
            summary["overall_assessment"] = (
                "[HIGH RISK] This contract poses HIGH RISK for your business. "
                "Several clauses could significantly impact your operations or finances."
            )
        elif score >= 5:
            summary["overall_assessment"] = (
                "[MODERATE RISK] This contract has MODERATE RISK. "
                "Some terms need careful consideration before signing."
            )
        else:
            summary["overall_assessment"] = (
                "[LOW RISK] This contract appears to have LOW RISK. "
                "Terms are generally fair and balanced."
            )
        
        # Key concerns from SME-specific analysis
        sme_concerns = contract_score.get("sme_concerns", [])
        for concern in sme_concerns:
            if concern["type"] == "cash_flow_risk":
                summary["key_concerns"].append(
                    "Long payment terms may strain your cash flow"
                )
                summary["action_items"].append(
                    "Negotiate for shorter payment terms (Net 30 or Net 45)"
                )
            elif concern["type"] == "resource_risk":
                summary["key_concerns"].append(
                    "Contract may require dedicated resources"
                )
            elif concern["type"] == "exit_risk":
                summary["key_concerns"].append(
                    "High exit costs or termination penalties"
                )
                summary["action_items"].append(
                    "Negotiate for reasonable termination terms"
                )
        
        # Add negotiation points from critical clauses
        if contract_score.get("critical_clauses_count", 0) > 0:
            summary["negotiation_points"].append(
                "Review and negotiate critical clauses before signing"
            )
        
        return summary
