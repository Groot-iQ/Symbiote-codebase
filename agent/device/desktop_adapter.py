import platform
import psutil
from typing import Dict
from .device_adapter import DeviceAdapter

class DesktopAdapter(DeviceAdapter):
    """
    Adapter for desktop devices.
    This class implements the DeviceAdapter interface for desktop computers,
    providing device-specific functionality and resource management.
    """
    
    def __init__(self):
        """
        Initialize the desktop adapter.
        This sets up the basic system information and detects device capabilities.
        """
        self.system_info = platform.uname()  # Get basic system information
        self.capabilities = self._detect_capabilities()  # Detect device capabilities
    
    def _detect_capabilities(self) -> Dict:
        """
        Detect the capabilities of the desktop device.
        This method checks for various hardware and software capabilities
        that the desktop device might have.
        
        Returns:
            Dict: Dictionary containing detected capabilities, for example:
            {
                'type': 'desktop',
                'os': 'Windows',
                'has_bluetooth': True,
                'has_wifi': True,
                ...
            }
        """
        return {
            'type': 'desktop',
            'os': self.system_info.system,
            'os_version': self.system_info.version,
            'architecture': self.system_info.machine,
            'processor': self.system_info.processor,
            'has_gpu': self._check_gpu(),
            'has_internet': self._check_internet(),
            'has_bluetooth': self._check_bluetooth(),
            'has_wifi': self._check_wifi(),
            'has_camera': self._check_camera(),
            'has_microphone': self._check_microphone(),
            'has_speakers': True,  # Most desktops have speakers
            'has_display': True,   # Most desktops have a display
            'has_keyboard': True,  # Most desktops have a keyboard
            'has_mouse': True      # Most desktops have a mouse
        }
    
    def _check_gpu(self) -> bool:
        """
        Check if the device has a GPU.
        Uses GPUtil to detect NVIDIA GPUs.
        
        Returns:
            bool: True if a GPU is detected, False otherwise
        """
        try:
            import GPUtil
            return len(GPUtil.getGPUs()) > 0
        except:
            return False
    
    def _check_internet(self) -> bool:
        """
        Check if the device has internet connectivity.
        Attempts to connect to Google's DNS server.
        
        Returns:
            bool: True if internet connection is available, False otherwise
        """
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    def _check_bluetooth(self) -> bool:
        """
        Check if the device has Bluetooth capability.
        Attempts to import the bluetooth module.
        
        Returns:
            bool: True if Bluetooth is available, False otherwise
        """
        try:
            import bluetooth
            return True
        except:
            return False
    
    def _check_wifi(self) -> bool:
        """
        Check if the device has WiFi capability.
        Checks for wireless network interfaces.
        
        Returns:
            bool: True if WiFi is available, False otherwise
        """
        try:
            import netifaces
            return 'wlan0' in netifaces.interfaces()
        except:
            return False
    
    def _check_camera(self) -> bool:
        """
        Check if the device has a camera.
        Uses OpenCV to detect video capture devices.
        
        Returns:
            bool: True if a camera is detected, False otherwise
        """
        try:
            import cv2
            return len(cv2.VideoCapture.list_ports()) > 0
        except:
            return False
    
    def _check_microphone(self) -> bool:
        """
        Check if the device has a microphone.
        Uses PyAudio to detect audio input devices.
        
        Returns:
            bool: True if a microphone is detected, False otherwise
        """
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            return p.get_device_count() > 0
        except:
            return False
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of the desktop device.
        Returns the previously detected capabilities.
        
        Returns:
            Dict: Dictionary of device capabilities
        """
        return self.capabilities
    
    def get_device_info(self) -> Dict:
        """
        Get detailed information about the desktop device.
        This includes system information, hardware resources, and current usage.
        
        Returns:
            Dict: Dictionary containing device information, for example:
            {
                'type': 'desktop',
                'hostname': 'DESKTOP-ABC123',
                'os': 'Windows',
                'memory': {'total': 8589934592, 'available': 4294967296},
                'cpu': {'cores': 8, 'usage': 25.5},
                ...
            }
        """
        return {
            'type': 'desktop',
            'hostname': self.system_info.node,
            'os': self.system_info.system,
            'os_version': self.system_info.version,
            'architecture': self.system_info.machine,
            'processor': self.system_info.processor,
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free
            },
            'cpu': {
                'cores': psutil.cpu_count(),
                'usage': psutil.cpu_percent()
            }
        }
    
    def can_execute_task(self, task_requirements: Dict) -> bool:
        """
        Check if the desktop can execute a given task.
        Verifies both required capabilities and resource availability.
        
        Args:
            task_requirements: Dictionary containing task requirements, for example:
            {
                'required_capabilities': ['bluetooth', 'wifi'],
                'required_resources': {
                    'cpu_percent': 50,
                    'memory_percent': 30
                }
            }
            
        Returns:
            bool: True if the task can be executed, False otherwise
        """
        # Check if all required capabilities are available
        for capability in task_requirements.get('required_capabilities', []):
            if not self.capabilities.get(capability, False):
                return False
        
        # Check resource requirements
        resources = task_requirements.get('required_resources', {})
        available = self.get_available_resources()
        
        for resource, amount in resources.items():
            if available.get(resource, 0) < amount:
                return False
        
        return True
    
    def get_available_resources(self) -> Dict:
        """
        Get the current available resources on the desktop.
        Returns the percentage of available CPU, memory, and disk space.
        
        Returns:
            Dict: Dictionary containing available resources, for example:
            {
                'cpu_percent': 75.5,
                'memory_percent': 60.0,
                'disk_percent': 80.0
            }
        """
        return {
            'cpu_percent': 100 - psutil.cpu_percent(),
            'memory_percent': 100 - psutil.virtual_memory().percent,
            'disk_percent': 100 - psutil.disk_usage('/').percent
        }
    
    def execute_task(self, task: Dict) -> bool:
        """
        Execute a task on the desktop.
        This is a placeholder implementation that should be customized
        based on the specific task types your system supports.
        
        Args:
            task: Dictionary containing task information
            
        Returns:
            bool: True if the task was executed successfully, False otherwise
        """
        # Implementation would depend on the specific task type
        # This is a placeholder implementation
        return True
    
    def stop_task(self, task_id: str) -> bool:
        """
        Stop a running task on the desktop.
        This is a placeholder implementation that should be customized
        based on how tasks are tracked and managed in your system.
        
        Args:
            task_id: ID of the task to stop
            
        Returns:
            bool: True if the task was stopped successfully, False otherwise
        """
        # Implementation would depend on how tasks are tracked
        # This is a placeholder implementation
        return True 