"""
Audit Logger
JSON-based audit trail logging for contract analyses
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import hashlib


class AuditLogger:
    """Create and manage audit trails for contract analyses"""
    
    def __init__(self, log_dir: str = None):
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path(__file__).parent.parent.parent / "audit_logs"
        
        self.log_dir.mkdir(exist_ok=True)
    
    def create_audit_entry(self, 
                          file_name: str,
                          file_hash: str,
                          analysis_type: str,
                          results: Dict,
                          user_id: str = "anonymous") -> str:
        """
        Create an audit log entry
        
        Args:
            file_name: Name of the analyzed file
            file_hash: SHA256 hash of the file
            analysis_type: Type of analysis performed
            results: Analysis results
            user_id: User identifier
            
        Returns:
            Audit entry ID
        """
        entry_id = self._generate_entry_id()
        timestamp = datetime.now().isoformat()
        
        entry = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "file_info": {
                "name": file_name,
                "hash": file_hash
            },
            "analysis_type": analysis_type,
            "results_summary": self._summarize_results(results),
            "version": "1.0"
        }
        
        # Save entry
        log_file = self.log_dir / f"{entry_id}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        
        return entry_id
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"AUDIT-{timestamp}"
    
    def _summarize_results(self, results: Dict) -> Dict:
        """Create a summary of results for the audit log"""
        summary = {}
        
        # Risk score
        if "risk_score" in results:
            summary["risk_score"] = results["risk_score"].get("composite_score")
            summary["risk_level"] = results["risk_score"].get("risk_level")
        
        # Contract type
        if "contract_type" in results:
            summary["contract_type"] = results["contract_type"].get("primary_type")
        
        # Findings count
        if "clause_detections" in results:
            detected_count = sum(
                1 for v in results["clause_detections"].values() 
                if v.get("found")
            )
            summary["risky_clauses_detected"] = detected_count
        
        return summary
    
    def get_audit_entry(self, entry_id: str) -> Optional[Dict]:
        """Retrieve an audit entry by ID"""
        log_file = self.log_dir / f"{entry_id}.json"
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_recent_entries(self, limit: int = 10) -> list:
        """Get most recent audit entries"""
        entries = []
        
        log_files = sorted(
            self.log_dir.glob("AUDIT-*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for log_file in log_files[:limit]:
            with open(log_file, 'r', encoding='utf-8') as f:
                entries.append(json.load(f))
        
        return entries
    
    def get_file_hash(self, file_bytes: bytes) -> str:
        """Calculate SHA256 hash of file"""
        return hashlib.sha256(file_bytes).hexdigest()
    
    def export_audit_trail(self, entry_ids: list = None) -> str:
        """Export audit trail entries as a formatted report"""
        if entry_ids:
            entries = [self.get_audit_entry(eid) for eid in entry_ids if eid]
            entries = [e for e in entries if e]
        else:
            entries = self.get_recent_entries(limit=100)
        
        lines = ["AUDIT TRAIL EXPORT", "=" * 50, ""]
        
        for entry in entries:
            lines.append(f"Entry ID: {entry.get('entry_id')}")
            lines.append(f"Timestamp: {entry.get('timestamp')}")
            lines.append(f"File: {entry.get('file_info', {}).get('name')}")
            lines.append(f"Analysis: {entry.get('analysis_type')}")
            
            summary = entry.get("results_summary", {})
            if summary:
                lines.append(f"Risk Score: {summary.get('risk_score', 'N/A')}")
                lines.append(f"Risk Level: {summary.get('risk_level', 'N/A')}")
            
            lines.append("-" * 30)
            lines.append("")
        
        return "\n".join(lines)
