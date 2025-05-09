import threading
import time
import logging
from typing import Dict, Optional
from config.settings import settings
from agent.device.desktop_adapter import DesktopAdapter
from agent.device.mobile_adapter import MobileAdapter
from agent.device.iot_adapter import IoTAdapter
from agent.communication.communication_layer import CommunicationLayer
from agent.core.memory_system import MemorySystem
from agent.core.task_manager import TaskManager
from agent.core.llm_integration import LLMIntegration

# Configure logging
logger = logging.getLogger(__name__)

class AgentCore:
    """Core class for the Mobile AI Agent System."""
    
    def __init__(self, agent_id: str, config: Dict = None):
        """
        Initialize the agent core.
        
        Args:
            agent_id: Unique identifier for this agent
            config: Configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}
        
        logger.debug(f"Initializing agent {agent_id} with config: {config}")
        
        # Initialize device adapter based on device type
        device_type = self.config.get('device_type', settings.DEVICE_TYPE)
        logger.debug(f"Creating device adapter for type: {device_type}")
        self.device_adapter = self._create_device_adapter(device_type)
        
        # Initialize memory system
        logger.debug("Initializing memory system")
        self.memory = MemorySystem(self.config.get('memory', {}))
        
        # Initialize task manager
        logger.debug("Initializing task manager")
        self.task_manager = TaskManager(self, self.config.get('tasks', {}))
        
        # Initialize communication layer
        logger.debug("Initializing communication layer")
        self.communication = CommunicationLayer(
            self,
            self.config.get('communication', {})
        )
        
        # Initialize LLM integration
        logger.debug("Initializing LLM integration")
        self.llm = LLMIntegration(self.config.get('llm', {}))
        
        self.running = False
        logger.info(f"Agent {agent_id} initialized successfully")
    
    def _create_device_adapter(self, device_type: str):
        """Create appropriate device adapter based on device type."""
        logger.debug(f"Creating device adapter for type: {device_type}")
        try:
            if device_type == 'desktop':
                return DesktopAdapter()
            elif device_type == 'mobile':
                return MobileAdapter()
            elif device_type == 'iot':
                return IoTAdapter()
            else:
                raise ValueError(f"Unsupported device type: {device_type}")
        except Exception as e:
            logger.error(f"Error creating device adapter: {e}", exc_info=True)
            raise
    
    def start(self) -> bool:
        """Start the agent's operation."""
        try:
            logger.info(f"Starting agent {self.agent_id}")
            self.running = True
            
            # Start task manager
            logger.debug("Starting task manager")
            if not self.task_manager.start():
                logger.error("Failed to start task manager")
                return False
            
            # Start communication layer
            logger.debug("Starting communication layer")
            if not self.communication.start():
                logger.error("Failed to start communication layer")
                self.task_manager.stop()
                return False
            
            # Announce presence
            logger.debug("Announcing presence")
            self.communication.announce_presence()
            
            logger.info(f"Agent {self.agent_id} started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting agent: {e}", exc_info=True)
            return False
    
    def stop(self) -> bool:
        """Stop the agent's operation."""
        try:
            logger.info(f"Stopping agent {self.agent_id}")
            self.running = False
            
            # Stop task manager
            logger.debug("Stopping task manager")
            if not self.task_manager.stop():
                logger.error("Failed to stop task manager")
                return False
            
            # Stop communication layer
            logger.debug("Stopping communication layer")
            if not self.communication.stop():
                logger.error("Failed to stop communication layer")
                return False
            
            logger.info(f"Agent {self.agent_id} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Error stopping agent: {e}", exc_info=True)
            return False
    
    def handle_received_data(self, sender_id: str, data: Dict) -> bool:
        """
        Handle data received from another device.
        
        Args:
            sender_id: ID of the sending device
            data: Received data
            
        Returns:
            Success status
        """
        try:
            logger.debug(f"Handling received data from {sender_id}")
            
            # Store the received data in memory
            memory_data = {
                'type': 'received_data',
                'sender_id': sender_id,
                'data': data,
                'timestamp': time.time()
            }
            logger.debug(f"Storing memory: {memory_data}")
            self.memory.store_memory(memory_data)
            
            # Handle different types of data
            if data.get('type') == 'task':
                logger.debug(f"Received task from {sender_id}: {data['task']}")
                
                # Analyze task using LLM
                task_analysis = self.llm.analyze_task(data['task'].get('description', ''))
                if task_analysis:
                    data['task'].update(task_analysis)
                
                # Add received task to task manager
                return self.task_manager.add_task(
                    data['task'],
                    data.get('priority', 0)
                )
            
            return True
        except Exception as e:
            logger.error(f"Error handling received data: {e}", exc_info=True)
            return False 