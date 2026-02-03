"""
Clause Explainer
Generates plain-language explanations of contract clauses
"""
from typing import Dict, Optional
from .llm_client import LLMClient
from .prompts import PromptTemplates


class ClauseExplainer:
    """Generate plain-language explanations of contract clauses"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.prompts = PromptTemplates()
        
        # Fallback explanations for common clause types
        self.fallback_explanations = {
            "indemnity": "This clause requires one party to compensate the other for losses, damages, or legal costs. It essentially means you agree to pay for certain problems that might arise.",
            "termination": "This clause explains how and when the contract can be ended. It may specify notice periods, reasons for termination, and what happens when the contract ends.",
            "confidentiality": "This clause requires you to keep certain information private and not share it with others. Violating this could lead to legal consequences.",
            "payment_terms": "This clause specifies how and when payments should be made, including amounts, due dates, and any penalties for late payment.",
            "governing_law": "This clause determines which location's laws will apply if there's a dispute. It can significantly affect your rights and where any legal proceedings would take place.",
            "force_majeure": "This clause covers situations beyond anyone's control (like natural disasters). It usually allows the contract to be paused or cancelled without penalty in such cases.",
            "intellectual_property": "This clause deals with ownership of ideas, inventions, creative works, and other intangible assets. It's important to understand who owns what during and after the contract.",
            "dispute_resolution": "This clause explains how disagreements will be handled - through courts, arbitration, or other methods. The chosen method can affect cost, time, and privacy.",
            "assignment": "This clause controls whether you can transfer your rights or obligations under this contract to someone else.",
            "amendment": "This clause explains how the contract can be changed or modified after signing."
        }
    
    def explain(self, clause_text: str, clause_type: str = None) -> Dict:
        """
        Generate a plain-language explanation of a clause
        
        Args:
            clause_text: The clause text to explain
            clause_type: Optional type hint for the clause
            
        Returns:
            Dict with explanation and metadata
        """
        # Try LLM first
        if self.llm.is_available():
            explanation = self._explain_with_llm(clause_text, clause_type)
        else:
            explanation = self._explain_fallback(clause_text, clause_type)
        
        return {
            "original_text": clause_text,
            "explanation": explanation,
            "clause_type": clause_type,
            "source": "ai" if self.llm.is_available() else "template"
        }
    
    def _explain_with_llm(self, clause_text: str, clause_type: str = None) -> str:
        """Generate explanation using LLM"""
        prompt = self.prompts.explain_clause(clause_text, clause_type)
        return self.llm.chat(prompt, self.prompts.CLAUSE_EXPLANATION_SYSTEM)
    
    def _explain_fallback(self, clause_text: str, clause_type: str = None) -> str:
        """Generate explanation using fallback templates"""
        if clause_type and clause_type in self.fallback_explanations:
            base_explanation = self.fallback_explanations[clause_type]
        else:
            base_explanation = self._analyze_basic(clause_text)
        
        return f"""📋 **Clause Explanation** (Rule-based analysis)

{base_explanation}

⚠️ *Note: For a more detailed AI-powered explanation, please configure an API key in your .env file.*"""
    
    def _analyze_basic(self, text: str) -> str:
        """Basic analysis without LLM"""
        text_lower = text.lower()
        
        elements = []
        
        if "shall" in text_lower or "must" in text_lower:
            elements.append("This clause creates **obligations** - things that must be done.")
        
        if "shall not" in text_lower or "must not" in text_lower:
            elements.append("This clause includes **prohibitions** - things that cannot be done.")
        
        if "may" in text_lower:
            elements.append("This clause grants certain **rights or permissions**.")
        
        if not elements:
            elements.append("This clause sets out general terms and conditions.")
        
        return "\n".join(elements)
    
    def explain_batch(self, clauses: list) -> list:
        """
        Explain multiple clauses
        
        Args:
            clauses: List of clause dictionaries with 'text' and optional 'clause_type'
            
        Returns:
            List of explanation results
        """
        results = []
        for clause in clauses:
            text = clause.get("text", "")
            clause_type = clause.get("clause_type")
            
            if len(text) > 50:  # Only explain meaningful clauses
                explanation = self.explain(text, clause_type)
                results.append({
                    **clause,
                    "explanation": explanation["explanation"]
                })
        
        return results
