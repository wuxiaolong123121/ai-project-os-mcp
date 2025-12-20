"""
Governance Events - Enhanced Event Model with Agent Identity
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, Optional
from typing import Dict
import uuid


class EventType(str, Enum):
    """Types of governance events"""
    STAGE_CHANGE = "STAGE_CHANGE"
    CODE_GENERATION = "CODE_GENERATION"
    ARCH_VIOLATION = "ARCH_VIOLATION"
    AUDIT_MISSING = "AUDIT_MISSING"
    TOOL_CALL = "TOOL_CALL"
    FREEZE_REQUEST = "FREEZE_REQUEST"
    POLICY_CHANGE = "POLICY_CHANGE"
    VIOLATION = "VIOLATION"
    SCORE_UPDATE = "SCORE_UPDATE"


class Actor(BaseModel):
    """
    Accountable entity for governance events
    
    Actor represents the accountable entity, not necessarily a human.
    """
    id: str = Field(..., description="Unique identifier for the actor")
    role: str = Field(..., description="Role of the actor (planner/coder/reviewer/system)")
    source: str = Field(..., description="Source of the actor (claude/cursor/trae/api)")
    name: Optional[str] = Field(None, description="Human-readable name of the actor")
    metadata: Dict[str, any] = Field(default_factory=dict, description="Additional metadata")


class GovernanceEvent(BaseModel):
    """Enhanced governance event with agent identity"""
    event_type: EventType = Field(..., description="Type of governance event")
    actor: Actor = Field(..., description="Actor who triggered the event")
    payload: Dict[str, any] = Field(default_factory=dict, description="Event-specific payload")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    
    class Config:
        extra = "forbid"  # Strict validation, no extra fields allowed
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventStore:
    """
    Event Store Interface - For event persistence and querying
    """
    
    def save_event(self, event: GovernanceEvent) -> bool:
        """Save a governance event to storage"""
        raise NotImplementedError
    
    def get_event(self, event_id: str) -> Optional[GovernanceEvent]:
        """Get a governance event by ID"""
        raise NotImplementedError
    
    def list_events(self, **filters) -> List[GovernanceEvent]:
        """List governance events with optional filters"""
        raise NotImplementedError


class InMemoryEventStore(EventStore):
    """
    In-memory implementation of EventStore for testing and development
    """
    
    def __init__(self):
        self.events = {}
    
    def save_event(self, event: GovernanceEvent) -> bool:
        """Save a governance event to in-memory storage"""
        self.events[event.event_id] = event
        return True
    
    def get_event(self, event_id: str) -> Optional[GovernanceEvent]:
        """Get a governance event by ID from in-memory storage"""
        return self.events.get(event_id)
    
    def list_events(self, **filters) -> List[GovernanceEvent]:
        """List governance events with optional filters"""
        results = list(self.events.values())
        
        # Apply filters
        if "event_type" in filters:
            results = [e for e in results if e.event_type == filters["event_type"]]
        
        if "actor_id" in filters:
            results = [e for e in results if e.actor.id == filters["actor_id"]]
        
        if "start_time" in filters:
            start_time = filters["start_time"]
            results = [e for e in results if e.timestamp >= start_time]
        
        if "end_time" in filters:
            end_time = filters["end_time"]
            results = [e for e in results if e.timestamp <= end_time]
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)