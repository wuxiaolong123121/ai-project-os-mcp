"""
Trigger Engine - Evaluates events and detects violations
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .events import EventType, GovernanceEvent
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
    
    def evaluate(self, event: GovernanceEvent, state: Dict[str, Any]) -> List[Dict[str, Any]]:
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
                violations.append(violation.model_dump())
        
        return violations
    
    def _should_trigger(self, trigger: GovernanceTrigger, event: GovernanceEvent, state: Dict[str, Any]) -> bool:
        """
        Check if a trigger should fire for the given event and state
        
        Args:
            trigger: Governance trigger to check
            event: Governance event to evaluate
            state: Current project state
            
        Returns:
            True if the trigger should fire, False otherwise
        """
        # Check event type match
        if trigger.when.event != event.event_type:
            return False
        
        # Check condition using safe structured comparison
        condition = trigger.when.condition
        
        # Get context from event and state
        context = {
            "event_type": event.event_type,
            "actor_id": event.actor.id,
            "actor_role": event.actor.role,
            "actor_role_type": event.actor.source,  # Use source as role_type for now
            **state,  # Add state to context
            **event.payload  # Add event payload to context
        }
        
        # Safe condition evaluation using structured comparison
        return self._safe_condition_eval(condition, context)
    
    def _safe_condition_eval(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Safe condition evaluation using structured comparison
        
        Args:
            condition: Condition string to evaluate (e.g., "stage != S5")
            context: Context dictionary for evaluation
            
        Returns:
            True if condition is met, False otherwise
        """
        # Remove whitespace
        condition = condition.strip()
        
        # Split condition into parts
        if "!=" in condition:
            left, right = condition.split("!=")
            operator = "!="
        elif "==" in condition:
            left, right = condition.split("==")
            operator = "=="
        elif ">" in condition:
            left, right = condition.split(">")
            operator = ">"
        elif "<" in condition:
            left, right = condition.split("<")
            operator = "<"
        elif ">=" in condition:
            left, right = condition.split(">=")
            operator = ">="
        elif "<=" in condition:
            left, right = condition.split("<=")
            operator = "<="
        else:
            # Unknown condition format, return False to be safe
            return False
        
        # Trim whitespace
        left = left.strip()
        right = right.strip().strip("'\"").strip()  # Remove quotes
        
        # Get left value from context
        if left not in context:
            return False
        
        left_value = context[left]
        
        # Compare values
        if operator == "!=":
            return left_value != right
        elif operator == "==":
            return left_value == right
        elif operator == ">":
            try:
                return float(left_value) > float(right)
            except (ValueError, TypeError):
                return False
        elif operator == "<":
            try:
                return float(left_value) < float(right)
            except (ValueError, TypeError):
                return False
        elif operator == ">=":
            try:
                return float(left_value) >= float(right)
            except (ValueError, TypeError):
                return False
        elif operator == "<=":
            try:
                return float(left_value) <= float(right)
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _create_violation(self, trigger: GovernanceTrigger, event: GovernanceEvent) -> GovernanceViolation:
        """Create a violation object from a trigger and event"""
        return GovernanceViolation(
            level=trigger.violation,
            rule_id=trigger.id,
            event_id=event.id,
            actor_id=event.actor.id,
            message=trigger.message
        )
    
    def get_triggers(self) -> List[Dict[str, Any]]:
        """Get list of registered triggers"""
        return [trigger.model_dump() for trigger in self.triggers]
    
    def add_trigger(self, trigger: GovernanceTrigger):
        """Add a new trigger"""
        self.triggers.append(trigger)
    
    def remove_trigger(self, trigger_id: str):
        """Remove a trigger by ID"""
        self.triggers = [t for t in self.triggers if t.id != trigger_id]


__all__ = []