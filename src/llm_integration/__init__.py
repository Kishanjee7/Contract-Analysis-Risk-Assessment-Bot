"""
LLM Integration Module
Handles integration with Claude/GPT-4 for legal reasoning
"""
from .llm_client import LLMClient
from .prompts import PromptTemplates
from .explainer import ClauseExplainer
from .clause_suggester import ClauseSuggester
from .summary_generator import ContractSummaryGenerator

__all__ = [
    "LLMClient",
    "PromptTemplates",
    "ClauseExplainer",
    "ClauseSuggester",
    "ContractSummaryGenerator"
]
