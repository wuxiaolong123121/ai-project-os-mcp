"""
Event Store - The source of truth for governance events

This module defines the EventStore interface and implementations.
EventStore is the single source of truth for all governance events.
Events are append-only and cannot be modified or deleted.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import uuid
from abc import ABC, abstractmethod

from .events import GovernanceEvent


class EventStore(ABC):
    """
    Event Store interface - The source of truth for governance events
    
    Events are append-only and cannot be modified or deleted.
    Any state, audit, or violation must reference an event_id.
    """
    
    @abstractmethod
    def append(self, event: GovernanceEvent) -> bool:
        """
        Append a governance event to the store
        
        Args:
            event: Governance event to append
            
        Returns:
            bool: True if successful, False otherwise
        
        🔒 铁律：事件一旦写入，不可修改、不可删除
        """
        pass
    
    @abstractmethod
    def get(self, event_id: str) -> Optional[GovernanceEvent]:
        """
        Get a governance event by ID
        
        Args:
            event_id: Event ID to retrieve
            
        Returns:
            Optional[GovernanceEvent]: The event if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list(self, **filters) -> List[GovernanceEvent]:
        """
        List governance events with optional filters
        
        Args:
            **filters: Filter criteria
                - event_type: Event type to filter by
                - actor_id: Actor ID to filter by
                - start_time: Start time to filter by
                - end_time: End time to filter by
            
        Returns:
            List[GovernanceEvent]: List of matching events, sorted by timestamp descending
        """
        pass
    
    @abstractmethod
    def count(self, **filters) -> int:
        """
        Count governance events with optional filters
        
        Args:
            **filters: Filter criteria (same as list method)
            
        Returns:
            int: Number of matching events
        """
        pass


class InMemoryEventStore(EventStore):
    """
    In-memory implementation of EventStore for testing and development
    
    This implementation is not persistent and should only be used for testing.
    """
    
    def __init__(self):
        """
        Initialize the in-memory event store
        """
        self.events: Dict[str, GovernanceEvent] = {}
    
    def append(self, event: GovernanceEvent) -> bool:
        """
        Append a governance event to the store
        
        Args:
            event: Governance event to append
            
        Returns:
            bool: Always True for in-memory storage
        
        🔒 铁律：事件一旦写入，不可修改、不可删除
        """
        # 确保事件ID唯一性
        if event.id in self.events:
            return False
        
        # 写入事件（append-only）
        self.events[event.id] = event
        return True
    
    def get(self, event_id: str) -> Optional[GovernanceEvent]:
        """
        Get a governance event by ID
        
        Args:
            event_id: Event ID to retrieve
            
        Returns:
            Optional[GovernanceEvent]: The event if found, None otherwise
        """
        return self.events.get(event_id)
    
    def list(self, **filters) -> List[GovernanceEvent]:
        """
        List governance events with optional filters
        
        Args:
            **filters: Filter criteria
                - event_type: Event type to filter by
                - actor_id: Actor ID to filter by
                - start_time: Start time to filter by
                - end_time: End time to filter by
            
        Returns:
            List[GovernanceEvent]: List of matching events, sorted by timestamp descending
        """
        results = list(self.events.values())
        
        # Apply filters
        if "event_type" in filters:
            event_type = filters["event_type"]
            results = [e for e in results if e.event_type == event_type]
        
        if "actor_id" in filters:
            actor_id = filters["actor_id"]
            results = [e for e in results if e.actor.id == actor_id]
        
        if "start_time" in filters:
            start_time = filters["start_time"]
            results = [e for e in results if e.timestamp >= start_time]
        
        if "end_time" in filters:
            end_time = filters["end_time"]
            results = [e for e in results if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def count(self, **filters) -> int:
        """
        Count governance events with optional filters
        
        Args:
            **filters: Filter criteria (same as list method)
            
        Returns:
            int: Number of matching events
        """
        return len(self.list(**filters))


# Global in-memory event store for development
_event_store = None

def get_event_store() -> EventStore:
    """
    Get the global event store instance
    
    Returns:
        EventStore: Global event store instance
    """
    global _event_store
    if _event_store is None:
        _event_store = InMemoryEventStore()
    return _event_store
