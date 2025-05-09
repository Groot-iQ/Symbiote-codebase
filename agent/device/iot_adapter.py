import platform
import psutil
from typing import Dict
from .device_adapter import DeviceAdapter

class IoTAdapter(DeviceAdapter):
    """Adapter for IoT devices."""
    
    def __init__(self):
        """Initialize the IoT adapter."""
        self.system_info = platform.uname()
        self.capabilities = self._detect_capabilities()
        self.is_raspberry_pi = self._check_raspberry_pi()
    
    def _check_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'raspberry pi' in f.read().lower()
        except:
            return False
    
    def _detect_capabilities(self) -> Dict:
        """
        Detect the capabilities of the IoT device.
        
        Returns:
            Dictionary of device capabilities
        """
        capabilities = {
            'type': 'iot',
            'os': self.system_info.system,
            'os_version': self.system_info.version,
            'architecture': self.system_info.machine,
            'processor': self.system_info.processor,
            'has_internet': self._check_internet(),
            'has_bluetooth': self._check_bluetooth(),
            'has_wifi': self._check_wifi(),
            'has_sensors': self._check_sensors(),
            'has_actuators': self._check_actuators(),
            'has_gpio': False,  # Will be updated if on Raspberry Pi
            'has_led': False,   # Will be updated if on Raspberry Pi
            'has_button': False,  # Will be updated if on Raspberry Pi
            'has_display': self._check_display(),
            'has_speaker': self._check_speaker(),
            'has_microphone': self._check_microphone(),
            'has_camera': self._check_camera()
        }
        
        # Update Raspberry Pi specific capabilities
        if self.is_raspberry_pi:
            capabilities.update({
                'has_gpio': self._check_gpio(),
                'has_led': self._check_led(),
                'has_button': self._check_button()
            })
        
        return capabilities
    
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
            import bleak
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
    
    def _check_sensors(self) -> bool:
        """Check if the device has any sensors."""
        # This would typically use platform-specific APIs
        # For now, we'll assume it has basic sensors
        return True
    
    def _check_actuators(self) -> bool:
        """Check if the device has any actuators."""
        # This would typically use platform-specific APIs
        # For now, we'll assume it has basic actuators
        return True
    
    def _check_gpio(self) -> bool:
        """Check if the device has GPIO pins."""
        if not self.is_raspberry_pi:
            return False
        try:
            import RPi.GPIO
            return True
        except:
            return False
    
    def _check_led(self) -> bool:
        """Check if the device has an LED."""
        if not self.is_raspberry_pi:
            return False
        # This would typically use platform-specific APIs
        # For now, we'll assume it has an LED
        return True
    
    def _check_button(self) -> bool:
        """Check if the device has a button."""
        if not self.is_raspberry_pi:
            return False
        # This would typically use platform-specific APIs
        # For now, we'll assume it has a button
        return True
    
    def _check_display(self) -> bool:
        """Check if the device has a display."""
        try:
            import Adafruit_SSD1306
            return True
        except:
            return False
    
    def _check_speaker(self) -> bool:
        """Check if the device has a speaker."""
        try:
            import pygame
            pygame.mixer.init()
            return True
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
    
    def _check_camera(self) -> bool:
        """Check if the device has a camera."""
        try:
            import cv2
            return len(cv2.VideoCapture.list_ports()) > 0
        except:
            return False
    
    def get_capabilities(self) -> Dict:
        """Get the capabilities of the IoT device."""
        return self.capabilities
    
    def get_device_info(self) -> Dict:
        """Get information about the IoT device."""
        return {
            'type': 'iot',
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
            'temperature': self._get_temperature(),
            'uptime': self._get_uptime()
        }
    
    def _get_temperature(self) -> float:
        """Get the current device temperature."""
        try:
            import psutil
            return psutil.sensors_temperatures()['cpu_thermal'][0].current
        except:
            return 0.0
    
    def _get_uptime(self) -> float:
        """Get the device uptime in seconds."""
        try:
            import psutil
            return psutil.boot_time()
        except:
            return 0.0
    
    def can_execute_task(self, task_requirements: Dict) -> bool:
        """Check if the IoT device can execute a given task."""
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
        """Get the current available resources on the IoT device."""
        return {
            'cpu_percent': 100 - psutil.cpu_percent(),
            'memory_percent': 100 - psutil.virtual_memory().percent,
            'disk_percent': 100 - psutil.disk_usage('/').percent,
            'temperature': self._get_temperature()
        }
    
    def execute_task(self, task: Dict) -> bool:
        """Execute a task on the IoT device."""
        # Implementation would depend on the specific task type
        # This is a placeholder implementation
        return True
    
    def stop_task(self, task_id: str) -> bool:
        """Stop a running task on the IoT device."""
        # Implementation would depend on how tasks are tracked
        # This is a placeholder implementation
        return True 