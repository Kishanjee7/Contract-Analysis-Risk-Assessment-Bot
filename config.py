"""
Configuration Management for Contract Analysis Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent
AUDIT_LOGS_DIR = BASE_DIR / "audit_logs"
TEMPLATES_DIR = BASE_DIR / "src" / "templates"
KNOWLEDGE_BASE_DIR = BASE_DIR / "src" / "knowledge_base"

# Ensure directories exist
AUDIT_LOGS_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Settings
OPENAI_MODEL = "gpt-4-turbo-preview"
ANTHROPIC_MODEL = "claude-3-opus-20240229"

# Application Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Contract Types
CONTRACT_TYPES = [
    "employment_agreement",
    "vendor_contract",
    "lease_agreement",
    "partnership_deed",
    "service_contract",
    "nda",
    "unknown"
]

# Risk Score Thresholds
RISK_THRESHOLDS = {
    "low": (0, 3),
    "medium": (4, 6),
    "high": (7, 10)
}

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "hi"]

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"]

# Risk Keywords and Patterns
HIGH_RISK_KEYWORDS = [
    "indemnify", "indemnification", "unlimited liability",
    "sole discretion", "unilateral", "waive all rights",
    "penalty", "liquidated damages", "forfeit",
    "perpetual", "irrevocable", "non-compete",
    "intellectual property transfer", "assign all rights"
]

MEDIUM_RISK_KEYWORDS = [
    "auto-renewal", "automatic renewal", "lock-in",
    "arbitration", "exclusive jurisdiction",
    "confidential", "non-disclosure", "terminate without cause",
    "modification", "amendment"
]

# Clause Types for Detection
CLAUSE_TYPES = [
    "obligations",
    "rights",
    "prohibitions",
    "payment_terms",
    "termination",
    "indemnity",
    "confidentiality",
    "intellectual_property",
    "dispute_resolution",
    "governing_law",
    "force_majeure",
    "amendment",
    "notice",
    "assignment"
]
