"""
Prompt Templates
Curated prompts for legal contract analysis
"""


class PromptTemplates:
    """Collection of prompt templates for contract analysis"""
    
    # System prompts
    LEGAL_ASSISTANT_SYSTEM = """You are an expert legal assistant specializing in contract analysis for small and medium businesses (SMEs) in India. 

Your role is to:
1. Explain legal terms in simple, plain language that business owners can understand
2. Identify potential risks and red flags in contracts
3. Suggest fairer alternatives for problematic clauses
4. Provide practical, actionable advice

Guidelines:
- Always explain legal jargon in simple terms
- Be balanced - acknowledge both risks and benefits
- Consider the SME perspective (limited resources, less bargaining power)
- Reference relevant Indian laws where applicable
- Never provide specific legal advice - recommend professional consultation for complex matters
- Be concise but thorough"""

    CLAUSE_EXPLANATION_SYSTEM = """You are a legal expert explaining contract clauses to business owners who may not have legal training.

Your explanations should:
- Use simple, everyday language
- Avoid legal jargon (or explain it immediately when used)
- Give practical examples where helpful
- Highlight both what the clause means AND its implications
- Be concise (2-3 sentences for simple clauses, more for complex ones)"""

    RISK_ANALYSIS_SYSTEM = """You are a contract risk analyst helping SMEs understand potential legal risks.

Your analysis should:
- Identify specific risks in the clause or contract
- Rate severity (Low/Medium/High) with clear reasoning
- Explain real-world consequences of the risk
- Suggest mitigation strategies
- Consider the Indian business context"""

    CLAUSE_SUGGESTION_SYSTEM = """You are a contract negotiation expert helping SMEs get fairer terms.

Your suggestions should:
- Propose specific alternative wording
- Explain why the alternative is more balanced
- Maintain legal validity of the clause
- Be realistic (not one-sided in favor of the user)
- Consider that both parties need acceptable terms"""

    # User prompts
    @staticmethod
    def explain_clause(clause_text: str, clause_type: str = None) -> str:
        """Generate prompt for clause explanation"""
        type_context = f" (This appears to be a {clause_type.replace('_', ' ')} clause)" if clause_type else ""
        
        return f"""Please explain the following contract clause in simple, plain language that a business owner can understand{type_context}:

---
{clause_text}
---

Provide:
1. A simple explanation of what this clause means
2. The practical implications for a business signing this contract
3. Any potential concerns or things to watch out for"""

    @staticmethod
    def analyze_risk(clause_text: str, detected_risks: list = None) -> str:
        """Generate prompt for risk analysis"""
        risks_context = ""
        if detected_risks:
            risks_context = f"\n\nOur automated analysis flagged these potential concerns: {', '.join(detected_risks)}"
        
        return f"""Analyze the following contract clause for potential risks to a small/medium business:{risks_context}

---
{clause_text}
---

Provide:
1. Risk Level (Low/Medium/High) with reasoning
2. Specific risks identified
3. Potential real-world consequences
4. Recommended actions or negotiation points"""

    @staticmethod
    def suggest_alternative(clause_text: str, concerns: list = None) -> str:
        """Generate prompt for alternative clause suggestion"""
        concerns_context = ""
        if concerns:
            concerns_context = f"\n\nKey concerns to address: {', '.join(concerns)}"
        
        return f"""Suggest a more balanced alternative to the following contract clause:{concerns_context}

---
{clause_text}
---

Provide:
1. The suggested alternative clause text (complete wording)
2. Explanation of what changed and why
3. How this better protects the business while remaining fair to both parties"""

    @staticmethod
    def generate_summary(contract_text: str, contract_type: str = None) -> str:
        """Generate prompt for contract summary"""
        type_context = f" ({contract_type.replace('_', ' ')})" if contract_type else ""
        
        return f"""Provide an executive summary of the following contract{type_context} for a business owner:

---
{contract_text[:8000]}  # Truncate for token limits
---

Include:
1. Overview (2-3 sentences on what this contract is about)
2. Key Terms (main obligations, rights, and timelines)
3. Financial Terms (payments, fees, penalties)
4. Duration and Termination conditions
5. Top 3 things the business owner should pay attention to

Keep the summary concise and in plain language."""

    @staticmethod
    def compliance_advice(contract_text: str, compliance_issues: list = None) -> str:
        """Generate prompt for compliance advice"""
        issues_context = ""
        if compliance_issues:
            issues_context = f"\n\nIdentified compliance gaps: {', '.join(compliance_issues)}"
        
        return f"""Review this contract for compliance with Indian business laws and provide advice:{issues_context}

---
{contract_text[:6000]}
---

Provide:
1. Compliance status overview
2. Any missing legal requirements
3. Recommendations to ensure legal validity
4. Specific Indian laws that may apply (if any)

Note: This is general guidance only, not legal advice."""

    @staticmethod
    def translate_to_simple(legal_text: str) -> str:
        """Generate prompt for translating legal language to simple language"""
        return f"""Translate the following legal text into simple, everyday language that anyone can understand:

---
{legal_text}
---

Requirements:
- Use simple words and short sentences
- Explain any technical terms
- Keep the meaning accurate
- Make it suitable for someone with no legal background"""

    @staticmethod
    def compare_clauses(standard_clause: str, contract_clause: str) -> str:
        """Generate prompt for comparing contract clause with standard"""
        return f"""Compare the following contract clause with a standard/typical clause and identify any deviations:

STANDARD CLAUSE:
---
{standard_clause}
---

CONTRACT CLAUSE:
---
{contract_clause}
---

Provide:
1. Key differences identified
2. Whether deviations favor one party over another
3. Risk assessment of the deviations
4. Recommendation on whether to accept, negotiate, or reject"""
