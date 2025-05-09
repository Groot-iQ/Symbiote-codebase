from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class DeviceAdapter(ABC):
    """
    Base class for device adapters.
    This abstract class defines the interface that all device adapters must implement.
    Device adapters are responsible for managing device-specific functionality and resources.
    """
    
    @abstractmethod
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the current device.
        This method should return a dictionary describing what the device can do,
        such as supported communication protocols, hardware features, etc.
        
        Returns:
            Dict: Dictionary containing device capabilities, for example:
            {
                'bluetooth': True,
                'wifi': True,
                'camera': False,
                'gps': True,
                'storage': '1TB'
            }
        """
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict:
        """
        Get information about the current device.
        This method should return basic information about the device,
        such as its name, type, operating system, etc.
        
        Returns:
            Dict: Dictionary containing device information, for example:
            {
                'name': 'Device Name',
                'type': 'desktop',
                'os': 'Windows 10',
                'version': '1.0.0'
            }
        """
        pass
    
    @abstractmethod
    def can_execute_task(self, task_requirements: Dict) -> bool:
        """
        Check if the device can execute a given task.
        This method should verify if the device has the necessary resources
        and capabilities to execute a specific task.
        
        Args:
            task_requirements: Dictionary containing task requirements, for example:
            {
                'memory': '1GB',
                'cpu': '2 cores',
                'storage': '100MB',
                'permissions': ['camera', 'location']
            }
            
        Returns:
            bool: True if the device can execute the task, False otherwise
        """
        pass
    
    @abstractmethod
    def get_available_resources(self) -> Dict:
        """
        Get the current available resources on the device.
        This method should return information about the device's current
        resource usage and availability.
        
        Returns:
            Dict: Dictionary containing available resources, for example:
            {
                'memory': '4GB free',
                'cpu': '50% available',
                'storage': '500GB free',
                'battery': '80%'
            }
        """
        pass
    
    @abstractmethod
    def execute_task(self, task: Dict) -> bool:
        """
        Execute a task on the device.
        This method should handle the actual execution of a task,
        including resource allocation and error handling.
        
        Args:
            task: Dictionary containing task information, for example:
            {
                'id': 'task_123',
                'type': 'data_processing',
                'parameters': {...},
                'priority': 1
            }
            
        Returns:
            bool: True if the task was executed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop_task(self, task_id: str) -> bool:
        """
        Stop a running task.
        This method should handle the graceful termination of a running task,
        including resource cleanup.
        
        Args:
            task_id: ID of the task to stop
            
        Returns:
            bool: True if the task was stopped successfully, False otherwise
        """
        pass 