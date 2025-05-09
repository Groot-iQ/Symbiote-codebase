import logging
import threading
import time
from typing import Dict, List, Optional
from config.settings import settings
from utils.security import SecurityManager

logger = logging.getLogger(__name__)

class CommunicationLayer:
    """Manages communication between devices."""
    
    def __init__(self, agent_core, config: Dict = None):
        """
        Initialize the communication layer.
        
        Args:
            agent_core: Reference to the agent core
            config: Communication configuration
        """
        self.agent_core = agent_core
        self.config = config or {}
        
        self.protocols = self.config.get('protocols', ['wifi', 'bluetooth'])
        self.security_level = self.config.get('security_level', settings.SECURITY_LEVEL)
        self.discovery_interval = self.config.get('discovery_interval', settings.DISCOVERY_INTERVAL)
        
        self.available_devices = {}  # Connected and discovered devices
        self.active_transfers = {}  # Ongoing data transfers
        
        # Initialize security manager
        self.security = SecurityManager()
        
        # Initialize protocol handlers
        self.protocol_handlers = {}
        for protocol in self.protocols:
            if protocol == 'bluetooth':
                from .bluetooth_protocol import BluetoothProtocolHandler
                self.protocol_handlers[protocol] = BluetoothProtocolHandler(self.agent_core)
            elif protocol == 'wifi':
                from .wifi_protocol import WifiProtocolHandler
                self.protocol_handlers[protocol] = WifiProtocolHandler(self.agent_core)
        
        self.running = False
    
    def start(self) -> bool:
        """Start the communication layer."""
        try:
            # Start all protocol handlers
            for handler in self.protocol_handlers.values():
                if not handler.start():
                    return False
            return True
        except Exception as e:
            logger.error(f"Error starting communication layer: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the communication layer."""
        try:
            # Stop all protocol handlers
            for handler in self.protocol_handlers.values():
                if not handler.stop():
                    return False
            return True
        except Exception as e:
            logger.error(f"Error stopping communication layer: {e}")
            return False
    
    def _discovery_loop(self):
        """Periodically discover available devices."""
        while self.running:
            # Perform discovery through all available protocols
            for protocol, handler in self.protocol_handlers.items():
                try:
                    discovered = handler.discover_devices()
                    
                    # Update available devices
                    for device_id, device_info in discovered.items():
                        # Add protocol information
                        device_info['protocol'] = protocol
                        
                        # Update or add to available devices
                        if device_id in self.available_devices:
                            self.available_devices[device_id].update(device_info)
                        else:
                            self.available_devices[device_id] = device_info
                except Exception as e:
                    print(f"Error in discovery loop for {protocol}: {e}")
            
            # Sleep until next discovery interval
            time.sleep(self.discovery_interval)
    
    def send_data(self, target_id: str, data: Dict, protocol: str = None) -> bool:
        """
        Send data to another device.
        
        Args:
            target_id: ID of the target device
            data: Data to send
            protocol: Protocol to use (optional)
            
        Returns:
            Success status
        """
        try:
            # If protocol is specified, use only that protocol
            if protocol:
                if protocol not in self.protocol_handlers:
                    return False
                return self.protocol_handlers[protocol].send_data(target_id, data)
            
            # Try all available protocols
            for handler in self.protocol_handlers.values():
                if handler.send_data(target_id, data):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
    
    def broadcast_data(self, data: Dict, protocol: str = None) -> bool:
        """
        Broadcast data to all nearby devices.
        
        Args:
            data: Data to broadcast
            protocol: Protocol to use (optional)
            
        Returns:
            Success status
        """
        try:
            # If protocol is specified, use only that protocol
            if protocol:
                if protocol not in self.protocol_handlers:
                    return False
                return self.protocol_handlers[protocol].broadcast_data(data)
            
            # Try all available protocols
            success = False
            for handler in self.protocol_handlers.values():
                if handler.broadcast_data(data):
                    success = True
            
            return success
        except Exception as e:
            logger.error(f"Error broadcasting data: {e}")
            return False
    
    def announce_presence(self) -> bool:
        """
        Announce this device's presence to nearby devices.
        
        Returns:
            Success status
        """
        try:
            announcement = {
                'type': 'announcement',
                'sender_id': self.agent_core.agent_id,
                'device_type': self.agent_core.config.get('device_type'),
                'capabilities': self.agent_core.device_adapter.get_capabilities()
            }
            
            return self.broadcast_data(announcement)
        except Exception as e:
            logger.error(f"Error announcing presence: {e}")
            return False
    
    def receive_data(self, sender_id: str, data: Dict) -> bool:
        """
        Handle received data from another device.
        
        Args:
            sender_id: ID of the sending device
            data: Received data
            
        Returns:
            Success status
        """
        try:
            # Verify the signature
            if not self.security.verify_token(data['signature'], data):
                print(f"Invalid signature from {sender_id}")
                return False
            
            # Decrypt the data
            decrypted_data = self.security.decrypt_data(data['data'])
            
            # Process the data
            return self.agent_core.handle_received_data(sender_id, decrypted_data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return False
    
    def get_available_devices(self) -> Dict:
        """
        Get information about available devices.
        
        Returns:
            Dictionary of available devices
        """
        return self.available_devices
    
    def is_device_available(self, device_id: str) -> bool:
        """
        Check if a device is available.
        
        Args:
            device_id: ID of the device to check
            
        Returns:
            Whether the device is available
        """
        return device_id in self.available_devices 