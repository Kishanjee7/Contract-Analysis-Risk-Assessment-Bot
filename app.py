"""
Contract Analysis & Risk Assessment Bot
Main Streamlit Application
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import *
from src.document_processor import DocumentLoader
from src.nlp_engine import (
    ContractClassifier, ClauseExtractor, 
    EntityExtractor, ObligationAnalyzer, AmbiguityDetector
)
from src.risk_engine import (
    RiskScorer, ClauseDetectors, 
    ComplianceChecker, RiskReportGenerator
)
from src.llm_integration import (
    LLMClient, ClauseExplainer, 
    ClauseSuggester, ContractSummaryGenerator
)
from src.ui import Dashboard, UIComponents, PDFReportGenerator
from src.utils import AuditLogger, TextUtils


# Page config
st.set_page_config(
    page_title="Contract Analyzer - SME Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
    }
    .upload-box {
        border: 2px dashed #1E3A5F;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None


def render_sidebar():
    """Render the sidebar"""
    st.sidebar.markdown("# ⚖️ Contract Analyzer")
    st.sidebar.markdown("### For Small & Medium Businesses")
    
    st.sidebar.markdown("---")
    
    # AI Status
    llm = LLMClient()
    if llm.is_available():
        st.sidebar.success(f"🤖 AI: {llm.get_provider_name()}")
    else:
        st.sidebar.warning("🤖 AI: Not configured")
        st.sidebar.caption("Add API key to .env for AI features")
    
    st.sidebar.markdown("---")
    
    # Supported formats
    st.sidebar.markdown("### 📄 Supported Formats")
    st.sidebar.markdown("- PDF documents")
    st.sidebar.markdown("- Word documents (.docx)")
    st.sidebar.markdown("- Text files (.txt)")
    
    # Disclaimer
    UIComponents.render_sidebar_info()


def analyze_contract(file_bytes: bytes, file_name: str) -> dict:
    """Run full contract analysis pipeline"""
    results = {
        "file_name": file_name,
        "success": False
    }
    
    progress_bar = st.progress(0, text="Starting analysis...")
    
    try:
        # Step 1: Document Loading
        progress_bar.progress(10, text="📄 Extracting text from document...")
        doc_loader = DocumentLoader()
        doc_result = doc_loader.load(file_bytes=file_bytes, file_name=file_name)
        
        if not doc_result.get("success"):
            st.error(f"❌ Failed to load document: {doc_result.get('error', 'Unknown error')}")
            return results
        
        text = doc_result.get("text", "")
        results["text"] = text
        results["language_info"] = doc_result.get("language_info", {})
        
        # Step 2: Contract Classification
        progress_bar.progress(20, text="🏷️ Classifying contract type...")
        classifier = ContractClassifier()
        results["contract_type"] = classifier.classify(text)
        
        # Step 3: Clause Extraction
        progress_bar.progress(30, text="📑 Extracting clauses...")
        clause_extractor = ClauseExtractor()
        clauses = clause_extractor.extract_clauses(text)
        results["clauses_raw"] = clauses
        
        # Step 4: Entity Extraction
        progress_bar.progress(40, text="🔍 Extracting entities...")
        entity_extractor = EntityExtractor()
        results["entities"] = entity_extractor.extract_all(text)
        
        # Step 5: Obligation Analysis
        progress_bar.progress(50, text="⚖️ Analyzing obligations...")
        obligation_analyzer = ObligationAnalyzer()
        results["obligations"] = obligation_analyzer.analyze(text)
        
        # Step 6: Ambiguity Detection
        progress_bar.progress(55, text="🔎 Detecting ambiguities...")
        ambiguity_detector = AmbiguityDetector()
        results["ambiguities"] = ambiguity_detector.detect(text)
        
        # Step 7: Risk Scoring
        progress_bar.progress(65, text="📊 Calculating risk scores...")
        risk_scorer = RiskScorer()
        
        # Score individual clauses
        scored_clauses = []
        for clause in clauses:
            clause_score = risk_scorer.score_clause(clause.get("text", ""))
            scored_clauses.append({
                **clause,
                "score": clause_score["score"],
                "risk_level": clause_score["risk_level"],
                "findings": clause_score["findings"]
            })
        
        results["clauses"] = scored_clauses
        results["risk_score"] = risk_scorer.score_contract(clauses)
        
        # Step 8: Clause Detection
        progress_bar.progress(75, text="🔴 Detecting risky clauses...")
        clause_detectors = ClauseDetectors()
        results["clause_detections"] = clause_detectors.detect_all(text)
        
        # Step 9: Compliance Check
        progress_bar.progress(80, text="✓ Checking compliance...")
        compliance_checker = ComplianceChecker()
        contract_type = results["contract_type"].get("primary_type", "general")
        results["compliance"] = compliance_checker.check_compliance(text, contract_type)
        
        # Step 10: Generate Explanations (if LLM available)
        progress_bar.progress(85, text="💡 Generating explanations...")
        llm = LLMClient()
        if llm.is_available():
            explainer = ClauseExplainer(llm)
            # Explain top risk clauses only
            high_risk_clauses = [c for c in scored_clauses if c["risk_level"] in ["high", "medium"]][:5]
            for clause in high_risk_clauses:
                explanation = explainer.explain(clause.get("text", ""), clause.get("clause_type"))
                clause["explanation"] = explanation.get("explanation", "")
        
        # Step 11: Generate Summary
        progress_bar.progress(90, text="📝 Generating summary...")
        summary_gen = ContractSummaryGenerator(llm if llm.is_available() else None)
        results["summary"] = summary_gen.generate_summary(
            text, 
            contract_type,
            results["entities"],
            results["risk_score"]
        )
        
        # Step 12: Generate Report
        progress_bar.progress(95, text="📋 Generating report...")
        report_gen = RiskReportGenerator()
        results["report"] = report_gen.generate_report(
            {"file_name": file_name, "contract_type": contract_type},
            results["risk_score"],
            results["clause_detections"],
            results["compliance"],
            results["entities"],
            results["obligations"]
        )
        
        # Step 13: Log to Audit
        audit_logger = AuditLogger()
        file_hash = audit_logger.get_file_hash(file_bytes)
        results["audit_id"] = audit_logger.create_audit_entry(
            file_name, file_hash, "full_analysis", results
        )
        
        progress_bar.progress(100, text="✅ Analysis complete!")
        results["success"] = True
        
    except Exception as e:
        st.error(f"❌ Analysis error: {str(e)}")
        import traceback
        st.expander("Error Details").code(traceback.format_exc())
    
    return results


def render_upload_section():
    """Render the file upload section"""
    st.markdown('<p class="main-header">📜 Contract Analysis & Risk Assessment</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your contract to get AI-powered risk analysis, plain-language explanations, and actionable recommendations.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        uploaded_file = st.file_uploader(
            "Upload your contract",
            type=["pdf", "docx", "doc", "txt"],
            help="Supported formats: PDF, Word (DOCX), Text files"
        )
        
        if uploaded_file:
            file_info = f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)"
            st.info(file_info)
            
            if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):
                file_bytes = uploaded_file.read()
                
                with st.spinner("Analyzing contract..."):
                    results = analyze_contract(file_bytes, uploaded_file.name)
                
                if results.get("success"):
                    st.session_state.analysis_results = results
                    st.session_state.analysis_complete = True
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.rerun()


def render_results_section():
    """Render the analysis results"""
    results = st.session_state.analysis_results
    
    if not results:
        st.error("No analysis results found.")
        return
    
    # Header with actions
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"## 📋 Analysis: {st.session_state.uploaded_file_name}")
    
    with col2:
        # Export PDF button
        pdf_gen = PDFReportGenerator()
        pdf_bytes = pdf_gen.generate(results, st.session_state.uploaded_file_name)
        st.download_button(
            "📥 Download PDF Report",
            data=pdf_bytes,
            file_name=f"contract_analysis_{st.session_state.uploaded_file_name.split('.')[0]}.pdf",
            mime="application/pdf"
        )
    
    with col3:
        if st.button("🔄 Analyze Another"):
            st.session_state.analysis_complete = False
            st.session_state.analysis_results = None
            st.session_state.uploaded_file_name = None
            st.rerun()
    
    # Render dashboard
    Dashboard.render(results)


def main():
    """Main application entry point"""
    initialize_session_state()
    render_sidebar()
    
    if st.session_state.analysis_complete and st.session_state.analysis_results:
        render_results_section()
    else:
        render_upload_section()
        
        # Sample contracts section
        st.markdown("---")
        st.markdown("### 📚 What This Tool Analyzes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔍 Risk Detection**
            - Penalty clauses
            - Indemnity provisions
            - Unilateral termination
            - Auto-renewal terms
            - Non-compete clauses
            """)
        
        with col2:
            st.markdown("""
            **📋 Contract Analysis**
            - Contract type classification
            - Clause-by-clause breakdown
            - Entity extraction
            - Obligation mapping
            - Ambiguity detection
            """)
        
        with col3:
            st.markdown("""
            **💡 AI Insights**
            - Plain-language explanations
            - Alternative clause suggestions
            - Compliance checking
            - Risk scoring
            - Negotiation points
            """)


if __name__ == "__main__":
    main()
