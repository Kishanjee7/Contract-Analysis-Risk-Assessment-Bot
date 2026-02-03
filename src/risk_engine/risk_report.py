"""
Risk Report Generator
Generates structured risk reports for contracts
"""
from typing import Dict, List
from datetime import datetime


class RiskReportGenerator:
    """Generate comprehensive risk reports"""
    
    def __init__(self):
        pass
    
    def generate_report(self, 
                       contract_info: Dict,
                       risk_score: Dict,
                       clause_detections: Dict,
                       compliance: Dict,
                       entities: Dict,
                       obligations: Dict) -> Dict:
        """
        Generate a comprehensive risk analysis report
        
        Args:
            contract_info: Basic contract information
            risk_score: Risk scoring results
            clause_detections: Clause detection results
            compliance: Compliance check results
            entities: Extracted entities
            obligations: Obligation analysis results
            
        Returns:
            Complete report dictionary
        """
        report = {
            "report_id": self._generate_report_id(),
            "generated_at": datetime.now().isoformat(),
            "contract_info": self._format_contract_info(contract_info),
            "executive_summary": self._generate_executive_summary(
                risk_score, clause_detections, compliance
            ),
            "risk_assessment": self._format_risk_assessment(risk_score, clause_detections),
            "key_findings": self._compile_key_findings(
                clause_detections, risk_score, obligations
            ),
            "compliance_status": self._format_compliance(compliance),
            "extracted_terms": self._format_extracted_terms(entities),
            "obligations_summary": self._format_obligations(obligations),
            "recommendations": self._generate_recommendations(
                risk_score, clause_detections, compliance
            ),
            "next_steps": self._generate_next_steps(risk_score)
        }
        
        return report
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        return f"CR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _format_contract_info(self, info: Dict) -> Dict:
        """Format basic contract information"""
        return {
            "file_name": info.get("file_name", "Unknown"),
            "contract_type": info.get("contract_type", "Unknown"),
            "language": info.get("language", "en"),
            "page_count": info.get("page_count", 0),
            "word_count": info.get("word_count", 0)
        }
    
    def _generate_executive_summary(self, 
                                   risk_score: Dict,
                                   clause_detections: Dict,
                                   compliance: Dict) -> Dict:
        """Generate executive summary for quick overview"""
        composite_score = risk_score.get("composite_score", 0)
        compliance_score = compliance.get("compliance_score", 0)
        
        # Count high-risk items
        high_risk_count = sum(
            1 for detection in clause_detections.values()
            if detection.get("found") and any(
                f.get("risk_level") == "high" 
                for f in detection.get("findings", [])
            )
        )
        
        # Determine overall status
        if composite_score >= 7 or high_risk_count >= 3:
            status = "HIGH_RISK"
            status_color = "red"
            recommendation = "Recommend professional legal review before signing"
        elif composite_score >= 5 or high_risk_count >= 1:
            status = "MODERATE_RISK"
            status_color = "yellow"
            recommendation = "Review flagged clauses carefully, consider negotiating terms"
        else:
            status = "LOW_RISK"
            status_color = "green"
            recommendation = "Contract appears balanced, standard review sufficient"
        
        return {
            "overall_status": status,
            "status_color": status_color,
            "risk_score": composite_score,
            "compliance_score": compliance_score,
            "high_risk_items": high_risk_count,
            "primary_recommendation": recommendation,
            "one_liner": self._get_one_liner(composite_score, high_risk_count)
        }
    
    def _get_one_liner(self, risk_score: float, high_risk_count: int) -> str:
        """Generate a one-line summary"""
        if risk_score >= 7:
            return f"[HIGH RISK] Contract has {high_risk_count} high-risk clauses requiring immediate attention"
        elif risk_score >= 5:
            return f"[MODERATE RISK] Contract has some concerning terms - review recommended"
        else:
            return "[LOW RISK] Contract terms appear generally balanced and fair"
    
    def _format_risk_assessment(self, risk_score: Dict, clause_detections: Dict) -> Dict:
        """Format detailed risk assessment"""
        return {
            "composite_score": risk_score.get("composite_score", 0),
            "risk_level": risk_score.get("risk_level", "unknown"),
            "severity_distribution": risk_score.get("severity_distribution", {}),
            "clause_scores": risk_score.get("clause_scores", [])[:10],  # Top 10
            "sme_concerns": risk_score.get("sme_concerns", []),
            "detected_clauses": {
                name: {
                    "found": data.get("found", False),
                    "count": data.get("count", 0),
                    "recommendation": data.get("recommendation")
                }
                for name, data in clause_detections.items()
            }
        }
    
    def _compile_key_findings(self, 
                             clause_detections: Dict,
                             risk_score: Dict,
                             obligations: Dict) -> List[Dict]:
        """Compile key findings from all analyses"""
        findings = []
        priority = 1
        
        # High-risk clause findings
        for clause_type, detection in clause_detections.items():
            if detection.get("found"):
                for finding in detection.get("findings", [])[:2]:  # Top 2 per type
                    if finding.get("risk_level") == "high":
                        findings.append({
                            "priority": priority,
                            "category": clause_type.replace("_", " ").title(),
                            "severity": "HIGH",
                            "description": finding.get("text", "")[:100],
                            "context": finding.get("context", "")[:200],
                            "recommendation": detection.get("recommendation")
                        })
                        priority += 1
        
        # One-sided terms
        one_sided = obligations.get("one_sided_terms", {})
        if one_sided.get("concerns"):
            for concern in one_sided["concerns"][:3]:
                findings.append({
                    "priority": priority,
                    "category": "One-Sided Terms",
                    "severity": "MEDIUM",
                    "description": concern,
                    "recommendation": "Consider negotiating for more balanced terms"
                })
                priority += 1
        
        # Sort by priority and limit
        findings.sort(key=lambda x: x["priority"])
        return findings[:10]
    
    def _format_compliance(self, compliance: Dict) -> Dict:
        """Format compliance check results"""
        return {
            "score": compliance.get("compliance_score", 0),
            "issues": compliance.get("issues", []),
            "warnings": compliance.get("warnings", []),
            "recommendations": compliance.get("recommendations", [])
        }
    
    def _format_extracted_terms(self, entities: Dict) -> Dict:
        """Format extracted contract terms"""
        return {
            "parties": [
                {"name": p.get("name"), "type": p.get("type")}
                for p in entities.get("parties", [])
            ],
            "dates": [
                d.get("raw") for d in entities.get("dates", [])
            ],
            "amounts": [
                {"value": a.get("value"), "currency": a.get("currency")}
                for a in entities.get("amounts", [])
            ],
            "durations": [
                d.get("raw") for d in entities.get("durations", [])
            ],
            "jurisdictions": entities.get("jurisdictions", [])
        }
    
    def _format_obligations(self, obligations: Dict) -> Dict:
        """Format obligation analysis"""
        return {
            "total_obligations": obligations.get("summary", {}).get("total_obligations", 0),
            "total_rights": obligations.get("summary", {}).get("total_rights", 0),
            "total_prohibitions": obligations.get("summary", {}).get("total_prohibitions", 0),
            "strong_obligations": obligations.get("summary", {}).get("strong_obligations", 0),
            "key_obligations": [
                o.get("text", "")[:200] 
                for o in obligations.get("obligations", [])[:5]
            ],
            "key_prohibitions": [
                p.get("text", "")[:200]
                for p in obligations.get("prohibitions", [])[:5]
            ]
        }
    
    def _generate_recommendations(self,
                                  risk_score: Dict,
                                  clause_detections: Dict,
                                  compliance: Dict) -> List[Dict]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # From clause detections
        for clause_type, detection in clause_detections.items():
            if detection.get("found") and detection.get("recommendation"):
                recommendations.append({
                    "category": clause_type.replace("_", " ").title(),
                    "action": detection["recommendation"],
                    "priority": "high" if detection.get("has_broad_indemnity") or 
                               detection.get("has_full_transfer") else "medium"
                })
        
        # From compliance
        for rec in compliance.get("recommendations", []):
            recommendations.append({
                "category": "Compliance",
                "action": rec,
                "priority": "medium"
            })
        
        # SME-specific
        for concern in risk_score.get("sme_concerns", []):
            if concern.get("type") == "cash_flow_risk":
                recommendations.append({
                    "category": "Cash Flow",
                    "action": "Negotiate for shorter payment terms (Net 30 or Net 45)",
                    "priority": "high"
                })
        
        return recommendations[:10]
    
    def _generate_next_steps(self, risk_score: Dict) -> List[str]:
        """Generate recommended next steps"""
        score = risk_score.get("composite_score", 0)
        
        if score >= 7:
            return [
                "1. Do NOT sign this contract without professional legal review",
                "2. Identify the top 3 high-risk clauses for negotiation",
                "3. Prepare counter-proposals for risky terms",
                "4. Consider seeking alternative vendors/partners if negotiation fails",
                "5. Document all negotiations and changes"
            ]
        elif score >= 5:
            return [
                "1. Review all flagged clauses carefully",
                "2. Create a list of terms you want to negotiate",
                "3. Discuss concerns with the other party",
                "4. Consider limited legal review for high-risk clauses",
                "5. Ensure all agreed changes are documented in writing"
            ]
        else:
            return [
                "1. Perform a final read-through of the contract",
                "2. Verify all details (names, dates, amounts) are correct",
                "3. Ensure you have copies of all related documents",
                "4. Sign and retain a copy for your records",
                "5. Set reminders for key dates (renewals, reviews)"
            ]
    
    def to_plain_text(self, report: Dict) -> str:
        """Convert report to plain text format"""
        lines = []
        lines.append("=" * 60)
        lines.append("CONTRACT RISK ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"\nReport ID: {report['report_id']}")
        lines.append(f"Generated: {report['generated_at']}")
        
        # Executive Summary
        summary = report.get("executive_summary", {})
        lines.append(f"\n{'='*40}")
        lines.append("EXECUTIVE SUMMARY")
        lines.append(f"{'='*40}")
        lines.append(f"Status: {summary.get('overall_status', 'Unknown')}")
        lines.append(f"Risk Score: {summary.get('risk_score', 0)}/10")
        lines.append(f"Compliance Score: {summary.get('compliance_score', 0)}%")
        lines.append(f"\n{summary.get('one_liner', '')}")
        lines.append(f"\nRecommendation: {summary.get('primary_recommendation', '')}")
        
        # Key Findings
        findings = report.get("key_findings", [])
        if findings:
            lines.append(f"\n{'='*40}")
            lines.append("KEY FINDINGS")
            lines.append(f"{'='*40}")
            for finding in findings:
                lines.append(f"\n[{finding.get('severity')}] {finding.get('category')}")
                lines.append(f"  {finding.get('description', '')}")
                if finding.get('recommendation'):
                    lines.append(f"  → {finding['recommendation']}")
        
        # Next Steps
        next_steps = report.get("next_steps", [])
        if next_steps:
            lines.append(f"\n{'='*40}")
            lines.append("RECOMMENDED NEXT STEPS")
            lines.append(f"{'='*40}")
            for step in next_steps:
                lines.append(step)
        
        return "\n".join(lines)
