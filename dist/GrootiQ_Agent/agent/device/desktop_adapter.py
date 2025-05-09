import platform
import psutil
from typing import Dict
from .device_adapter import DeviceAdapter

class DesktopAdapter(DeviceAdapter):
    """Adapter for desktop devices."""
    
    def __init__(self):
        """Initialize the desktop adapter."""
        self.system_info = platform.uname()
        self.capabilities = self._detect_capabilities()
    
    def _detect_capabilities(self) -> Dict:
        """
        Detect the capabilities of the desktop device.
        
        Returns:
            Dictionary of device capabilities
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
        """Check if the device has a GPU."""
        try:
            import GPUtil
            return len(GPUtil.getGPUs()) > 0
        except:
            return False
    
    def _check_internet(self) -> bool:
        """Check if the device has internet connectivity."""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    def _check_bluetooth(self) -> bool:
        """Check if the device has Bluetooth capability."""
        try:
            import bluetooth
            return True
        except:
            return False
    
    def _check_wifi(self) -> bool:
        """Check if the device has WiFi capability."""
        try:
            import netifaces
            return 'wlan0' in netifaces.interfaces()
        except:
            return False
    
    def _check_camera(self) -> bool:
        """Check if the device has a camera."""
        try:
            import cv2
            return len(cv2.VideoCapture.list_ports()) > 0
        except:
            return False
    
    def _check_microphone(self) -> bool:
        """Check if the device has a microphone."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            return p.get_device_count() > 0
        except:
            return False
    
    def get_capabilities(self) -> Dict:
        """Get the capabilities of the desktop device."""
        return self.capabilities
    
    def get_device_info(self) -> Dict:
        """Get information about the desktop device."""
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
        """Check if the desktop can execute a given task."""
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
        """Get the current available resources on the desktop."""
        return {
            'cpu_percent': 100 - psutil.cpu_percent(),
            'memory_percent': 100 - psutil.virtual_memory().percent,
            'disk_percent': 100 - psutil.disk_usage('/').percent
        }
    
    def execute_task(self, task: Dict) -> bool:
        """Execute a task on the desktop."""
        # Implementation would depend on the specific task type
        # This is a placeholder implementation
        return True
    
    def stop_task(self, task_id: str) -> bool:
        """Stop a running task on the desktop."""
        # Implementation would depend on how tasks are tracked
        # This is a placeholder implementation
        return True 