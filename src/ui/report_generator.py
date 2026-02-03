"""
PDF Report Generator
Generates PDF reports for export
"""
from fpdf import FPDF
from typing import Dict
from datetime import datetime
import io
import re


class PDFReportGenerator:
    """Generate PDF reports from analysis results"""
    
    def __init__(self):
        self.pdf = None
    
    def _sanitize_text(self, text: str) -> str:
        """Remove Unicode characters not supported by Helvetica font"""
        if not text:
            return ""
        
        # Replace common emojis with text equivalents
        replacements = {
            "✅": "[OK]",
            "❌": "[X]",
            "⚠️": "[!]",
            "🔴": "[HIGH]",
            "🟡": "[MEDIUM]",
            "🟢": "[LOW]",
            "⚡": "[!]",
            "📋": "",
            "📊": "",
            "📑": "",
            "💡": "",
            "💰": "",
            "📅": "",
            "⏱️": "",
            "⚖️": "",
            "🔍": "",
            "📝": "",
            "👥": "",
            "🤖": "",
            "📄": "",
            "🏷️": "",
            "✓": "[OK]",
        }
        
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
        
        # Remove any remaining non-ASCII characters that might cause issues
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text
    
    def generate(self, analysis_results: Dict, file_name: str = "contract_analysis") -> bytes:
        """
        Generate a PDF report from analysis results
        
        Args:
            analysis_results: Complete analysis results
            file_name: Base name for the report
            
        Returns:
            PDF as bytes
        """
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        try:
            # Add pages
            self._add_cover_page(analysis_results, file_name)
            self._add_executive_summary(analysis_results)
            self._add_risk_analysis(analysis_results)
            self._add_key_findings(analysis_results)
            self._add_recommendations(analysis_results)
            self._add_disclaimer()
        except Exception as e:
            # On any error, add a simple error page
            self.pdf = FPDF()
            self.pdf.add_page()
            self.pdf.set_font("Helvetica", "B", 16)
            self.pdf.cell(0, 10, "Contract Analysis Report", ln=True, align="C")
            self.pdf.set_font("Helvetica", "", 12)
            self.pdf.cell(0, 20, "", ln=True)
            self.pdf.cell(0, 10, f"Document: {self._sanitize_text(file_name)}", ln=True)
            self.pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
            self.pdf.cell(0, 20, "", ln=True)
            self.pdf.cell(0, 10, "Note: Full report generation encountered an issue.", ln=True)
            self.pdf.cell(0, 10, "Please view the analysis in the web interface.", ln=True)
        
        # Return as bytes
        return bytes(self.pdf.output())
    
    def _add_cover_page(self, results: Dict, file_name: str):
        """Add cover page"""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_font("Helvetica", "B", 24)
        self.pdf.cell(0, 60, "", ln=True)  # Spacing
        self.pdf.cell(0, 15, "CONTRACT ANALYSIS REPORT", ln=True, align="C")
        
        # File name
        self.pdf.set_font("Helvetica", "", 14)
        self.pdf.cell(0, 10, f"Document: {file_name}", ln=True, align="C")
        
        # Date
        self.pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        
        # Risk indicator
        report = results.get("report", {})
        summary = report.get("executive_summary", {})
        risk_score = summary.get("risk_score", 0)
        risk_level = summary.get("overall_status", "UNKNOWN")
        
        self.pdf.cell(0, 30, "", ln=True)  # Spacing
        self.pdf.set_font("Helvetica", "B", 18)
        
        color_map = {
            "HIGH_RISK": (244, 67, 54),
            "MODERATE_RISK": (255, 152, 0),
            "LOW_RISK": (76, 175, 80)
        }
        color = color_map.get(risk_level, (158, 158, 158))
        self.pdf.set_text_color(*color)
        self.pdf.cell(0, 15, f"Risk Score: {risk_score}/10 ({risk_level.replace('_', ' ')})", ln=True, align="C")
        self.pdf.set_text_color(0, 0, 0)
    
    def _add_executive_summary(self, results: Dict):
        """Add executive summary page"""
        self.pdf.add_page()
        
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, "EXECUTIVE SUMMARY", ln=True)
        self.pdf.ln(5)
        
        report = results.get("report", {})
        summary = report.get("executive_summary", {})
        
        self.pdf.set_font("Helvetica", "", 11)
        
        # One-liner
        one_liner = summary.get("one_liner", "")
        if one_liner:
            self.pdf.multi_cell(0, 7, self._sanitize_text(one_liner))
            self.pdf.ln(5)
        
        # Key metrics
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.cell(0, 10, "Key Metrics:", ln=True)
        self.pdf.set_font("Helvetica", "", 11)
        
        metrics = [
            f"Risk Score: {summary.get('risk_score', 0)}/10",
            f"Compliance Score: {summary.get('compliance_score', 0)}%",
            f"High Risk Items: {summary.get('high_risk_items', 0)}",
        ]
        
        for metric in metrics:
            self.pdf.cell(0, 7, f"  - {metric}", ln=True)
        
        # Contract type
        contract_type = results.get("contract_type", {}).get("primary_type", "unknown")
        self.pdf.cell(0, 7, f"  - Contract Type: {contract_type.replace('_', ' ').title()}", ln=True)
    
    def _add_risk_analysis(self, results: Dict):
        """Add risk analysis section"""
        self.pdf.add_page()
        
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, "RISK ANALYSIS", ln=True)
        self.pdf.ln(5)
        
        # Detected clause types
        clause_detections = results.get("clause_detections", {})
        
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.cell(0, 10, "Detected Risky Clause Types:", ln=True)
        self.pdf.set_font("Helvetica", "", 11)
        
        for clause_type, detection in clause_detections.items():
            if detection.get("found"):
                count = detection.get("count", 0)
                self.pdf.cell(0, 7, f"  - {clause_type.replace('_', ' ').title()}: {count} found", ln=True)
    
    def _add_key_findings(self, results: Dict):
        """Add key findings section"""
        self.pdf.add_page()
        
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, "KEY FINDINGS", ln=True)
        self.pdf.ln(5)
        
        report = results.get("report", {})
        findings = report.get("key_findings", [])
        
        self.pdf.set_font("Helvetica", "", 11)
        
        for i, finding in enumerate(findings[:10], 1):
            severity = finding.get("severity", "MEDIUM")
            category = self._sanitize_text(finding.get("category", "General"))
            description = self._sanitize_text(finding.get("description", "")[:200])
            
            self.pdf.set_font("Helvetica", "B", 11)
            self.pdf.cell(0, 7, f"{i}. [{severity}] {category}", ln=True)
            self.pdf.set_font("Helvetica", "", 10)
            if description.strip():
                self.pdf.multi_cell(0, 6, f"   {description}")
            self.pdf.ln(3)
    
    def _add_recommendations(self, results: Dict):
        """Add recommendations section"""
        self.pdf.add_page()
        
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, "RECOMMENDATIONS", ln=True)
        self.pdf.ln(5)
        
        report = results.get("report", {})
        recommendations = report.get("recommendations", [])
        next_steps = report.get("next_steps", [])
        
        # Recommendations
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.cell(0, 10, "Key Recommendations:", ln=True)
        self.pdf.set_font("Helvetica", "", 11)
        
        for rec in recommendations[:8]:
            action = self._sanitize_text(rec.get("action", "")[:150])
            if action.strip():
                self.pdf.multi_cell(0, 6, f"  - {action}")
        
        self.pdf.ln(5)
        
        # Next steps
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.cell(0, 10, "Next Steps:", ln=True)
        self.pdf.set_font("Helvetica", "", 11)
        
        for step in next_steps:
            sanitized_step = self._sanitize_text(step)
            if sanitized_step.strip():
                self.pdf.multi_cell(0, 6, sanitized_step)
    
    def _add_disclaimer(self):
        """Add disclaimer page"""
        self.pdf.add_page()
        
        self.pdf.set_font("Helvetica", "B", 16)
        self.pdf.cell(0, 10, "DISCLAIMER", ln=True)
        self.pdf.ln(10)
        
        self.pdf.set_font("Helvetica", "", 11)
        
        disclaimer = """
This report has been generated by an automated contract analysis tool and is provided for 
informational purposes only. It does not constitute legal advice.

The analysis is based on pattern matching, natural language processing, and AI-assisted 
interpretation. While efforts have been made to ensure accuracy, the tool may not identify 
all relevant issues or may flag items that are not actually problematic in your specific context.

IMPORTANT:
- This report should not be used as a substitute for professional legal advice
- Always consult a qualified lawyer before signing important contracts
- The risk scores and assessments are indicative and should be verified by a legal professional
- Laws and regulations may vary by jurisdiction and may have changed since this analysis

For important business decisions or contracts involving significant value, we strongly 
recommend engaging qualified legal counsel.
        """
        
        self.pdf.multi_cell(0, 6, disclaimer.strip())
        
        # Generation info
        self.pdf.ln(10)
        self.pdf.set_font("Helvetica", "I", 9)
        self.pdf.cell(0, 6, f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        self.pdf.cell(0, 6, "Contract Analysis & Risk Assessment Bot v1.0", ln=True)
