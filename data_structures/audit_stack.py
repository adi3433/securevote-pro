from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class AuditStack:
    """
    Stack-based audit system for tracking voting operations.
    Enables LIFO undo operations in demo mode.
    """
    
    def __init__(self):
        """Initialize empty audit stack."""
        self.stack: List[Dict[str, Any]] = []
        self.max_size = 10000  # Prevent memory overflow
    
    def push(self, event: Dict[str, Any]) -> None:
        """
        Push audit event onto stack.
        
        Args:
            event: Dictionary containing event details
        """
        if len(self.stack) >= self.max_size:
            # Remove oldest event to prevent overflow
            self.stack.pop(0)
        
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.utcnow().isoformat()
        
        self.stack.append(event)
    
    def pop(self) -> Optional[Dict[str, Any]]:
        """
        Pop most recent event from stack.
        
        Returns:
            Most recent event or None if stack is empty
        """
        if self.is_empty():
            return None
        return self.stack.pop()
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """
        View most recent event without removing it.
        
        Returns:
            Most recent event or None if stack is empty
        """
        if self.is_empty():
            return None
        return self.stack[-1]
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self.stack) == 0
    
    def size(self) -> int:
        """Get current stack size."""
        return len(self.stack)
    
    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent events from stack.
        
        Args:
            count: Number of recent events to return
        
        Returns:
            List of recent events (most recent first)
        """
        if count <= 0:
            return []
        
        return self.stack[-count:] if len(self.stack) >= count else self.stack[:]
    
    def clear(self) -> None:
        """Clear all events from stack."""
        self.stack.clear()
    
    def to_json(self) -> str:
        """Convert stack to JSON string."""
        return json.dumps(self.stack, indent=2)
    
    def from_json(self, json_str: str) -> None:
        """Load stack from JSON string."""
        try:
            self.stack = json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
    
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get all events of specific type.
        
        Args:
            event_type: Type of events to filter
        
        Returns:
            List of events matching the type
        """
        return [event for event in self.stack if event.get('type') == event_type]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get stack statistics."""
        event_types = {}
        for event in self.stack:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'total_events': len(self.stack),
            'event_types': event_types,
            'max_size': self.max_size,
            'is_empty': self.is_empty(),
            'oldest_event': self.stack[0]['timestamp'] if self.stack else None,
            'newest_event': self.stack[-1]['timestamp'] if self.stack else None
        }
