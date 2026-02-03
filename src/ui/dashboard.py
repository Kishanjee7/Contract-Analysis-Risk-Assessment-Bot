"""
Dashboard Layout
Main dashboard for contract analysis results
"""
import streamlit as st
from typing import Dict


class Dashboard:
    """Main dashboard for displaying analysis results"""
    
    @staticmethod
    def render(analysis_results: Dict):
        """Render the full analysis dashboard"""
        
        # Executive Summary Section
        Dashboard._render_executive_summary(analysis_results)
        
        st.markdown("---")
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Risk Analysis",
            "📑 Clause Breakdown", 
            "⚖️ Compliance",
            "📋 Extracted Info",
            "💡 Recommendations"
        ])
        
        with tab1:
            Dashboard._render_risk_analysis(analysis_results)
        
        with tab2:
            Dashboard._render_clause_breakdown(analysis_results)
        
        with tab3:
            Dashboard._render_compliance(analysis_results)
        
        with tab4:
            Dashboard._render_extracted_info(analysis_results)
        
        with tab5:
            Dashboard._render_recommendations(analysis_results)
    
    @staticmethod
    def _render_executive_summary(results: Dict):
        """Render executive summary section"""
        st.markdown("## 📋 Executive Summary")
        
        report = results.get("report", {})
        summary = report.get("executive_summary", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = summary.get("risk_score", 0)
            color = "🔴" if score >= 7 else "🟡" if score >= 4 else "🟢"
            st.metric("Risk Score", f"{color} {score}/10")
        
        with col2:
            compliance = summary.get("compliance_score", 0)
            st.metric("Compliance", f"{compliance}%")
        
        with col3:
            high_risk = summary.get("high_risk_items", 0)
            st.metric("High Risk Items", high_risk)
        
        with col4:
            contract_type = results.get("contract_type", {}).get("primary_type", "unknown")
            st.metric("Contract Type", contract_type.replace("_", " ").title())
        
        # Status message
        status = summary.get("overall_status", "UNKNOWN")
        one_liner = summary.get("one_liner", "")
        
        if status == "HIGH_RISK":
            st.error(f"⚠️ {one_liner}")
        elif status == "MODERATE_RISK":
            st.warning(f"⚡ {one_liner}")
        else:
            st.success(f"✅ {one_liner}")
    
    @staticmethod
    def _render_risk_analysis(results: Dict):
        """Render risk analysis section"""
        st.markdown("### Risk Assessment")
        
        risk_score = results.get("risk_score", {})
        clause_detections = results.get("clause_detections", {})
        
        # Severity distribution
        severity = risk_score.get("severity_distribution", {})
        if severity:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Critical", severity.get("critical", 0))
            with col2:
                st.metric("High", severity.get("high", 0))
            with col3:
                st.metric("Medium", severity.get("medium", 0))
            with col4:
                st.metric("Low", severity.get("low", 0))
        
        # Detected clause types
        st.markdown("### Detected Risky Clause Types")
        
        for clause_type, detection in clause_detections.items():
            if detection.get("found"):
                count = detection.get("count", 0)
                rec = detection.get("recommendation", "")
                
                with st.expander(f"🔍 {clause_type.replace('_', ' ').title()} ({count} found)"):
                    st.write(f"**Recommendation:** {rec}")
                    
                    for i, finding in enumerate(detection.get("findings", [])[:3]):
                        st.markdown(f"**Finding {i+1}:**")
                        st.text(finding.get("context", finding.get("text", ""))[:300])
    
    @staticmethod
    def _render_clause_breakdown(results: Dict):
        """Render clause-by-clause breakdown"""
        st.markdown("### Clause-by-Clause Analysis")
        
        clauses = results.get("clauses", [])
        
        if not clauses:
            st.info("No clauses extracted from the document.")
            return
        
        # Filter options
        filter_option = st.selectbox(
            "Filter clauses by risk level:",
            ["All", "High Risk Only", "Medium Risk Only", "Low Risk Only"]
        )
        
        for clause in clauses:
            risk_level = clause.get("risk_level", "low")
            
            # Apply filter
            if filter_option == "High Risk Only" and risk_level != "high":
                continue
            elif filter_option == "Medium Risk Only" and risk_level != "medium":
                continue
            elif filter_option == "Low Risk Only" and risk_level != "low":
                continue
            
            icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            icon = icons.get(risk_level, "⚪")
            
            with st.expander(f"{icon} Clause {clause.get('clause_number', '')} - Score: {clause.get('score', 0)}/10"):
                st.markdown(f"**Type:** {clause.get('clause_type', 'general').replace('_', ' ').title()}")
                st.markdown("**Text:**")
                st.text(clause.get("text", "")[:500])
                
                if clause.get("explanation"):
                    st.markdown("**Explanation:**")
                    st.info(clause["explanation"])
    
    @staticmethod
    def _render_compliance(results: Dict):
        """Render compliance check results"""
        st.markdown("### Compliance Check")
        
        compliance = results.get("compliance", {})
        
        score = compliance.get("compliance_score", 0)
        st.progress(score / 100, text=f"Compliance Score: {score}%")
        
        # Issues
        issues = compliance.get("issues", [])
        if issues:
            st.markdown("#### ⚠️ Issues Found")
            for issue in issues:
                st.warning(issue)
        
        # Warnings
        warnings = compliance.get("warnings", [])
        if warnings:
            st.markdown("#### ⚡ Warnings")
            for warning in warnings:
                st.info(warning)
        
        # Recommendations
        recommendations = compliance.get("recommendations", [])
        if recommendations:
            st.markdown("#### 💡 Recommendations")
            for rec in recommendations:
                st.success(rec)
        
        if not issues and not warnings:
            st.success("✅ No major compliance issues detected!")
    
    @staticmethod
    def _render_extracted_info(results: Dict):
        """Render extracted information"""
        st.markdown("### Extracted Information")
        
        entities = results.get("entities", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👥 Parties")
            parties = entities.get("parties", [])
            if parties:
                for party in parties:
                    st.write(f"- {party.get('name', '')} ({party.get('type', '')})")
            else:
                st.write("No parties identified")
            
            st.markdown("#### 💰 Financial Terms")
            amounts = entities.get("amounts", [])
            if amounts:
                for amount in amounts:
                    st.write(f"- {amount.get('currency', 'INR')} {amount.get('value', '')}")
            else:
                st.write("No amounts identified")
        
        with col2:
            st.markdown("#### 📅 Key Dates")
            dates = entities.get("dates", [])
            if dates:
                for date in dates[:5]:
                    st.write(f"- {date.get('raw', '')}")
            else:
                st.write("No dates identified")
            
            st.markdown("#### ⏱️ Durations")
            durations = entities.get("durations", [])
            if durations:
                for duration in durations[:5]:
                    st.write(f"- {duration.get('raw', '')}")
            else:
                st.write("No durations identified")
        
        st.markdown("#### ⚖️ Jurisdictions")
        jurisdictions = entities.get("jurisdictions", [])
        if jurisdictions:
            st.write(", ".join(jurisdictions))
        else:
            st.write("No jurisdiction specified")
    
    @staticmethod
    def _render_recommendations(results: Dict):
        """Render recommendations section"""
        st.markdown("### Recommendations & Next Steps")
        
        report = results.get("report", {})
        recommendations = report.get("recommendations", [])
        next_steps = report.get("next_steps", [])
        
        if recommendations:
            st.markdown("#### 💡 Key Recommendations")
            for rec in recommendations[:10]:
                priority = rec.get("priority", "medium")
                icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.markdown(f"{icon} **{rec.get('category', '')}:** {rec.get('action', '')}")
        
        if next_steps:
            st.markdown("#### 📝 Recommended Next Steps")
            for step in next_steps:
                st.markdown(step)
        
        # Disclaimer
        st.markdown("---")
        st.warning("""
        ⚠️ **Important Disclaimer**
        
        This analysis is provided for informational purposes only and does not constitute legal advice.
        For important contracts or if you have concerns, please consult a qualified legal professional.
        """)
