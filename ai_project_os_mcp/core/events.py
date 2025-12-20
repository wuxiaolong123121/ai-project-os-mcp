"""
Governance Events - Enhanced Event Model with Agent Identity
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List, Literal
import uuid


class EventType(str, Enum):
    """Types of governance events"""
    STAGE_CHANGE = "STAGE_CHANGE"
    CODE_GENERATION = "CODE_GENERATION"
    ARCH_VIOLATION = "ARCH_VIOLATION"
    AUDIT_MISSING = "AUDIT_MISSING"
    TOOL_CALL = "TOOL_CALL"
    FREEZE_REQUEST = "FREEZE_REQUEST"
    UNFREEZE = "UNFREEZE"
    STATUS = "STATUS"
    POLICY_CHANGE = "POLICY_CHANGE"
    VIOLATION = "VIOLATION"
    SCORE_UPDATE = "SCORE_UPDATE"


class Actor(BaseModel):
    """
    Accountable entity for governance events
    
    Actor represents the accountable entity, not necessarily a human.
    """
    id: str = Field(..., description="Unique identifier for the actor")
    role: Literal["planner", "coder", "reviewer", "system"] = Field(..., description="Role of the actor")
    role_type: Literal["AI", "HUMAN", "SYSTEM"] = Field(..., description="Type of actor")
    source: Literal["claude", "cursor", "trae", "api"] = Field(..., description="Source of the actor")
    name: Optional[str] = Field(None, description="Human-readable name of the actor")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GovernanceEvent(BaseModel):
    """Enhanced governance event with agent identity"""
    event_type: EventType = Field(..., description="Type of governance event")
    actor: Actor = Field(..., description="Actor who triggered the event")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific payload")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    
    class Config:
        extra = "forbid"  # Strict validation, no extra fields allowed
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }