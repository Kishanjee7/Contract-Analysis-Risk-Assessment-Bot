"""
Reusable UI Components for Streamlit
"""
import streamlit as st
from typing import Dict, List


class UIComponents:
    """Reusable UI components for the contract analyzer"""
    
    @staticmethod
    def render_risk_score_card(score: float, level: str):
        """Render a risk score card with visual indicator"""
        colors = {
            "low": "#4CAF50",      # Green
            "medium": "#FF9800",   # Orange
            "high": "#F44336"      # Red
        }
        
        color = colors.get(level, "#9E9E9E")
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        ">
            <div style="font-size: 14px; color: #666; margin-bottom: 5px;">RISK SCORE</div>
            <div style="font-size: 42px; font-weight: bold; color: {color};">{score}/10</div>
            <div style="font-size: 16px; color: {color}; text-transform: uppercase;">{level} RISK</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_cards(metrics: List[Dict]):
        """Render a row of metric cards"""
        cols = st.columns(len(metrics))
        
        for col, metric in zip(cols, metrics):
            with col:
                st.metric(
                    label=metric.get("label", ""),
                    value=metric.get("value", ""),
                    delta=metric.get("delta"),
                    delta_color=metric.get("delta_color", "normal")
                )
    
    @staticmethod
    def render_finding_card(finding: Dict, severity: str = "medium"):
        """Render a finding/issue card"""
        icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        
        colors = {
            "high": "#FFEBEE",
            "medium": "#FFF8E1",
            "low": "#E8F5E9"
        }
        
        icon = icons.get(severity.lower(), "⚪")
        bg_color = colors.get(severity.lower(), "#F5F5F5")
        
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        ">
            <div style="font-weight: bold; margin-bottom: 8px;">
                {icon} {finding.get('category', 'Finding')}
            </div>
            <div style="color: #333; margin-bottom: 8px;">
                {finding.get('description', '')}
            </div>
            <div style="font-size: 12px; color: #666; font-style: italic;">
                💡 {finding.get('recommendation', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_clause_card(clause: Dict, expanded: bool = False):
        """Render a clause analysis card"""
        risk_level = clause.get("risk_level", "low")
        
        icons = {
            "high": "⚠️",
            "medium": "⚡",
            "low": "✓"
        }
        
        icon = icons.get(risk_level, "📄")
        
        with st.expander(
            f"{icon} Clause {clause.get('clause_number', '')} - {clause.get('heading', 'Untitled')[:50]}",
            expanded=expanded
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Clause Text:**")
                st.text(clause.get("text", "")[:500])
                
                if clause.get("explanation"):
                    st.markdown("**Plain Language Explanation:**")
                    st.info(clause["explanation"])
            
            with col2:
                score = clause.get("score", 0)
                st.markdown(f"**Risk Score:** {score}/10")
                st.markdown(f"**Type:** {clause.get('clause_type', 'general').replace('_', ' ').title()}")
    
    @staticmethod
    def render_entity_tags(entities: Dict):
        """Render extracted entities as tags"""
        st.markdown("### 📋 Extracted Information")
        
        # Parties
        parties = entities.get("parties", [])
        if parties:
            st.markdown("**Parties:**")
            party_html = " ".join([
                f'<span style="background-color: #E3F2FD; padding: 4px 8px; border-radius: 4px; margin: 2px;">{p.get("name", "")}</span>'
                for p in parties
            ])
            st.markdown(party_html, unsafe_allow_html=True)
        
        # Amounts
        amounts = entities.get("amounts", [])
        if amounts:
            st.markdown("**Financial Terms:**")
            amount_html = " ".join([
                f'<span style="background-color: #E8F5E9; padding: 4px 8px; border-radius: 4px; margin: 2px;">{a.get("currency", "")} {a.get("value", "")}</span>'
                for a in amounts
            ])
            st.markdown(amount_html, unsafe_allow_html=True)
        
        # Dates
        dates = entities.get("dates", [])
        if dates:
            st.markdown("**Key Dates:**")
            date_html = " ".join([
                f'<span style="background-color: #FFF3E0; padding: 4px 8px; border-radius: 4px; margin: 2px;">{d.get("raw", "")}</span>'
                for d in dates[:5]
            ])
            st.markdown(date_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_indicator(current: int, total: int, label: str = "Processing"):
        """Render a progress indicator"""
        progress = current / total if total > 0 else 0
        st.progress(progress, text=f"{label}: {current}/{total}")
    
    @staticmethod
    def render_sidebar_info():
        """Render sidebar information"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📖 About")
        st.sidebar.markdown("""
        This tool helps SMEs analyze contracts by:
        - Identifying risky clauses
        - Explaining legal terms
        - Suggesting alternatives
        - Checking compliance
        """)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚠️ Disclaimer")
        st.sidebar.markdown("""
        This tool provides general guidance only.
        It is not a substitute for professional legal advice.
        Always consult a qualified lawyer for important contracts.
        """)
