"""
Violation Model and Management

This module defines the Violation model and related management classes.
Violations are auditable objects that represent governance rule breaches.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ViolationLevel(str, Enum):
    """
    Violation severity levels
    """
    CRITICAL = "CRITICAL"  # System freeze, requires immediate action
    MAJOR = "MAJOR"        # Requires human approval
    MINOR = "MINOR"        # Warning, affects governance score
    INFO = "INFO"          # Informational, no score impact


class ViolationStatus(str, Enum):
    """
    Violation status
    """
    OPEN = "OPEN"          # Violation is active
    RESOLVED = "RESOLVED"  # Violation has been resolved


class GovernanceViolation(BaseModel):
    """
    Represents a governance violation that occurred
    
    Violations are immutable once created, and can be resolved but not deleted
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique violation identifier"
    )
    
    level: ViolationLevel = Field(
        ...,
        description="Severity level of the violation"
    )
    
    rule_id: str = Field(
        ...,
        description="ID of the rule that was violated"
    )
    
    event_id: str = Field(
        ...,
        description="ID of the event that triggered this violation"
    )
    
    actor_id: str = Field(
        ...,
        description="ID of the actor who caused the violation"
    )
    
    message: str = Field(
        ...,
        description="Human-readable violation message"
    )
    
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional violation details"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the violation occurred"
    )
    
    status: ViolationStatus = Field(
        default=ViolationStatus.OPEN,
        description="Current status of the violation"
    )
    
    resolved_by: Optional[str] = Field(
        None,
        description="ID of the actor who resolved the violation"
    )
    
    resolved_at: Optional[datetime] = Field(
        None,
        description="When the violation was resolved"
    )
    
    class Config:
        """Model configuration"""
        extra = "forbid"  # Strict validation
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
