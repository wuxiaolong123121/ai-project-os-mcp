"""
Governance Engine - Core v2.5 implementation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .violation import Violation, ViolationLevel, ViolationType
from .policy_engine import PolicyEngine
from .score_engine import ScoreEngine
from .state_manager import StateManager


class GovernanceEngine:
    """
    Governance Engine - The core of v2.5 implementation
    
    This is the single entry point for all governance operations.
    It coordinates Policy, Audit, Score, and State engines.
    
    Key responsibilities:
    - Enforce policy compliance
    - Generate and track violations
    - Maintain audit trail
    - Calculate governance score
    - Update project state
    """
    
    def __init__(self, project_root: str):
        """
        Initialize Governance Engine
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        
        # Initialize sub-engines
        self.policy_engine = PolicyEngine(project_root)
        self.audit_engine = AuditEngine(project_root)
        self.score_engine = ScoreEngine()
        self.state_manager = StateManager(project_root)
        
        # Load initial state
        self.state = self.state_manager.load_state()
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a governance event
        
        Args:
            event: Governance event with required fields: event_type, data
            
        Returns:
            Processed event result with violations, score, and audit info
        """
        # Validate event structure
        if not self._validate_event(event):
            violation = Violation(
                level=ViolationLevel.CRITICAL,
                type=ViolationType.INVALID_EVENT,
                message="Invalid event structure",
                details={"event": event}
            )
            return self._create_result(event, [violation.to_dict()])
        
        # Generate event ID if not present
        if "event_id" not in event:
            event["event_id"] = self._generate_event_id()
        
        # Set timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # 1. Check policy compliance
        violations = self._check_policy_compliance(event)
        
        # 2. Create audit record
        audit_record = self.audit_engine.create_audit_record(event, violations)
        
        # 3. Update governance score
        score = self.score_engine.update(event, violations, self.state)
        
        # 4. Update project state
        self._update_state(event, violations, audit_record, score)
        
        # 5. Create result
        result = self._create_result(event, violations, audit_record, score)
        
        return result
    
    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Validate event structure
        
        Args:
            event: Event to validate
            
        Returns:
            True if valid, False otherwise
        """
        return "event_type" in event and "data" in event
    
    def _generate_event_id(self) -> str:
        """
        Generate a unique event ID
        
        Returns:
            Unique event ID
        """
        return f"event-{datetime.utcnow().timestamp()}-{hash(str(datetime.utcnow()))}"
    
    def _check_policy_compliance(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if event complies with policies
        
        Args:
            event: Event to check
            
        Returns:
            List of violations
        """
        violations = []
        
        # Get applicable policies for this event type
        policies = self.policy_engine.get_applicable_policies(event["event_type"])
        
        # Check each policy
        for policy in policies:
            policy_violations = self.policy_engine.check_policy(policy, event, self.state)
            violations.extend(policy_violations)
        
        return violations
    
    def _update_state(self, event: Dict[str, Any], violations: List[Dict[str, Any]], 
                     audit_record: Dict[str, Any], score: Dict[str, Any]) -> None:
        """
        Update project state based on event and violations
        
        Args:
            event: Processed event
            violations: Detected violations
            audit_record: Created audit record
            score: Updated governance score
        """
        # Update state with event info
        update = {
            "last_event": event,
            "last_audit": audit_record,
            "current_score": score,
            "violation_count": {
                "critical": len([v for v in violations if v["level"] == ViolationLevel.CRITICAL]),
                "major": len([v for v in violations if v["level"] == ViolationLevel.MAJOR]),
                "minor": len([v for v in violations if v["level"] == ViolationLevel.MINOR])
            }
        }
        
        # Update state based on event type
        if event["event_type"] == "STAGE_CHANGE":
            update["stage"] = event["data"].get("stage")
        
        # Save updated state
        self.state = self.state_manager.update_state(update)
    
    def _create_result(self, event: Dict[str, Any], violations: List[Dict[str, Any]], 
                      audit_record: Optional[Dict[str, Any]] = None,
                      score: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create result dictionary
        
        Args:
            event: Processed event
            violations: Detected violations
            audit_record: Audit record
            score: Governance score
            
        Returns:
            Result dictionary
        """
        result = {
            "event_id": event["event_id"],
            "status": "FAILED" if any(v["level"] in [ViolationLevel.CRITICAL, ViolationLevel.MAJOR] for v in violations) else "PASSED",
            "violations": violations,
            "violation_count": {
                "critical": len([v for v in violations if v["level"] == ViolationLevel.CRITICAL]),
                "major": len([v for v in violations if v["level"] == ViolationLevel.MAJOR]),
                "minor": len([v for v in violations if v["level"] == ViolationLevel.MINOR])
            }
        }
        
        if audit_record:
            result["audit_record"] = audit_record
        
        if score:
            result["score"] = score
        
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current project state
        
        Returns:
            Current project state
        """
        return self.state
    
    def get_audit_history(self) -> List[Dict[str, Any]]:
        """
        Get audit history
        
        Returns:
            List of audit records
        """
        return self.audit_engine.get_audit_history()
    
    def get_score_history(self) -> List[Dict[str, Any]]:
        """
        Get score history
        
        Returns:
            List of score records
        """
        return self.score_engine.get_score_history()
    
    def get_current_score(self) -> Dict[str, Any]:
        """
        Get current governance score
        
        Returns:
            Current governance score
        """
        return self.score_engine.get_score()
    
    def check_policy(self, policy_name: str, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check a specific policy against an event
        
        Args:
            policy_name: Name of the policy to check
            event: Event to check
            
        Returns:
            List of violations
        """
        policy = self.policy_engine.get_policy(policy_name)
        if not policy:
            return [Violation(
                level=ViolationLevel.MINOR,
                type=ViolationType.POLICY_NOT_FOUND,
                message=f"Policy {policy_name} not found"
            ).to_dict()]
        
        return self.policy_engine.check_policy(policy, event, self.state)
    
    def load_policies(self) -> List[Dict[str, Any]]:
        """
        Load all policies
        
        Returns:
            List of loaded policies
        """
        return self.policy_engine.load_policies()
    
    def validate_state(self) -> List[Dict[str, Any]]:
        """
        Validate current state against all policies
        
        Returns:
            List of violations
        """
        violations = []
        policies = self.policy_engine.load_policies()
        
        for policy in policies:
            event = {
                "event_type": "STATE_VALIDATION",
                "data": {"state": self.state}
            }
            policy_violations = self.policy_engine.check_policy(policy, event, self.state)
            violations.extend(policy_violations)
        
        return violations