import platform
import psutil
from typing import Dict
from .device_adapter import DeviceAdapter

class MobileAdapter(DeviceAdapter):
    """Adapter for mobile devices."""
    
    def __init__(self):
        """Initialize the mobile adapter."""
        self.system_info = platform.uname()
        self.capabilities = self._detect_capabilities()
    
    def _detect_capabilities(self) -> Dict:
        """
        Detect the capabilities of the mobile device.
        
        Returns:
            Dictionary of device capabilities
        """
        return {
            'type': 'mobile',
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
            'has_speakers': True,  # Most mobile devices have speakers
            'has_display': True,   # All mobile devices have a display
            'has_touchscreen': True,  # All mobile devices have touchscreen
            'has_gps': self._check_gps(),
            'has_accelerometer': self._check_accelerometer(),
            'has_gyroscope': self._check_gyroscope(),
            'has_battery': True,  # All mobile devices have a battery
            'is_charging': self._check_charging()
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
    
    def _check_gps(self) -> bool:
        """Check if the device has GPS capability."""
        # This would typically use platform-specific APIs
        # For now, we'll assume it's available
        return True
    
    def _check_accelerometer(self) -> bool:
        """Check if the device has an accelerometer."""
        # This would typically use platform-specific APIs
        # For now, we'll assume it's available
        return True
    
    def _check_gyroscope(self) -> bool:
        """Check if the device has a gyroscope."""
        # This would typically use platform-specific APIs
        # For now, we'll assume it's available
        return True
    
    def _check_charging(self) -> bool:
        """Check if the device is currently charging."""
        # This would typically use platform-specific APIs
        # For now, we'll return False
        return False
    
    def get_capabilities(self) -> Dict:
        """Get the capabilities of the mobile device."""
        return self.capabilities
    
    def get_device_info(self) -> Dict:
        """Get information about the mobile device."""
        return {
            'type': 'mobile',
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
            },
            'battery': {
                'percent': self._get_battery_percent(),
                'is_charging': self._check_charging()
            }
        }
    
    def _get_battery_percent(self) -> float:
        """Get the current battery percentage."""
        try:
            return psutil.sensors_battery().percent
        except:
            return 0.0
    
    def can_execute_task(self, task_requirements: Dict) -> bool:
        """Check if the mobile device can execute a given task."""
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
        """Get the current available resources on the mobile device."""
        return {
            'cpu_percent': 100 - psutil.cpu_percent(),
            'memory_percent': 100 - psutil.virtual_memory().percent,
            'disk_percent': 100 - psutil.disk_usage('/').percent,
            'battery_percent': self._get_battery_percent()
        }
    
    def execute_task(self, task: Dict) -> bool:
        """Execute a task on the mobile device."""
        # Implementation would depend on the specific task type
        # This is a placeholder implementation
        return True
    
    def stop_task(self, task_id: str) -> bool:
        """Stop a running task on the mobile device."""
        # Implementation would depend on how tasks are tracked
        # This is a placeholder implementation
        return True 