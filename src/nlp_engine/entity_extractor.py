"""
Entity Extractor
Extracts named entities from contracts using spaCy and custom patterns
"""
import re
from typing import Dict, List, Optional
from datetime import datetime

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class EntityExtractor:
    """Extract named entities from contract documents"""
    
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found. Using pattern-based extraction only.")
                self.nlp = None
        
        # Custom patterns for contract-specific entities
        self.patterns = {
            "parties": [
                r"(?:between|party|parties)[:\s]+([A-Z][A-Za-z\s&,\.]+?)(?:and|,|\(|hereinafter)",
                r"hereinafter\s+(?:referred\s+to\s+as|called)\s+[\"']?([A-Za-z\s]+)[\"']?",
                r"([A-Z][A-Za-z\s&]+(?:Pvt\.?|Private|Ltd\.?|Limited|LLP|Inc\.?|Corp\.?))",
            ],
            "dates": [
                r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
                r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
                r"(?:dated|effective|commencing)\s+(?:on\s+)?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            ],
            "amounts": [
                r"(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)",
                r"([\d,]+(?:\.\d{2})?)\s*(?:rupees|lakhs?|crores?)",
                r"\$\s*([\d,]+(?:\.\d{2})?)",
                r"(?:USD|EUR|GBP)\s*([\d,]+(?:\.\d{2})?)",
            ],
            "durations": [
                r"(\d+)\s*(?:years?|months?|weeks?|days?)",
                r"(?:period|term|duration)\s+of\s+(\d+)\s*(?:years?|months?|weeks?|days?)",
                r"for\s+a\s+(?:period|term)\s+of\s+(\d+)\s*(?:years?|months?|weeks?|days?)",
            ],
            "percentages": [
                r"(\d+(?:\.\d+)?)\s*(?:%|percent|per\s*cent)",
            ],
            "jurisdictions": [
                r"(?:jurisdiction|laws?\s+of|courts?\s+(?:of|at|in))\s+([A-Z][A-Za-z\s]+?)(?:\.|,|and)",
                r"(?:Mumbai|Delhi|Bangalore|Chennai|Kolkata|Hyderabad|Pune|Ahmedabad)\s+(?:courts?|jurisdiction)",
            ]
        }
    
    def extract_all(self, text: str) -> Dict:
        """
        Extract all entity types from text
        
        Args:
            text: Contract text
            
        Returns:
            Dict with all extracted entities
        """
        entities = {
            "parties": self._extract_parties(text),
            "dates": self._extract_dates(text),
            "amounts": self._extract_amounts(text),
            "durations": self._extract_durations(text),
            "percentages": self._extract_percentages(text),
            "jurisdictions": self._extract_jurisdictions(text),
        }
        
        # Add spaCy entities if available
        if self.nlp:
            spacy_entities = self._extract_with_spacy(text)
            entities["organizations"] = spacy_entities.get("ORG", [])
            entities["persons"] = spacy_entities.get("PERSON", [])
            entities["locations"] = spacy_entities.get("GPE", [])
        
        return entities
    
    def _extract_parties(self, text: str) -> List[Dict]:
        """Extract party names from contract"""
        parties = []
        seen = set()
        
        for pattern in self.patterns["parties"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                party_name = match.strip() if isinstance(match, str) else match[0].strip()
                # Clean up
                party_name = re.sub(r'\s+', ' ', party_name)
                party_name = party_name.strip('.,')
                
                if len(party_name) > 3 and party_name.lower() not in seen:
                    seen.add(party_name.lower())
                    parties.append({
                        "name": party_name,
                        "type": self._classify_party_type(party_name)
                    })
        
        return parties[:10]  # Limit to reasonable number
    
    def _classify_party_type(self, party_name: str) -> str:
        """Classify party as company or individual"""
        company_indicators = ["pvt", "private", "ltd", "limited", "llp", "inc", "corp", "company", "firm"]
        if any(ind in party_name.lower() for ind in company_indicators):
            return "company"
        return "individual_or_unknown"
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """Extract dates from contract"""
        dates = []
        seen = set()
        
        for pattern in self.patterns["dates"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.strip() if isinstance(match, str) else match[0].strip()
                if date_str not in seen:
                    seen.add(date_str)
                    dates.append({
                        "raw": date_str,
                        "parsed": self._parse_date(date_str)
                    })
        
        return dates
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Try to parse date into standard format"""
        formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
            "%m/%d/%Y", "%Y-%m-%d",
            "%d %B %Y", "%B %d, %Y", "%B %d %Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None
    
    def _extract_amounts(self, text: str) -> List[Dict]:
        """Extract monetary amounts from contract"""
        amounts = []
        
        for pattern in self.patterns["amounts"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                amount_str = match.group(1) if match.groups() else match.group(0)
                # Get currency
                full_match = match.group(0)
                currency = "INR"
                if "$" in full_match or "USD" in full_match:
                    currency = "USD"
                elif "EUR" in full_match:
                    currency = "EUR"
                elif "GBP" in full_match:
                    currency = "GBP"
                
                # Parse numeric value
                amount_clean = re.sub(r'[,\s]', '', amount_str)
                try:
                    value = float(amount_clean)
                    amounts.append({
                        "raw": full_match,
                        "value": value,
                        "currency": currency
                    })
                except ValueError:
                    pass
        
        return amounts
    
    def _extract_durations(self, text: str) -> List[Dict]:
        """Extract time durations from contract"""
        durations = []
        
        for pattern in self.patterns["durations"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                full = match.group(0)
                number = match.group(1)
                
                # Determine unit
                unit = "days"
                if "year" in full.lower():
                    unit = "years"
                elif "month" in full.lower():
                    unit = "months"
                elif "week" in full.lower():
                    unit = "weeks"
                
                try:
                    durations.append({
                        "raw": full,
                        "value": int(number),
                        "unit": unit
                    })
                except ValueError:
                    pass
        
        return durations
    
    def _extract_percentages(self, text: str) -> List[Dict]:
        """Extract percentages from contract"""
        percentages = []
        
        for pattern in self.patterns["percentages"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = float(match.group(1))
                    context = self._get_context(text, match.start(), match.end())
                    percentages.append({
                        "raw": match.group(0),
                        "value": value,
                        "context": context
                    })
                except ValueError:
                    pass
        
        return percentages
    
    def _extract_jurisdictions(self, text: str) -> List[str]:
        """Extract jurisdiction mentions from contract"""
        jurisdictions = set()
        
        for pattern in self.patterns["jurisdictions"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    jurisdictions.add(match.strip())
        
        # Also look for Indian cities commonly used in jurisdiction clauses
        indian_cities = ["Mumbai", "Delhi", "New Delhi", "Bangalore", "Bengaluru", 
                        "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
        for city in indian_cities:
            if city.lower() in text.lower():
                jurisdictions.add(city)
        
        return list(jurisdictions)
    
    def _extract_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy NER"""
        if not self.nlp:
            return {}
        
        # Limit text length for performance
        text = text[:100000]
        doc = self.nlp(text)
        
        entities = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            if ent.text not in entities[label]:
                entities[label].append(ent.text)
        
        return entities
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
