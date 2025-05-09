from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class DeviceAdapter(ABC):
    """Base class for device adapters."""
    
    @abstractmethod
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the current device.
        
        Returns:
            Dictionary of device capabilities
        """
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict:
        """
        Get information about the current device.
        
        Returns:
            Dictionary of device information
        """
        pass
    
    @abstractmethod
    def can_execute_task(self, task_requirements: Dict) -> bool:
        """
        Check if the device can execute a given task.
        
        Args:
            task_requirements: Dictionary of task requirements
            
        Returns:
            Whether the device can execute the task
        """
        pass
    
    @abstractmethod
    def get_available_resources(self) -> Dict:
        """
        Get the current available resources on the device.
        
        Returns:
            Dictionary of available resources
        """
        pass
    
    @abstractmethod
    def execute_task(self, task: Dict) -> bool:
        """
        Execute a task on the device.
        
        Args:
            task: Task to execute
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def stop_task(self, task_id: str) -> bool:
        """
        Stop a running task.
        
        Args:
            task_id: ID of the task to stop
            
        Returns:
            Success status
        """
        pass 