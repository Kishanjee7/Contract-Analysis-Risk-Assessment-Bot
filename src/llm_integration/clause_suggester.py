"""
Clause Suggester
Suggests alternative clauses for problematic terms
"""
from typing import Dict, List, Optional
from .llm_client import LLMClient
from .prompts import PromptTemplates


class ClauseSuggester:
    """Suggest alternative clauses to improve contract terms"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.prompts = PromptTemplates()
        
        # Standard alternative templates for common issues
        self.standard_alternatives = {
            "unlimited_indemnity": {
                "original_pattern": "indemnify.*all claims",
                "suggestion": "Limit indemnification to claims arising from the indemnifying party's gross negligence or willful misconduct, with a cap equal to the total contract value.",
                "reasoning": "Unlimited indemnification exposes you to potentially unlimited liability. Limiting it to gross negligence/willful misconduct and capping the amount provides reasonable protection for both parties."
            },
            "unilateral_termination": {
                "original_pattern": "terminate.*without cause.*without notice",
                "suggestion": "Either party may terminate this Agreement by providing thirty (30) days written notice to the other party.",
                "reasoning": "Unilateral termination without notice leaves you vulnerable. Requiring notice period gives time to prepare and find alternatives."
            },
            "broad_non_compete": {
                "original_pattern": "non-compete.*worldwide.*perpetual",
                "suggestion": "The non-compete restriction shall be limited to [specific geographic area] for a period of twelve (12) months following termination.",
                "reasoning": "Overly broad non-compete clauses may be unenforceable and unfairly restrictive. Reasonable time and geographic limits protect legitimate interests while allowing you to earn a living."
            },
            "ip_full_transfer": {
                "original_pattern": "assign all.*intellectual property",
                "suggestion": "Client shall receive a perpetual, non-exclusive license to use deliverables. Original intellectual property and tools developed prior to the engagement shall remain with the service provider.",
                "reasoning": "Full IP transfer may give away more than intended. Retaining background IP while licensing deliverables is a fairer arrangement."
            },
            "long_payment_terms": {
                "original_pattern": "payment.*90 days|net 90",
                "suggestion": "Payment shall be made within thirty (30) days of invoice date. Interest at 1.5% per month shall apply to overdue amounts.",
                "reasoning": "Long payment terms strain cash flow for small businesses. 30 days is standard and more manageable."
            },
            "one_sided_liability": {
                "original_pattern": "liability.*limited.*fees paid",
                "suggestion": "Neither party's liability shall exceed the total fees paid or payable under this Agreement during the twelve (12) months preceding the claim.",
                "reasoning": "Symmetric liability caps ensure both parties share risk equally."
            }
        }
    
    def suggest_alternative(self, 
                           clause_text: str, 
                           concerns: List[str] = None,
                           clause_type: str = None) -> Dict:
        """
        Suggest an alternative to a problematic clause
        
        Args:
            clause_text: Original clause text
            concerns: List of identified concerns
            clause_type: Type of clause
            
        Returns:
            Dict with suggestion and reasoning
        """
        # Try LLM first
        if self.llm.is_available():
            suggestion = self._suggest_with_llm(clause_text, concerns)
        else:
            suggestion = self._suggest_fallback(clause_text, concerns, clause_type)
        
        return {
            "original_clause": clause_text,
            "concerns": concerns or [],
            "suggestion": suggestion,
            "source": "ai" if self.llm.is_available() else "template"
        }
    
    def _suggest_with_llm(self, clause_text: str, concerns: List[str] = None) -> Dict:
        """Generate suggestion using LLM"""
        prompt = self.prompts.suggest_alternative(clause_text, concerns)
        response = self.llm.chat(prompt, self.prompts.CLAUSE_SUGGESTION_SYSTEM)
        
        return {
            "alternative_text": response,
            "source": "ai"
        }
    
    def _suggest_fallback(self, 
                         clause_text: str, 
                         concerns: List[str] = None,
                         clause_type: str = None) -> Dict:
        """Generate suggestion using templates"""
        text_lower = clause_text.lower()
        
        # Find matching template
        matched = None
        for issue_type, template in self.standard_alternatives.items():
            if any(keyword in text_lower for keyword in template["original_pattern"].split(".*")):
                matched = template
                break
        
        if matched:
            return {
                "alternative_text": matched["suggestion"],
                "reasoning": matched["reasoning"],
                "source": "template"
            }
        else:
            return {
                "alternative_text": self._generate_generic_suggestion(clause_text, concerns),
                "reasoning": "Generic suggestion based on identified concerns.",
                "source": "template"
            }
    
    def _generate_generic_suggestion(self, clause_text: str, concerns: List[str] = None) -> str:
        """Generate generic suggestion based on concerns"""
        suggestions = []
        
        if concerns:
            for concern in concerns:
                concern_lower = concern.lower()
                if "liability" in concern_lower:
                    suggestions.append("Consider adding a mutual liability cap")
                if "termination" in concern_lower:
                    suggestions.append("Request mutual termination rights with notice period")
                if "payment" in concern_lower:
                    suggestions.append("Negotiate for shorter payment terms (Net 30)")
        
        if not suggestions:
            suggestions.append("Consider negotiating for more balanced terms")
            suggestions.append("Request that rights and obligations be mutual")
        
        return "**Suggested improvements:**\n" + "\n".join(f"• {s}" for s in suggestions)
    
    def get_negotiation_points(self, clause_text: str, risk_level: str) -> List[str]:
        """
        Generate negotiation talking points for a clause
        
        Args:
            clause_text: The clause to negotiate
            risk_level: Current risk assessment (low/medium/high)
            
        Returns:
            List of negotiation points
        """
        text_lower = clause_text.lower()
        points = []
        
        if risk_level in ["medium", "high"]:
            # Analyze clause and generate points
            if "indemnify" in text_lower:
                points.extend([
                    "Request to limit indemnification to direct damages only",
                    "Add a cap on indemnification equal to contract value",
                    "Require mutual indemnification obligations"
                ])
            
            if "terminate" in text_lower and "without" in text_lower:
                points.extend([
                    "Request minimum 30-day notice period for termination",
                    "Add cure period for termination due to breach",
                    "Request mutual termination rights"
                ])
            
            if "penalty" in text_lower or "liquidated damages" in text_lower:
                points.extend([
                    "Request reduction in penalty amounts",
                    "Add cap on total penalties",
                    "Ensure penalties are proportionate to potential damage"
                ])
            
            if "exclusive" in text_lower and ("jurisdiction" in text_lower or "arbitration" in text_lower):
                points.extend([
                    "Request jurisdiction in a mutually convenient location",
                    "Consider adding online dispute resolution option",
                    "Request cost-sharing for dispute resolution"
                ])
        
        if not points:
            points = [
                "Review all obligations to ensure they are achievable",
                "Clarify any ambiguous terms before signing",
                "Request written clarification of any verbal promises"
            ]
        
        return points
