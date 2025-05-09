import asyncio
import json
import logging
from typing import Dict, Optional
from bleak import BleakClient, BleakScanner
from config.settings import settings

logger = logging.getLogger(__name__)

class BluetoothProtocolHandler:
    """Handles Bluetooth communication."""
    
    def __init__(self, agent_core):
        """
        Initialize the Bluetooth protocol handler.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.connected_devices = {}
        self.running = False
        self.loop = None
    
    async def start_discovery(self):
        """Start discovering nearby Bluetooth devices."""
        try:
            devices = await BleakScanner.discover()
            for device in devices:
                if device.name and "agent" in device.name.lower():
                    logger.info(f"Found agent device: {device.name} ({device.address})")
                    await self.connect_device(device.address)
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
    
    async def connect_device(self, address: str):
        """
        Connect to a Bluetooth device.
        
        Args:
            address: Device address to connect to
        """
        try:
            client = BleakClient(address)
            await client.connect()
            self.connected_devices[address] = client
            logger.info(f"Connected to device: {address}")
        except Exception as e:
            logger.error(f"Error connecting to device {address}: {e}")
    
    async def send_data(self, device_address: str, data: Dict) -> bool:
        """
        Send data to a connected device.
        
        Args:
            device_address: Address of the target device
            data: Data to send
            
        Returns:
            Success status
        """
        try:
            if device_address not in self.connected_devices:
                return False
            
            client = self.connected_devices[device_address]
            message = json.dumps(data).encode()
            await client.write_gatt_char(settings.BLE_CHARACTERISTIC_UUID, message)
            return True
        except Exception as e:
            logger.error(f"Error sending data to {device_address}: {e}")
            return False
    
    def start(self) -> bool:
        """Start the Bluetooth protocol handler."""
        try:
            self.running = True
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.create_task(self._discovery_loop())
            return True
        except Exception as e:
            logger.error(f"Error starting Bluetooth handler: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the Bluetooth protocol handler."""
        try:
            self.running = False
            if self.loop:
                self.loop.stop()
            return True
        except Exception as e:
            logger.error(f"Error stopping Bluetooth handler: {e}")
            return False
    
    async def _discovery_loop(self):
        """Main discovery loop."""
        while self.running:
            await self.start_discovery()
            await asyncio.sleep(settings.DISCOVERY_INTERVAL) 