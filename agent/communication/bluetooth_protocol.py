import asyncio
import json
import logging
from typing import Dict, Optional
from bleak import BleakClient, BleakScanner  # Bleak is a cross-platform BLE library
from config.settings import settings

logger = logging.getLogger(__name__)

class BluetoothProtocolHandler:
    """
    Handles Bluetooth Low Energy (BLE) communication between devices.
    This class provides:
    1. Device discovery using BLE scanning
    2. Connection management with BLE devices
    3. Data transfer using GATT characteristics
    4. Automatic reconnection and error handling
    
    The handler uses the Bleak library for cross-platform BLE support.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Bluetooth protocol handler.
        This sets up the connection tracking and event loop.
        
        Args:
            agent_core: Reference to the main agent that controls the system
        """
        self.agent_core = agent_core
        self.connected_devices = {}  # Dictionary to store connected devices: {address: BleakClient}
        self.running = False  # Flag to control the discovery loop
        self.loop = None  # Asyncio event loop for async operations
    
    async def start_discovery(self):
        """
        Start discovering nearby Bluetooth devices.
        This method:
        1. Scans for BLE devices in range
        2. Logs all discovered devices
        3. Attempts to connect to matching devices
        
        The discovery process uses BLE advertising packets to find devices.
        """
        try:
            logger.info("Starting Bluetooth device discovery...")
            # Scan for nearby BLE devices
            devices = await BleakScanner.discover()
            logger.info(f"Found {len(devices)} Bluetooth devices")
            
            # Process each discovered device
            for device in devices:
                logger.info(f"Found device: {device.name or 'Unknown'} ({device.address})")
                # Log device details for debugging
                logger.debug(f"Device details: {device.details}")
                
                # Try to connect to all devices initially
                try:
                    await self.connect_device(device.address)
                except Exception as e:
                    logger.error(f"Failed to connect to device {device.address}: {e}")
                    
        except Exception as e:
            logger.error(f"Error discovering devices: {e}", exc_info=True)
    
    async def connect_device(self, address: str):
        """
        Connect to a Bluetooth device using its address.
        This method:
        1. Creates a new BLE client for the device
        2. Establishes a GATT connection
        3. Stores the connected client for future use
        4. Implements reconnection logic
        
        Args:
            address: The Bluetooth address of the device to connect to
        """
        try:
            logger.info(f"Attempting to connect to device: {address}")
            # Create a new BLE client for the device
            client = BleakClient(address)
            
            # Set up connection callback
            client.set_disconnected_callback(self._handle_disconnection)
            
            # Attempt to establish connection with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await client.connect()
                    # Store the connected client
                    self.connected_devices[address] = client
                    logger.info(f"Successfully connected to device: {address}")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(1)
                    else:
                        raise e
            
            # Log currently connected devices
            logger.info(f"Currently connected devices: {list(self.connected_devices.keys())}")
        except Exception as e:
            logger.error(f"Error connecting to device {address}: {e}", exc_info=True)
            raise
    
    async def _handle_disconnection(self, client):
        """
        Handle device disconnection.
        This method:
        1. Logs the disconnection
        2. Attempts to reconnect if the device is still in range
        3. Updates the connected devices list
        
        Args:
            client: The disconnected BleakClient
        """
        address = client.address
        logger.warning(f"Device disconnected: {address}")
        
        # Remove from connected devices
        if address in self.connected_devices:
            del self.connected_devices[address]
        
        # Attempt to reconnect
        try:
            await self.connect_device(address)
        except Exception as e:
            logger.error(f"Failed to reconnect to device {address}: {e}")
    
    async def send_data(self, device_address: str, data: Dict) -> bool:
        """
        Send data to a connected device.
        This method:
        1. Verifies connection to the target device
        2. Converts data to JSON format
        3. Writes data to the BLE characteristic
        
        Args:
            device_address: The address of the target device
            data: The data to send (will be converted to JSON)
            
        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        try:
            # Check if we're connected to the target device
            if device_address not in self.connected_devices:
                logger.error(f"Not connected to device: {device_address}")
                return False
            
            # Get the client for the target device
            client = self.connected_devices[device_address]
            # Convert data to JSON and encode as bytes
            message = json.dumps(data).encode()
            # Write data to the BLE characteristic
            await client.write_gatt_char(settings.BLE_CHARACTERISTIC_UUID, message)
            return True
        except Exception as e:
            logger.error(f"Error sending data to {device_address}: {e}")
            return False
    
    async def broadcast_data(self, data: Dict) -> bool:
        """
        Broadcast data to all connected devices.
        This method:
        1. Converts data to JSON format
        2. Sends data to all connected devices
        3. Handles errors for each device independently
        
        Args:
            data: Data to broadcast (will be converted to JSON)
            
        Returns:
            bool: True if data was sent to at least one device, False otherwise
        """
        try:
            if not self.connected_devices:
                logger.warning("No devices connected for broadcast")
                return False
            
            # Convert data to JSON and encode as bytes
            message = json.dumps(data).encode()
            
            # Track if any send was successful
            success = False
            
            # Send to all connected devices
            for address, client in self.connected_devices.items():
                try:
                    await client.write_gatt_char(settings.BLE_CHARACTERISTIC_UUID, message)
                    success = True
                    logger.debug(f"Broadcast sent to device: {address}")
                except Exception as e:
                    logger.error(f"Error broadcasting to device {address}: {e}")
                    continue
            
            return success
        except Exception as e:
            logger.error(f"Error in broadcast_data: {e}")
            return False

    def discover_devices(self) -> Dict:
        """
        Discover nearby Bluetooth devices.
        This method:
        1. Runs the discovery process
        2. Returns a dictionary of discovered devices
        
        Returns:
            Dict: Dictionary of discovered devices: {device_id: device_info}
        """
        try:
            # Create a new event loop for discovery
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run discovery
            discovered = loop.run_until_complete(self.start_discovery())
            loop.close()
            
            # Convert discovered devices to dictionary
            devices = {}
            for device in discovered:
                device_id = device.address
                devices[device_id] = {
                    'name': device.name or 'Unknown',
                    'address': device.address,
                    'rssi': device.rssi,
                    'metadata': device.metadata
                }
            
            return devices
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return {}
    
    def start(self) -> bool:
        """
        Start the Bluetooth protocol handler.
        This method:
        1. Creates a new asyncio event loop
        2. Sets up the loop for async operations
        3. Starts the discovery process
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.running = True
            # Create and set up a new event loop for async operations
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            # Start the discovery loop
            self.loop.create_task(self._discovery_loop())
            return True
        except Exception as e:
            logger.error(f"Error starting Bluetooth handler: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the Bluetooth protocol handler.
        This method:
        1. Stops the discovery loop
        2. Cleans up the event loop
        3. Releases system resources
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            self.running = False
            if self.loop:
                self.loop.stop()
            return True
        except Exception as e:
            logger.error(f"Error stopping Bluetooth handler: {e}")
            return False
    
    async def _discovery_loop(self):
        """
        Main discovery loop that runs continuously.
        This method:
        1. Periodically scans for new devices
        2. Attempts to connect to matching devices
        3. Waits for the specified interval between scans
        
        The loop runs asynchronously to avoid blocking the main thread.
        """
        while self.running:
            # Start a new discovery cycle
            await self.start_discovery()
            # Wait for the specified interval before next discovery
            await asyncio.sleep(settings.DISCOVERY_INTERVAL) 