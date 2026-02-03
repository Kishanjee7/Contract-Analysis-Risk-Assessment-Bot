"""
Contract Summary Generator
Generates executive summaries of contracts
"""
from typing import Dict, Optional
from .llm_client import LLMClient
from .prompts import PromptTemplates


class ContractSummaryGenerator:
    """Generate plain-language contract summaries"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.prompts = PromptTemplates()
    
    def generate_summary(self, 
                        contract_text: str,
                        contract_type: str = None,
                        entities: Dict = None,
                        risk_score: Dict = None) -> Dict:
        """
        Generate an executive summary of a contract
        
        Args:
            contract_text: Full contract text
            contract_type: Type of contract
            entities: Extracted entities (parties, dates, amounts)
            risk_score: Risk assessment results
            
        Returns:
            Dict with summary sections
        """
        if self.llm.is_available():
            ai_summary = self._generate_with_llm(contract_text, contract_type)
        else:
            ai_summary = None
        
        # Generate structured summary from extracted data
        structured_summary = self._generate_structured_summary(
            entities or {}, risk_score or {}
        )
        
        return {
            "ai_summary": ai_summary,
            "structured_summary": structured_summary,
            "quick_facts": self._generate_quick_facts(entities or {}),
            "source": "ai" if ai_summary else "extracted"
        }
    
    def _generate_with_llm(self, contract_text: str, contract_type: str) -> str:
        """Generate summary using LLM"""
        prompt = self.prompts.generate_summary(contract_text, contract_type)
        return self.llm.chat(prompt, self.prompts.LEGAL_ASSISTANT_SYSTEM)
    
    def _generate_structured_summary(self, entities: Dict, risk_score: Dict) -> Dict:
        """Generate summary from extracted data"""
        summary = {}
        
        # Parties
        parties = entities.get("parties", [])
        if parties:
            summary["parties"] = [p.get("name", "") for p in parties]
        
        # Key dates
        dates = entities.get("dates", [])
        if dates:
            summary["key_dates"] = [d.get("raw", "") for d in dates[:5]]
        
        # Financial terms
        amounts = entities.get("amounts", [])
        if amounts:
            summary["financial_terms"] = [
                f"{a.get('currency', 'INR')} {a.get('value', '')}" 
                for a in amounts[:5]
            ]
        
        # Duration
        durations = entities.get("durations", [])
        if durations:
            summary["duration"] = durations[0].get("raw", "")
        
        # Risk overview
        if risk_score:
            summary["risk_level"] = risk_score.get("risk_level", "unknown")
            summary["risk_score"] = risk_score.get("composite_score", 0)
        
        return summary
    
    def _generate_quick_facts(self, entities: Dict) -> list:
        """Generate quick facts list"""
        facts = []
        
        parties = entities.get("parties", [])
        if len(parties) >= 2:
            facts.append(f"📝 Agreement between {parties[0].get('name', 'Party 1')} and {parties[1].get('name', 'Party 2')}")
        
        amounts = entities.get("amounts", [])
        if amounts:
            largest = max(amounts, key=lambda x: x.get("value", 0))
            facts.append(f"💰 Contract value: {largest.get('currency', 'INR')} {largest.get('value', '')}")
        
        durations = entities.get("durations", [])
        if durations:
            facts.append(f"⏱️ Duration: {durations[0].get('raw', 'Not specified')}")
        
        jurisdictions = entities.get("jurisdictions", [])
        if jurisdictions:
            facts.append(f"⚖️ Jurisdiction: {jurisdictions[0]}")
        
        return facts
    
    def translate_to_simple(self, legal_text: str) -> str:
        """
        Translate legal text to simple language
        
        Args:
            legal_text: Complex legal text
            
        Returns:
            Plain language translation
        """
        if self.llm.is_available():
            prompt = self.prompts.translate_to_simple(legal_text)
            return self.llm.chat(prompt, self.prompts.CLAUSE_EXPLANATION_SYSTEM)
        else:
            return self._basic_simplification(legal_text)
    
    def _basic_simplification(self, text: str) -> str:
        """Basic rule-based simplification"""
        replacements = {
            "hereinafter": "from now on",
            "whereas": "because",
            "notwithstanding": "despite",
            "pursuant to": "according to",
            "aforementioned": "mentioned earlier",
            "hereunder": "under this agreement",
            "hereto": "to this agreement",
            "shall": "will",
            "thereof": "of that",
            "therein": "in that",
            "whereby": "by which",
            "forthwith": "immediately"
        }
        
        result = text
        for legal_term, simple_term in replacements.items():
            result = result.replace(legal_term, simple_term)
            result = result.replace(legal_term.capitalize(), simple_term.capitalize())
        
        return result
