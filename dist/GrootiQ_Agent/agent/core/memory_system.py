import json
import time
from typing import Dict, List, Optional
from config.settings import settings

class MemorySystem:
    """Manages the agent's memory system."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the memory system.
        
        Args:
            config: Memory configuration
        """
        self.config = config or {}
        self.short_term_capacity = self.config.get(
            'short_term_capacity',
            settings.SHORT_TERM_CAPACITY
        )
        
        # Initialize memory stores
        self.short_term = []
        self.long_term = {}
    
    def store_memory(self, memory: Dict, importance: int = 1) -> bool:
        """
        Store a memory.
        
        Args:
            memory: Memory data to store
            importance: Importance level of the memory
            
        Returns:
            Success status
        """
        try:
            # Add to short-term memory
            self.short_term.append(memory)
            
            # Trim short-term memory if needed
            while len(self.short_term) > self.short_term_capacity:
                # Move oldest memory to long-term storage
                oldest = self.short_term.pop(0)
                self._store_long_term(oldest, importance)
            
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def _store_long_term(self, memory: Dict, importance: int) -> bool:
        """Store a memory in long-term storage."""
        try:
            memory_id = str(hash(str(memory)))
            self.long_term[memory_id] = {
                'data': memory,
                'timestamp': time.time(),
                'importance': importance
            }
            return True
        except Exception as e:
            print(f"Error storing long-term memory: {e}")
            return False
    
    def retrieve_memory(self, query: Dict) -> Optional[Dict]:
        """
        Retrieve a memory matching the query.
        
        Args:
            query: Query parameters
            
        Returns:
            Retrieved memory or None if not found
        """
        # First check short-term memory
        for memory in self.short_term:
            if self._matches_query(memory, query):
                return memory
        
        # Then check long-term storage
        for memory_data in self.long_term.values():
            if self._matches_query(memory_data['data'], query):
                return memory_data['data']
        
        return None
    
    def _matches_query(self, memory: Dict, query: Dict) -> bool:
        """Check if a memory matches a query."""
        for key, value in query.items():
            if key not in memory or memory[key] != value:
                return False
        return True 