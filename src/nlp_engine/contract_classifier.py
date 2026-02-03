"""
Contract Type Classifier
Classifies contracts into categories based on content analysis
"""
import re
from typing import Dict, List, Tuple
from collections import Counter


class ContractClassifier:
    """Classify contract documents into predefined categories"""
    
    def __init__(self):
        # Keywords and patterns for each contract type
        self.contract_patterns = {
            "employment_agreement": {
                "keywords": [
                    "employee", "employer", "employment", "salary", "wages",
                    "working hours", "probation", "resignation", "termination of employment",
                    "job title", "job description", "work duties", "leave policy",
                    "gratuity", "provident fund", "epf", "esi", "notice period",
                    "full-time", "part-time", "designation", "reporting manager"
                ],
                "weight": 1.0
            },
            "vendor_contract": {
                "keywords": [
                    "vendor", "supplier", "purchase order", "supply", "goods",
                    "delivery", "shipment", "procurement", "inventory", "wholesale",
                    "pricing", "unit price", "bulk order", "minimum order",
                    "product specifications", "quality standards", "returns policy",
                    "invoice", "payment terms", "net 30", "net 60"
                ],
                "weight": 1.0
            },
            "lease_agreement": {
                "keywords": [
                    "lease", "lessor", "lessee", "tenant", "landlord",
                    "rent", "monthly rent", "security deposit", "premises",
                    "property", "real estate", "occupation", "subletting",
                    "maintenance", "utilities", "eviction", "renewal of lease",
                    "commercial lease", "residential", "lock-in period"
                ],
                "weight": 1.0
            },
            "partnership_deed": {
                "keywords": [
                    "partner", "partnership", "partnership deed", "profit sharing",
                    "loss sharing", "capital contribution", "partnership firm",
                    "managing partner", "sleeping partner", "dissolution",
                    "partnership act", "goodwill", "drawings", "retirement of partner"
                ],
                "weight": 1.0
            },
            "service_contract": {
                "keywords": [
                    "service provider", "client", "services", "scope of work",
                    "deliverables", "milestones", "service level", "sla",
                    "consulting", "professional services", "project timeline",
                    "acceptance criteria", "change request", "statement of work",
                    "hourly rate", "fixed fee", "retainer"
                ],
                "weight": 1.0
            },
            "nda": {
                "keywords": [
                    "non-disclosure", "nda", "confidential information",
                    "confidentiality agreement", "proprietary information",
                    "trade secrets", "disclosing party", "receiving party",
                    "non-circumvention", "mutual nda", "unilateral nda"
                ],
                "weight": 1.2  # Higher weight as NDAs are usually shorter
            }
        }
        
        # Title patterns that strongly indicate contract type
        self.title_patterns = {
            "employment_agreement": r"(employment|job|appointment|offer)\s*(agreement|contract|letter)",
            "vendor_contract": r"(vendor|supplier|supply|purchase)\s*(agreement|contract|order)",
            "lease_agreement": r"(lease|rental|tenancy)\s*(agreement|deed|contract)",
            "partnership_deed": r"partnership\s*(deed|agreement)",
            "service_contract": r"(service|consulting|professional)\s*(agreement|contract)",
            "nda": r"(non-disclosure|nda|confidentiality)\s*(agreement|contract)?"
        }
    
    def classify(self, text: str) -> Dict:
        """
        Classify a contract based on its content
        
        Args:
            text: Full text of the contract
            
        Returns:
            Dict with classification results
        """
        text_lower = text.lower()
        scores = {}
        
        # First, check title patterns (first 500 chars)
        title_section = text_lower[:500]
        title_match = None
        
        for contract_type, pattern in self.title_patterns.items():
            if re.search(pattern, title_section, re.IGNORECASE):
                title_match = contract_type
                break
        
        # Calculate keyword scores for each type
        for contract_type, config in self.contract_patterns.items():
            keyword_count = 0
            matched_keywords = []
            
            for keyword in config["keywords"]:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
                if count > 0:
                    keyword_count += count
                    matched_keywords.append(keyword)
            
            # Apply weight
            weighted_score = keyword_count * config["weight"]
            
            # Bonus for title match
            if contract_type == title_match:
                weighted_score *= 2
            
            scores[contract_type] = {
                "score": weighted_score,
                "matched_keywords": matched_keywords,
                "keyword_count": len(matched_keywords)
            }
        
        # Determine primary classification
        if scores:
            primary_type = max(scores.keys(), key=lambda k: scores[k]["score"])
            max_score = scores[primary_type]["score"]
            
            # Check if score is significant enough
            if max_score < 3:
                primary_type = "unknown"
                confidence = 0.0
            else:
                # Calculate confidence based on score distribution
                total_score = sum(s["score"] for s in scores.values())
                confidence = scores[primary_type]["score"] / total_score if total_score > 0 else 0
        else:
            primary_type = "unknown"
            confidence = 0.0
        
        return {
            "primary_type": primary_type,
            "confidence": round(confidence, 2),
            "all_scores": scores,
            "title_match": title_match,
            "top_keywords": scores.get(primary_type, {}).get("matched_keywords", [])[:10]
        }
    
    def get_contract_type_description(self, contract_type: str) -> str:
        """Get a human-readable description of the contract type"""
        descriptions = {
            "employment_agreement": "Employment Agreement - A contract between an employer and employee defining terms of employment",
            "vendor_contract": "Vendor/Supplier Contract - An agreement for the supply of goods or products",
            "lease_agreement": "Lease Agreement - A contract for the rental of property or premises",
            "partnership_deed": "Partnership Deed - An agreement establishing a business partnership",
            "service_contract": "Service Contract - An agreement for the provision of professional services",
            "nda": "Non-Disclosure Agreement - A contract protecting confidential information",
            "unknown": "Unknown Contract Type - Unable to determine the specific contract category"
        }
        return descriptions.get(contract_type, "Unknown Contract Type")
