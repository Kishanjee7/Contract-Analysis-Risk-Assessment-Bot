# Contract Analysis & Risk Assessment Bot

A GenAI-powered legal assistant for SMEs to analyze contracts, identify risks, and receive actionable advice in plain language.

##Link

## Features

- 📄 **Multi-format Support**: PDF, DOCX, and TXT contract analysis
- 🔍 **Risk Assessment**: Clause-level and contract-level risk scoring
- 🏷️ **Entity Extraction**: Parties, dates, amounts, jurisdiction, obligations
- 💡 **Plain Language Explanations**: AI-powered clause explanations
- 🌐 **Multilingual**: English and Hindi contract support
- 📊 **Visual Dashboard**: Interactive Streamlit interface
- 📑 **PDF Reports**: Export analysis for legal consultation

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
4. Configure API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI or Anthropic API key

## Usage

```bash
streamlit run app.py
```

## Project Structure

```
├── app.py                 # Main Streamlit application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── src/
│   ├── document_processor/   # Document extraction modules
│   ├── nlp_engine/          # NLP processing modules
│   ├── risk_engine/         # Risk assessment modules
│   ├── llm_integration/     # LLM client and prompts
│   ├── templates/           # Contract templates
│   ├── knowledge_base/      # Risk patterns and issues
│   ├── ui/                  # UI components
│   └── utils/               # Utilities and logging
├── tests/                 # Test files
└── audit_logs/            # Audit trail storage
```

## License

MIT License
