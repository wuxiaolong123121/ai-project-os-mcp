"""
Score Engine - Governance scoring with irreversible decay
"""

from typing import Dict, Any
from enum import Enum

from .violation import ViolationLevel


class ScoreComponent(str, Enum):
    """Score component types"""
    GOVERNANCE = "governance"
    AUDIT_COVERAGE = "audit_coverage"
    COMPLIANCE = "compliance"


class ScoreEngine:
    """
    Score Engine - Calculates governance score with irreversible decay
    
    This is a private module - do not use directly outside governance_engine.py
    
    Key features:
    - Irreversible decay for violations
    - Stage-based score reset
    - Multiple score components
    - Detailed breakdown
    """
    
    def __init__(self):
        self.base_score = 100
        self.score_decay = {
            ViolationLevel.CRITICAL: -30,  # Irreversible, only reset by stage change
            ViolationLevel.MAJOR: -10,      # Irreversible, only reset by stage change
            ViolationLevel.MINOR: -2        # Irreversible, only reset by stage change
        }
        self.current_score = self.base_score
        self.score_history = []
    
    def update(self, event: Dict[str, Any], violations: list, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update governance score based on event and violations
        
        Args:
            event: Governance event
            violations: List of detected violations
            state: Current project state
            
        Returns:
            Updated score details
        """
        # Check if we need to reset the score (stage change)
        if event.get("event_type") == "STAGE_CHANGE":
            self.reset_score()
        
        # Apply score decay for violations
        for violation in violations:
            level = ViolationLevel(violation.get("level"))
            self.current_score += self.score_decay[level]
            
        # Ensure score doesn't go below 0
        self.current_score = max(0, self.current_score)
        
        # Calculate audit coverage (mock implementation)
        audit_coverage = self._calculate_audit_coverage(state)
        
        # Calculate compliance score (mock implementation)
        compliance_score = self._calculate_compliance_score(state)
        
        # Calculate final score
        final_score = {
            "governance_score": self.current_score,
            "audit_coverage": audit_coverage,
            "compliance_score": compliance_score,
            "violations": {
                "critical": len([v for v in violations if v.get("level") == ViolationLevel.CRITICAL]),
                "major": len([v for v in violations if v.get("level") == ViolationLevel.MAJOR]),
                "minor": len([v for v in violations if v.get("level") == ViolationLevel.MINOR])
            },
            "timestamp": event.get("timestamp"),
            "event_id": event.get("event_id")
        }
        
        # Add to history
        self.score_history.append(final_score)
        
        return final_score
    
    def _calculate_audit_coverage(self, state: Dict[str, Any]) -> float:
        """Calculate audit coverage percentage"""
        # Mock implementation - replace with real calculation
        # For example: total_audits / (total_items * audit_required_rate)
        return 92.5
    
    def _calculate_compliance_score(self, state: Dict[str, Any]) -> float:
        """Calculate compliance score"""
        # Mock implementation - replace with real calculation
        # For example: compliance_checked_items / total_items
        return 88.0
    
    def reset_score(self):
        """Reset score to base score (called on stage change)"""
        self.current_score = self.base_score
    
    def get_score(self) -> Dict[str, Any]:
        """Get current score"""
        if not self.score_history:
            return {
                "governance_score": self.base_score,
                "audit_coverage": 0.0,
                "compliance_score": 0.0,
                "violations": {
                    "critical": 0,
                    "major": 0,
                    "minor": 0
                }
            }
        return self.score_history[-1]
    
    def get_score_history(self) -> list:
        """Get score history"""
        return self.score_history
    
    def calculate_combined_score(self, scores: list) -> float:
        """Calculate combined score from multiple components"""
        # Weighted average of score components
        weights = {
            ScoreComponent.GOVERNANCE: 0.6,
            ScoreComponent.AUDIT_COVERAGE: 0.2,
            ScoreComponent.COMPLIANCE: 0.2
        }
        
        if not scores:
            return self.base_score
        
        latest_score = scores[-1]
        combined = (
            latest_score.get("governance_score", self.base_score) * weights[ScoreComponent.GOVERNANCE] +
            latest_score.get("audit_coverage", 0) * weights[ScoreComponent.AUDIT_COVERAGE] +
            latest_score.get("compliance_score", 0) * weights[ScoreComponent.COMPLIANCE]
        )
        
        return max(0, combined)