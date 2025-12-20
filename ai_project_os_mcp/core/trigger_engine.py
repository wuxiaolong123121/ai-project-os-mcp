"""
Trigger Engine - Evaluates events and detects violations
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .events import EventType
from .violation import GovernanceViolation, ViolationLevel


class TriggerCondition(BaseModel):
    """Trigger condition definition"""
    event: EventType = Field(..., description="Type of event to trigger on")
    condition: str = Field(..., description="Condition expression to evaluate")


class GovernanceTrigger(BaseModel):
    """Governance trigger definition"""
    id: str = Field(..., description="Unique trigger ID")
    when: TriggerCondition = Field(..., description="When to trigger")
    violation: ViolationLevel = Field(..., description="Violation level when triggered")
    message: str = Field(..., description="Violation message")
    enabled: bool = Field(default=True, description="Whether the trigger is enabled")


class TriggerEngine:
    """
    Trigger Engine - Evaluates events and detects violations
    
    This is a private module - do not use directly outside governance_engine.py
    """
    
    def __init__(self):
        self.triggers = self._load_default_triggers()
    
    def _load_default_triggers(self) -> List[GovernanceTrigger]:
        """Load default governance triggers"""
        return [
            GovernanceTrigger(
                id="code_outside_s5",
                when=TriggerCondition(
                    event=EventType.CODE_GENERATION,
                    condition="stage != 'S5'"
                ),
                violation=ViolationLevel.CRITICAL,
                message="Code generation outside S5 stage",
                enabled=True
            ),
            GovernanceTrigger(
                id="audit_missing",
                when=TriggerCondition(
                    event=EventType.AUDIT_MISSING,
                    condition="audit_required == True"
                ),
                violation=ViolationLevel.MAJOR,
                message="Audit required but missing",
                enabled=True
            ),
            GovernanceTrigger(
                id="arch_violation",
                when=TriggerCondition(
                    event=EventType.ARCH_VIOLATION,
                    condition="true"
                ),
                violation=ViolationLevel.MINOR,
                message="Architecture violation detected",
                enabled=True
            )
        ]
    
    def evaluate(self, event: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate event against triggers and detect violations
        
        Args:
            event: Governance event to evaluate
            state: Current project state
            
        Returns:
            List of detected violations
        """
        violations = []
        
        for trigger in self.triggers:
            if not trigger.enabled:
                continue
            
            if self._should_trigger(trigger, event, state):
                violation = self._create_violation(trigger, event)
                violations.append(violation.dict())
        
        return violations
    
    def _should_trigger(self, trigger: GovernanceTrigger, event: Dict[str, Any], state: Dict[str, Any]) -> bool:
        """Check if a trigger should fire for the given event and state"""
        # Check event type match
        if trigger.when.event != event.get("event_type"):
            return False
        
        # Check condition
        condition = trigger.when.condition
        context = {**event, **state}
        
        try:
            # Simple condition evaluation
            # For production, use a safer evaluator
            return eval(condition, {}, context)
        except Exception:
            # If condition evaluation fails, return False to be safe
            return False
    
    def _create_violation(self, trigger: GovernanceTrigger, event: Dict[str, Any]) -> GovernanceViolation:
        """Create a violation object from a trigger and event"""
        return GovernanceViolation(
            level=trigger.violation,
            rule_id=trigger.id,
            event_id=event.get("event_id"),
            actor_id=event.get("actor", {}).get("id"),
            message=trigger.message
        )
    
    def get_triggers(self) -> List[Dict[str, Any]]:
        """Get list of registered triggers"""
        return [trigger.dict() for trigger in self.triggers]
    
    def add_trigger(self, trigger: GovernanceTrigger):
        """Add a new trigger"""
        self.triggers.append(trigger)
    
    def remove_trigger(self, trigger_id: str):
        """Remove a trigger by ID"""
        self.triggers = [t for t in self.triggers if t.id != trigger_id]