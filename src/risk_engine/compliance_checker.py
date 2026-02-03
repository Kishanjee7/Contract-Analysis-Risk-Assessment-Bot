"""
Compliance Checker
Checks contract compliance with Indian business law requirements
"""
import re
from typing import Dict, List


class ComplianceChecker:
    """Check contract compliance with Indian business law requirements"""
    
    def __init__(self):
        # Indian Contract Act 1872 requirements
        self.basic_requirements = {
            "parties": {
                "description": "Contract must clearly identify all parties",
                "patterns": [
                    r"(?:between|party|parties)",
                    r"(?:first\s+party|second\s+party)",
                    r"(?:company|employer|employee|vendor|client)"
                ]
            },
            "consideration": {
                "description": "Contract must have lawful consideration",
                "patterns": [
                    r"(?:consideration|payment|compensation|fee|salary|price)",
                    r"(?:Rs\.?|INR|₹)\s*[\d,]+"
                ]
            },
            "lawful_object": {
                "description": "Contract object must be lawful"
            },
            "free_consent": {
                "description": "Contract requires free consent of parties",
                "warning_patterns": [
                    r"(?:coercion|undue\s+influence|fraud|misrepresentation)"
                ]
            }
        }
        
        # Sector-specific compliance
        self.employment_compliance = {
            "minimum_wage": {
                "description": "Must comply with Minimum Wages Act",
                "check": "salary_amount"
            },
            "working_hours": {
                "description": "Maximum 48 hours/week as per Factories Act",
                "patterns": [r"(\d+)\s*hours?\s*(?:per\s+)?(?:week|day)"]
            },
            "leave_policy": {
                "description": "Must provide statutory leave entitlements",
                "patterns": [
                    r"(?:annual|earned|casual|sick)\s+leave",
                    r"(\d+)\s*days?\s*(?:of\s+)?leave"
                ]
            },
            "pf_esi": {
                "description": "EPF/ESI deductions may be applicable",
                "patterns": [
                    r"(?:provident\s+fund|PF|EPF|ESI)",
                    r"(?:employer\s+contribution|employee\s+contribution)"
                ]
            },
            "gratuity": {
                "description": "Gratuity applicable for 5+ years service",
                "patterns": [r"gratuity"]
            },
            "notice_period": {
                "description": "Notice requirements for termination",
                "patterns": [r"notice\s+period\s+of\s+(\d+)\s*(?:days?|months?)"]
            }
        }
        
        self.lease_compliance = {
            "stamp_duty": {
                "description": "Lease agreements require stamp duty payment",
                "patterns": [r"stamp\s+duty", r"registration"]
            },
            "registration": {
                "description": "Leases > 12 months must be registered",
                "patterns": [r"register(?:ed|ation)", r"sub-?registrar"]
            },
            "rent_control": {
                "description": "May be subject to state Rent Control Act",
                "patterns": [r"rent\s+control\s+act", r"standard\s+rent"]
            }
        }
        
        self.general_compliance = {
            "stamp_paper": {
                "description": "Contract may require execution on stamp paper",
                "patterns": [r"stamp\s+paper", r"stamp\s+duty", r"e-?stamp"]
            },
            "witness": {
                "description": "Witnesses may be required for validity",
                "patterns": [r"witness(?:es)?", r"attestation", r"attest(?:ed)?"]
            },
            "jurisdiction": {
                "description": "Exclusive jurisdiction clauses should be reasonable",
                "patterns": [r"(?:exclusive\s+)?jurisdiction\s+(?:of\s+)?(?:courts?\s+(?:at|of|in))"]
            },
            "arbitration": {
                "description": "Must comply with Arbitration & Conciliation Act",
                "patterns": [r"arbitration", r"Arbitration\s+and\s+Conciliation\s+Act"]
            }
        }
    
    def check_compliance(self, text: str, contract_type: str = "general") -> Dict:
        """
        Check contract for compliance issues
        
        Args:
            text: Contract text
            contract_type: Type of contract (employment, lease, vendor, etc.)
            
        Returns:
            Dict with compliance findings
        """
        text_lower = text.lower()
        
        results = {
            "basic_requirements": self._check_basic_requirements(text),
            "general_compliance": self._check_general(text),
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Add contract-type specific checks
        if contract_type == "employment_agreement":
            results["employment_compliance"] = self._check_employment(text)
        elif contract_type == "lease_agreement":
            results["lease_compliance"] = self._check_lease(text)
        
        # Compile issues and recommendations
        self._compile_findings(results)
        
        # Calculate compliance score
        results["compliance_score"] = self._calculate_score(results)
        
        return results
    
    def _check_basic_requirements(self, text: str) -> Dict:
        """Check basic contract requirements"""
        findings = {}
        
        for req_name, req_config in self.basic_requirements.items():
            if "patterns" in req_config:
                found = any(
                    re.search(pattern, text, re.IGNORECASE)
                    for pattern in req_config["patterns"]
                )
                findings[req_name] = {
                    "description": req_config["description"],
                    "found": found,
                    "status": "[OK] Found" if found else "[!] Not clearly specified"
                }
            else:
                findings[req_name] = {
                    "description": req_config["description"],
                    "status": "[!] Manual review required"
                }
        
        return findings
    
    def _check_employment(self, text: str) -> Dict:
        """Check employment-specific compliance"""
        findings = {}
        
        for check_name, check_config in self.employment_compliance.items():
            if "patterns" in check_config:
                matches = []
                for pattern in check_config["patterns"]:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    matches.extend(found)
                
                findings[check_name] = {
                    "description": check_config["description"],
                    "found": len(matches) > 0,
                    "matches": matches[:5],  # Limit matches
                    "status": "[OK] Addressed" if matches else "[!] Not specified"
                }
            else:
                findings[check_name] = {
                    "description": check_config["description"],
                    "status": "[!] Manual review required"
                }
        
        return findings
    
    def _check_lease(self, text: str) -> Dict:
        """Check lease-specific compliance"""
        findings = {}
        
        for check_name, check_config in self.lease_compliance.items():
            matches = []
            for pattern in check_config["patterns"]:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            
            findings[check_name] = {
                "description": check_config["description"],
                "found": len(matches) > 0,
                "status": "[OK] Mentioned" if matches else "[!] Not addressed"
            }
        
        # Check if registration might be required (lease > 12 months)
        duration_match = re.search(r'(\d+)\s*(?:months?|years?)', text, re.IGNORECASE)
        if duration_match:
            duration_text = duration_match.group(0).lower()
            if "year" in duration_text or (duration_match.group(1).isdigit() and int(duration_match.group(1)) > 12 and "month" in duration_text):
                findings["registration_required"] = {
                    "description": "Lease exceeds 12 months - Registration mandatory under Registration Act",
                    "status": "⚠ Registration required",
                    "action": "Register with Sub-Registrar office"
                }
        
        return findings
    
    def _check_general(self, text: str) -> Dict:
        """Check general compliance requirements"""
        findings = {}
        
        for check_name, check_config in self.general_compliance.items():
            matches = []
            for pattern in check_config["patterns"]:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            
            findings[check_name] = {
                "description": check_config["description"],
                "found": len(matches) > 0,
                "status": "[OK] Addressed" if matches else "[i] Not explicitly mentioned"
            }
        
        return findings
    
    def _compile_findings(self, results: Dict) -> None:
        """Compile issues and recommendations from all checks"""
        # Check basic requirements
        for req_name, req_data in results.get("basic_requirements", {}).items():
            if not req_data.get("found", True) and req_name != "lawful_object":
                results["issues"].append(f"{req_data['description']} - not clearly specified")
        
        # Employment-specific issues
        for check_name, check_data in results.get("employment_compliance", {}).items():
            if not check_data.get("found", True):
                results["warnings"].append(f"{check_data['description']} - should be addressed")
        
        # Lease-specific issues
        for check_name, check_data in results.get("lease_compliance", {}).items():
            if check_name == "registration_required":
                results["issues"].append(check_data.get("action", ""))
            elif not check_data.get("found", True):
                results["warnings"].append(f"{check_data['description']}")
        
        # Add recommendations
        if not results.get("general_compliance", {}).get("stamp_paper", {}).get("found"):
            results["recommendations"].append(
                "Consider executing the contract on appropriate stamp paper as per applicable state laws"
            )
        
        if not results.get("general_compliance", {}).get("witness", {}).get("found"):
            results["recommendations"].append(
                "Consider having the contract attested by witnesses for stronger enforceability"
            )
    
    def _calculate_score(self, results: Dict) -> float:
        """Calculate overall compliance score"""
        total_checks = 0
        passed_checks = 0
        
        # Count basic requirements
        for req_data in results.get("basic_requirements", {}).values():
            total_checks += 1
            if req_data.get("found", False) or "Manual" in req_data.get("status", ""):
                passed_checks += 1
        
        # Count type-specific compliance
        for compliance_type in ["employment_compliance", "lease_compliance"]:
            for check_data in results.get(compliance_type, {}).values():
                total_checks += 1
                if check_data.get("found", False):
                    passed_checks += 1
        
        if total_checks == 0:
            return 100.0
        
        return round((passed_checks / total_checks) * 100, 1)
    
    def get_compliance_summary(self, results: Dict) -> Dict:
        """Generate SME-friendly compliance summary"""
        score = results.get("compliance_score", 0)
        
        summary = {
            "score": score,
            "status": "",
            "key_issues": results.get("issues", [])[:5],
            "warnings": results.get("warnings", [])[:5],
            "action_items": results.get("recommendations", [])[:5]
        }
        
        if score >= 80:
            summary["status"] = "[GOOD] Good Compliance - Contract addresses most legal requirements"
        elif score >= 60:
            summary["status"] = "[MODERATE] Moderate Compliance - Some requirements may need attention"
        else:
            summary["status"] = "[LOW] Low Compliance - Several legal requirements may not be addressed"
        
        return summary
