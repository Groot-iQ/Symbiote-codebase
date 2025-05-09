import json
import time
from typing import Dict, List, Optional
from config.settings import settings

class MemorySystem:
    """
    Manages the agent's memory system.
    This class implements a two-tier memory system:
    1. Short-term memory: Recent memories stored in a list
    2. Long-term memory: Older memories stored in a dictionary
    
    The system automatically manages memory capacity by:
    1. Storing new memories in short-term memory
    2. Moving older memories to long-term storage when capacity is reached
    3. Maintaining importance levels for long-term memories
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the memory system.
        
        Args:
            config: Memory configuration containing:
                   - short_term_capacity: Maximum number of short-term memories
        """
        self.config = config or {}
        self.short_term_capacity = self.config.get(
            'short_term_capacity',
            settings.SHORT_TERM_CAPACITY
        )
        
        # Initialize memory stores
        self.short_term = []  # List of recent memories
        self.long_term = {}   # Dictionary of older memories
    
    def store_memory(self, memory: Dict, importance: int = 1) -> bool:
        """
        Store a memory in the system.
        This method:
        1. Adds the memory to short-term storage
        2. If short-term capacity is exceeded, moves oldest memory to long-term storage
        
        Args:
            memory: Memory data to store, containing:
                   - type: Type of memory (e.g., 'received_data', 'task_result')
                   - data: The actual memory data
                   - timestamp: When the memory was created
            importance: Importance level of the memory (higher = more important)
            
        Returns:
            bool: True if memory was stored successfully, False otherwise
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
        """
        Store a memory in long-term storage.
        This method:
        1. Generates a unique ID for the memory
        2. Stores the memory with metadata (timestamp and importance)
        
        Args:
            memory: Memory data to store
            importance: Importance level of the memory
            
        Returns:
            bool: True if memory was stored successfully, False otherwise
        """
        try:
            # Generate unique ID based on memory content
            memory_id = str(hash(str(memory)))
            
            # Store memory with metadata
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
        This method:
        1. First checks short-term memory (most recent)
        2. Then checks long-term memory if not found
        
        Args:
            query: Query parameters to match against memories, containing:
                  - type: Type of memory to find
                  - key: Value pairs to match in memory data
                  
        Returns:
            Optional[Dict]: Retrieved memory if found, None otherwise
        """
        # First check short-term memory (most recent)
        for memory in self.short_term:
            if self._matches_query(memory, query):
                return memory
        
        # Then check long-term storage
        for memory_data in self.long_term.values():
            if self._matches_query(memory_data['data'], query):
                return memory_data['data']
        
        return None
    
    def _matches_query(self, memory: Dict, query: Dict) -> bool:
        """
        Check if a memory matches a query.
        This method verifies that all key-value pairs in the query
        exist and match in the memory.
        
        Args:
            memory: Memory to check
            query: Query parameters to match
            
        Returns:
            bool: True if memory matches query, False otherwise
        """
        for key, value in query.items():
            if key not in memory or memory[key] != value:
                return False
        return True 