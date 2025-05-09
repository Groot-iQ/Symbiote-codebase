import logging
import threading
import time
from typing import Dict, List, Optional
from config.settings import settings
from utils.security import SecurityManager

logger = logging.getLogger(__name__)

class CommunicationLayer:
    """
    Manages communication between devices using multiple protocols (Bluetooth and WiFi).
    This class coordinates:
    1. Device discovery and connection management
    2. Data transfer between devices
    3. Protocol selection and fallback
    4. Security and encryption
    
    The layer supports multiple communication protocols and automatically
    selects the best available protocol for each communication.
    """
    
    def __init__(self, agent_core, config: Dict = None):
        """
        Initialize the communication layer.
        This sets up protocol handlers, security, and device tracking.
        
        Args:
            agent_core: Reference to the main agent that controls the system
            config: Configuration dictionary containing:
                   - protocols: List of enabled protocols ('wifi', 'bluetooth')
                   - security_level: Security level for communication
                   - discovery_interval: Time between device discovery cycles
        """
        self.agent_core = agent_core
        self.config = config or {}
        
        # Get configuration values with defaults
        self.protocols = self.config.get('protocols', ['wifi', 'bluetooth'])
        self.security_level = self.config.get('security_level', settings.SECURITY_LEVEL)
        self.discovery_interval = self.config.get('discovery_interval', settings.DISCOVERY_INTERVAL)
        
        # Track discovered devices and active transfers
        self.available_devices = {}  # Dictionary of discovered devices: {device_id: device_info}
        self.active_transfers = {}   # Dictionary of ongoing data transfers
        self.device_status = {}      # Dictionary of device connection status
        
        # Initialize security manager for data encryption and authentication
        self.security = SecurityManager()
        
        # Initialize protocol handlers for each supported protocol
        self.protocol_handlers = {}
        for protocol in self.protocols:
            if protocol == 'bluetooth':
                from .bluetooth_protocol import BluetoothProtocolHandler
                self.protocol_handlers[protocol] = BluetoothProtocolHandler(self.agent_core)
            elif protocol == 'wifi':
                from .wifi_protocol import WifiProtocolHandler
                self.protocol_handlers[protocol] = WifiProtocolHandler(self.agent_core)
        
        self.running = False  # Flag to control the discovery loop
        self.discovery_thread = None  # Thread for device discovery
    
    def start(self) -> bool:
        """
        Start the communication layer.
        This initializes and starts all protocol handlers.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            # Start all protocol handlers
            for protocol, handler in self.protocol_handlers.items():
                if not handler.start():
                    logger.error(f"Failed to start {protocol} handler")
                    return False
                logger.info(f"Started {protocol} handler")
            
            # Start discovery thread
            self.running = True
            self.discovery_thread = threading.Thread(target=self._discovery_loop)
            self.discovery_thread.daemon = True
            self.discovery_thread.start()
            
            # Announce presence
            self.announce_presence()
            
            return True
        except Exception as e:
            logger.error(f"Error starting communication layer: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the communication layer.
        This stops all protocol handlers and cleans up resources.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
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
        """
        Main discovery loop that runs continuously.
        This method:
        1. Periodically discovers devices using all available protocols
        2. Updates the list of available devices
        3. Maintains device information including protocol used
        4. Handles device status updates
        
        The loop runs every discovery_interval seconds.
        """
        while self.running:
            try:
                logger.info("Starting device discovery cycle...")
                discovered_devices = {}
                
                # Try to discover devices using each protocol
                for protocol, handler in self.protocol_handlers.items():
                    try:
                        logger.info(f"Discovering devices using {protocol} protocol...")
                        # Get list of discovered devices from the protocol handler
                        protocol_devices = handler.discover_devices()
                        logger.info(f"Found {len(protocol_devices)} devices using {protocol}")
                        
                        # Process each discovered device
                        for device_id, device_info in protocol_devices.items():
                            # Add protocol information to device info
                            device_info['protocol'] = protocol
                            device_info['last_seen'] = time.time()
                            
                            # Update discovered devices
                            discovered_devices[device_id] = device_info
                            
                            # Update device status
                            if device_id not in self.device_status:
                                self.device_status[device_id] = 'new'
                            elif self.device_status[device_id] == 'disconnected':
                                self.device_status[device_id] = 'reconnected'
                            
                            # Notify agent core about device status change
                            self.agent_core.handle_device_status_change(device_id, self.device_status[device_id])
                    except Exception as e:
                        logger.error(f"Error in discovery loop for {protocol}: {e}", exc_info=True)
                
                # Update available devices
                self.available_devices = discovered_devices
                
                # Check for disconnected devices
                current_time = time.time()
                for device_id, device_info in list(self.available_devices.items()):
                    if current_time - device_info['last_seen'] > self.discovery_interval * 2:
                        logger.warning(f"Device {device_id} appears to be disconnected")
                        self.device_status[device_id] = 'disconnected'
                        self.agent_core.handle_device_status_change(device_id, 'disconnected')
                
                logger.info(f"Current available devices: {list(self.available_devices.keys())}")
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}", exc_info=True)
            
            # Wait for the specified interval before next discovery cycle
            time.sleep(self.discovery_interval)
    
    def send_data(self, target_id: str, data: Dict, protocol: str = None) -> bool:
        """
        Send data to a specific device.
        This method:
        1. Uses specified protocol if provided
        2. Otherwise tries all available protocols until one succeeds
        3. Handles encryption and security
        
        Args:
            target_id: ID of the target device
            data: Data to send (will be encrypted)
            protocol: Specific protocol to use (optional)
            
        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        try:
            # If a specific protocol is requested, use only that protocol
            if protocol:
                if protocol not in self.protocol_handlers:
                    return False
                return self.protocol_handlers[protocol].send_data(target_id, data)
            
            # Try all available protocols until one succeeds
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
        This method:
        1. Uses specified protocol if provided
        2. Otherwise tries all available protocols
        3. Handles encryption and security
        
        Args:
            data: Data to broadcast (will be encrypted)
            protocol: Specific protocol to use (optional)
            
        Returns:
            bool: True if data was broadcast successfully, False otherwise
        """
        try:
            # If a specific protocol is requested, use only that protocol
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
        This method:
        1. Creates an announcement message with device info
        2. Broadcasts the announcement to all nearby devices
        3. Includes device capabilities and type
        
        Returns:
            bool: True if announcement was sent successfully, False otherwise
        """
        try:
            # Create announcement message
            announcement = {
                'type': 'announcement',
                'sender_id': self.agent_core.agent_id,
                'device_type': self.agent_core.config.get('device_type'),
                'capabilities': self.agent_core.device_adapter.get_capabilities()
            }
            
            # Broadcast the announcement
            return self.broadcast_data(announcement)
        except Exception as e:
            logger.error(f"Error announcing presence: {e}")
            return False
    
    def receive_data(self, sender_id: str, data: Dict) -> bool:
        """
        Handle received data from another device.
        This method:
        1. Verifies the data's authenticity using security manager
        2. Decrypts the received data
        3. Processes the data through the agent core
        
        Args:
            sender_id: ID of the sending device
            data: Received data containing:
                 - signature: Security signature
                 - data: Encrypted data payload
                 
        Returns:
            bool: True if data was processed successfully, False otherwise
        """
        try:
            # Verify the data's signature
            if not self.security.verify_token(data['signature'], data):
                print(f"Invalid signature from {sender_id}")
                return False
            
            # Decrypt the data
            decrypted_data = self.security.decrypt_data(data['data'])
            
            # Process the data through the agent core
            return self.agent_core.handle_received_data(sender_id, decrypted_data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return False
    
    def get_available_devices(self) -> Dict:
        """
        Get information about all available devices.
        This returns the current list of discovered devices and their information.
        
        Returns:
            Dict: Dictionary of available devices and their information:
                  {device_id: {
                      'protocol': protocol used,
                      'capabilities': device capabilities,
                      'device_type': type of device,
                      ...
                  }}
        """
        return self.available_devices
    
    def is_device_available(self, device_id: str) -> bool:
        """
        Check if a specific device is available.
        This checks if the device is in the list of discovered devices.
        
        Args:
            device_id: ID of the device to check
            
        Returns:
            bool: True if the device is available, False otherwise
        """
        return device_id in self.available_devices
    
    def handle_device_disconnection(self, device_id: str):
        """
        Handle device disconnection.
        This method:
        1. Updates device status
        2. Notifies agent core
        3. Updates available devices list
        
        Args:
            device_id: ID of the disconnected device
        """
        if device_id in self.available_devices:
            self.device_status[device_id] = 'disconnected'
            self.agent_core.handle_device_status_change(device_id, 'disconnected')
            logger.info(f"Device {device_id} disconnected") 