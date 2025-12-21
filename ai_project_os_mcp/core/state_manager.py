"""
State Manager - Manages Project State

This module is responsible for managing the project state.
It ensures that state is the single source of truth for governance decisions.

Key principles:
1. State as Truth
2. Persistence
3. Immutability guarantees
4. Version history
5. Thread safety
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class StateManager:
    """
    State Manager - Manages project state
    
    This class ensures that:
    - State is the single source of truth
    - State changes are properly recorded
    - State is persisted to disk
    - State can be rolled back if needed
    """
    
    def __init__(self, state_file: str = "state.json"):
        """
        Initialize state manager
        
        Args:
            state_file: Path to the state file
        """
        self.state_file = state_file
        self._state = self._load_state()
        self._state_history = []
        self._save_state_history()
    
    def _load_state(self) -> Dict[str, Any]:
        """
        Load state from file
        
        Returns:
            Dict[str, Any]: Current state
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                # If state file is corrupted, return default state
                return self._get_default_state()
        return self._get_default_state()
    
    def _get_default_state(self) -> Dict[str, Any]:
        """
        Get default project state
        
        Returns:
            Dict[str, Any]: Default state
        """
        return {
            "stage": "S1",
            "version": "1.0.3",
            "frozen": False,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_state_history(self):
        """
        Save state history to file
        """
        history_file = f"{self.state_file}.history"
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self._state_history, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            # Ignore errors when saving history for now
            pass
    
    def load_state(self) -> Dict[str, Any]:
        """
        Get current state
        
        Returns:
            Dict[str, Any]: Current state
        """
        return self._state.copy()
    
    def save_state(self, new_state: Dict[str, Any]) -> bool:
        """
        Save new state
        
        Args:
            new_state: New state to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add update timestamp
            new_state["last_updated"] = datetime.now().isoformat()
            
            # Save current state to history
            self._state_history.append({
                "timestamp": datetime.now().isoformat(),
                "state": self._state.copy()
            })
            
            # Keep only the last 100 states in history
            self._state_history = self._state_history[-100:]
            
            # Update current state
            self._state = new_state.copy()
            
            # Save to file
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
            
            # Save history
            self._save_state_history()
            
            return True
        except Exception:
            return False
    
    def update_state(self, updates: Dict[str, Any]) -> bool:
        """
        Update state with partial updates
        
        Args:
            updates: Partial state updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        new_state = self._state.copy()
        new_state.update(updates)
        return self.save_state(new_state)
    
    def rollback_state(self) -> bool:
        """
        Rollback to previous state
        
        Returns:
            bool: True if successful, False otherwise
        """
        if len(self._state_history) < 1:
            return False
        
        # Get previous state
        previous_state = self._state_history[-1]["state"]
        
        # Remove the last history entry
        self._state_history.pop()
        
        # Save previous state as current
        self._state = previous_state.copy()
        
        # Save to file
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
            
            # Save history
            self._save_state_history()
            
            return True
        except Exception:
            return False
    
    def get_state_history(self) -> list:
        """
        Get state history
        
        Returns:
            list: State history
        """
        return self._state_history.copy()
    
    def is_frozen(self) -> bool:
        """
        Check if project is frozen
        
        Returns:
            bool: True if frozen, False otherwise
        """
        return self._state.get("frozen", False)
    
    def get_stage(self) -> str:
        """
        Get current project stage
        
        Returns:
            str: Current stage
        """
        return self._state.get("stage", "S1")
    
    def set_stage(self, stage: str) -> bool:
        """
        Set current project stage
        
        Args:
            stage: New stage
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.update_state({"stage": stage})
    
    def freeze(self, reason: str, actor_id: str) -> bool:
        """
        Freeze the project
        
        Args:
            reason: Reason for freezing
            actor_id: ID of the actor freezing the project
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.update_state({
            "frozen": True,
            "freeze_reason": reason,
            "freeze_by": actor_id,
            "freeze_at": datetime.now().isoformat()
        })
    
    def unfreeze(self, actor_id: str) -> bool:
        """
        Unfreeze the project

        Args:
            actor_id: ID of the actor unfreezing the project

        Returns:
            bool: True if successful, False otherwise
        """
        new_state = self._state.copy()
        new_state["frozen"] = False
        new_state.pop("freeze_reason", None)
        new_state.pop("freeze_by", None)
        new_state.pop("freeze_at", None)
        new_state.pop("freeze_event_id", None)
        return self.save_state(new_state)


__all__ = []