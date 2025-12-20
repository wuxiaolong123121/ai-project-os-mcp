"""
Governance Engine - Core v2.5 implementation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .events import GovernanceEvent, EventType
from .event_store import get_event_store
from .violation import GovernanceViolation, ViolationLevel
from .policy_engine import PolicyEngine, ActionType, Action
from .score_engine import ScoreEngine
from .state_manager import StateManager
from .trigger_engine import TriggerEngine


class GovernanceEngine:
    """
    Governance Engine - The single entry point for all governance operations
    
    This is the core of v2.5 implementation and follows the Single Gate principle.
    All governance operations must pass through this engine.
    
    Key responsibilities:
    - Enforce policy compliance
    - Generate and track violations
    - Maintain audit trail
    - Calculate governance score
    - Update project state
    - Ensure structural non-bypassability
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
        self.score_engine = ScoreEngine()
        self.state_manager = StateManager(project_root)
        self.trigger_engine = TriggerEngine()
        self.event_store = get_event_store()
        
        # Load initial state
        self.state = self.state_manager.load_state()
        
        # Ensure required state fields exist
        self._initialize_state()
    
    def _initialize_state(self):
        """
        Ensure required state fields exist
        """
        if "score" not in self.state:
            self.state["score"] = {
                "global": 100,  # Irreversible,跨阶段
                "stage": 100    # 阶段内评分，阶段切换时重置
            }
        
        if "is_frozen" not in self.state:
            self.state["is_frozen"] = False
        
        if "events" not in self.state:
            self.state["events"] = []
    
    def handle_event(self, event: GovernanceEvent) -> Dict[str, Any]:
        """
        Process a governance event - the single entry point for all governance operations
        
        Args:
            event: Governance event with actor identity
            
        Returns:
            Processed event result with violations, score, and actions
        """
        # 1. Validate actor identity (必改：无 Actor 的 Event 直接拒绝)
        if not event.actor:
            violation = GovernanceViolation(
                level=ViolationLevel.CRITICAL,
                rule_id="anonymous_event",
                event_id=event.id,
                actor_id="anonymous",  # 无 Actor 时使用默认值
                message="Anonymous event is not allowed"
            )
            return {
                "event_id": event.id,
                "status": "FAILED",
                "violations": [violation.model_dump()],
                "actions": []
            }
        
        # 2. Check frozen state (必改：Frozen 状态下，只接受 UNFREEZE / STATUS 事件)
        if self.state["is_frozen"]:
            if event.event_type not in [EventType.UNFREEZE, EventType.STATUS]:
                violation = GovernanceViolation(
                    level=ViolationLevel.CRITICAL,
                    rule_id="frozen_project",
                    event_id=event.id,
                    actor_id=event.actor.id,
                    message="Project is frozen, only UNFREEZE and STATUS events are allowed"
                )
                return {
                    "event_id": event.id,
                    "status": "FAILED",
                    "violations": [violation.model_dump()],
                    "actions": []
                }
        
        # 3. Save event to EventStore (必改：EventStore = 不可修改 append-only)
        self.event_store.append(event)
        
        # 4. Detect violations using TriggerEngine (Phase A2)
        violations = self.trigger_engine.evaluate(event, self.state)
        
        # 5. Decide actions using PolicyEngine (Phase A3)
        actions = self.policy_engine.decide(violations)
        
        # 6. Update score using ScoreEngine (Phase B1)
        score_update = self.score_engine.update(event, violations, self.state)
        
        # 7. Apply actions and update state in transaction (Phase A3)
        with self._governance_transaction():
            # 检查是否有 CRITICAL 违规，如果有，直接冻结项目
            has_critical_violation = any(v["level"] == ViolationLevel.CRITICAL for v in violations)
            if has_critical_violation:
                self.state["is_frozen"] = True
            
            self._apply_actions(actions, event)
            self._update_state(event, violations, actions, score_update)
            # 8. Write audit record (新增：必改 - 所有事件必须有审计记录)
            self._write_audit(event, violations, actions, score_update)
        
        # 9. Create result
        result = {
            "event_id": event.id,
            "status": "FAILED" if any(v["level"] in [ViolationLevel.CRITICAL, ViolationLevel.MAJOR] for v in violations) else "PASSED",
            "violations": violations,
            "actions": actions,
            "score": score_update
        }
        
        return result
    
    def _governance_transaction(self):
        """
        Governance transaction context manager to ensure atomicity
        
        Returns:
            Context manager for governance transactions
        """
        engine = self
        
        class GovernanceTransaction:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    # Commit: save state to disk
                    engine.state_manager.save_state(engine.state)
                else:
                    # Rollback: do nothing, state remains in memory
                    pass
        
        return GovernanceTransaction()
    
    def _apply_actions(self, actions: List[Action], event: GovernanceEvent):
        """
        Apply actions to the system
        
        Args:
            actions: List of structured actions to apply
            event: Original event
        """
        for action in actions:
            if action.type == ActionType.FREEZE_PROJECT:
                self.state["is_frozen"] = True
            elif action.type == ActionType.UNFREEZE_PROJECT:
                self.state["is_frozen"] = False
            
        # 特殊处理：如果是 FREEZE_REQUEST 事件，直接冻结项目
        if event.event_type == EventType.FREEZE_REQUEST:
            self.state["is_frozen"] = True
        # 特殊处理：如果是 UNFREEZE 事件，直接解冻项目
        elif event.event_type == EventType.UNFREEZE:
            self.state["is_frozen"] = False
    
    def _update_state(self, event: GovernanceEvent, violations: List[Dict[str, Any]], 
                     actions: List[Dict[str, Any]], score_update: Dict[str, Any]):
        """
        Update project state based on event, violations, and actions
        
        Args:
            event: Processed event
            violations: Detected violations
            actions: Applied actions
            score_update: Updated score
        """
        # Update score
        self.state["score"] = score_update
        
        # Add event to state (for quick access, but EventStore is the source of truth)
        self.state["events"].append({
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "actor_id": event.actor.id
        })
        
        # Update violation count
        violation_count = {
            "critical": len([v for v in violations if v["level"] == ViolationLevel.CRITICAL]),
            "major": len([v for v in violations if v["level"] == ViolationLevel.MAJOR]),
            "minor": len([v for v in violations if v["level"] == ViolationLevel.MINOR])
        }
        self.state["violation_count"] = violation_count
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current project state
        
        Returns:
            Current project state
        """
        return self.state
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get event history from EventStore
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self.event_store.list()[:limit]
        return [event.model_dump() for event in events]
    
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
    
    def _update_state(self, event: GovernanceEvent, violations: List[Dict[str, Any]], 
                     actions: List[Dict[str, Any]], score_update: Dict[str, Any]):
        """
        Update project state based on event, violations, and actions
        
        Args:
            event: Processed event
            violations: Detected violations
            actions: Applied actions
            score_update: Updated score
        """
        # Update score
        self.state["score"] = score_update
        
        # Add event to state (for quick access, but EventStore is the source of truth)
        self.state["events"].append({
            "event_id": event.id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "actor_id": event.actor.id
        })
        
        # Update violation count
        violation_count = {
            "critical": len([v for v in violations if v["level"] == ViolationLevel.CRITICAL]),
            "major": len([v for v in violations if v["level"] == ViolationLevel.MAJOR]),
            "minor": len([v for v in violations if v["level"] == ViolationLevel.MINOR])
        }
        self.state["violation_count"] = violation_count
    
    def _write_audit(self, event: GovernanceEvent, violations: List[Dict[str, Any]], 
                    actions: List[Dict[str, Any]], score_update: Dict[str, Any]):
        """
        Write audit record for the event
        
        Args:
            event: Processed event
            violations: Detected violations
            actions: Applied actions
            score_update: Updated score
        
        🔒 铁律：所有事件必须有审计记录，且必须引用event_id
        """
        # Ensure audit field exists in state
        if "audit" not in self.state:
            self.state["audit"] = []
        
        # Create audit record
        audit_record = {
            "event_id": event.id,
            "event_type": event.event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "actor": {
                "id": event.actor.id,
                "role": event.actor.role,
                "role_type": event.actor.role_type,
                "source": event.actor.source
            },
            "status": "FAILED" if any(v["level"] in [ViolationLevel.CRITICAL, ViolationLevel.MAJOR] for v in violations) else "PASSED",
            "violations": violations,
            "actions": actions,
            "score_change": {
                "global": score_update["global"] - self.state["score"]["global"] if "global" in self.state["score"] else score_update["global"] - 100,
                "stage": score_update["stage"] - self.state["score"]["stage"] if "stage" in self.state["score"] else score_update["stage"] - 100
            },
            "score": score_update
        }
        
        # Add audit record to state (for quick access, but EventStore is the source of truth)
        self.state["audit"].append(audit_record)
        
        # Save updated state
        self.state_manager.save_state(self.state)
    
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