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
    
    resolved: bool = Field(
        default=False,
        description="Whether the violation has been resolved"
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


class ViolationStore:
    """
    Interface for storing and retrieving violations
    """
    
    def save_violation(self, violation: GovernanceViolation) -> bool:
        """
        Save a violation to storage
        
        Args:
            violation: The violation to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError
    
    def get_violation(self, violation_id: str) -> Optional[GovernanceViolation]:
        """
        Get a violation by ID
        
        Args:
            violation_id: The ID of the violation to retrieve
            
        Returns:
            Optional[GovernanceViolation]: The violation if found, None otherwise
        """
        raise NotImplementedError
    
    def list_violations(self, **filters) -> List[GovernanceViolation]:
        """
        List violations with optional filters
        
        Args:
            **filters: Filter criteria
                - level: ViolationLevel
                - resolved: bool
                - actor_id: str
                - start_time: datetime
                - end_time: datetime
                - event_id: str
                
        Returns:
            List[GovernanceViolation]: List of matching violations
        """
        raise NotImplementedError
    
    def resolve_violation(self, violation_id: str, resolved_by: str) -> bool:
        """
        Mark a violation as resolved
        
        Args:
            violation_id: The ID of the violation to resolve
            resolved_by: The ID of the actor resolving the violation
            
        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError


class InMemoryViolationStore(ViolationStore):
    """
    In-memory implementation of ViolationStore for testing and development
    """
    
    def __init__(self):
        """
        Initialize the in-memory violation store
        """
        self.violations: Dict[str, GovernanceViolation] = {}
    
    def save_violation(self, violation: GovernanceViolation) -> bool:
        """
        Save a violation to in-memory storage
        
        Args:
            violation: The violation to save
            
        Returns:
            bool: Always True for in-memory storage
        """
        self.violations[violation.id] = violation
        return True
    
    def get_violation(self, violation_id: str) -> Optional[GovernanceViolation]:
        """
        Get a violation by ID
        
        Args:
            violation_id: The ID of the violation to retrieve
            
        Returns:
            Optional[GovernanceViolation]: The violation if found, None otherwise
        """
        return self.violations.get(violation_id)
    
    def list_violations(self, **filters) -> List[GovernanceViolation]:
        """
        List violations with optional filters
        
        Args:
            **filters: Filter criteria
                - level: ViolationLevel
                - resolved: bool
                - actor_id: str
                - start_time: datetime
                - end_time: datetime
                - event_id: str
                
        Returns:
            List[GovernanceViolation]: List of matching violations
        """
        results = list(self.violations.values())
        
        # Apply filters
        if "level" in filters:
            level = filters["level"]
            results = [v for v in results if v.level == level]
        
        if "resolved" in filters:
            resolved = filters["resolved"]
            results = [v for v in results if v.resolved == resolved]
        
        if "actor_id" in filters:
            actor_id = filters["actor_id"]
            results = [v for v in results if v.actor_id == actor_id]
        
        if "start_time" in filters:
            start_time = filters["start_time"]
            results = [v for v in results if v.timestamp >= start_time]
        
        if "end_time" in filters:
            end_time = filters["end_time"]
            results = [v for v in results if v.timestamp <= end_time]
        
        if "event_id" in filters:
            event_id = filters["event_id"]
            results = [v for v in results if v.event_id == event_id]
        
        # Sort by severity and then by timestamp (newest first)
        severity_order = {ViolationLevel.CRITICAL: 0, ViolationLevel.MAJOR: 1, ViolationLevel.MINOR: 2, ViolationLevel.INFO: 3}
        return sorted(
            results, 
            key=lambda x: (severity_order[x.level], x.timestamp), 
            reverse=True
        )
    
    def resolve_violation(self, violation_id: str, resolved_by: str) -> bool:
        """
        Mark a violation as resolved
        
        Args:
            violation_id: The ID of the violation to resolve
            resolved_by: The ID of the actor resolving the violation
            
        Returns:
            bool: True if successful, False otherwise
        """
        if violation_id not in self.violations:
            return False
        
        violation = self.violations[violation_id].copy()
        violation.resolved = True
        violation.resolved_by = resolved_by
        violation.resolved_at = datetime.now()
        
        # Create a new violation instance with resolved state
        resolved_violation = GovernanceViolation(
            **violation.dict(),
            id=violation_id  # Keep the same ID
        )
        
        self.violations[violation_id] = resolved_violation
        return True


# Global in-memory stores for development
violation_store = InMemoryViolationStore()
