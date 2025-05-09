import asyncio
import json
import logging
import websockets
from typing import Dict, Optional
from config.settings import settings
import socket
import time

logger = logging.getLogger(__name__)

class WifiProtocolHandler:
    """
    Handles WiFi communication using WebSocket.
    This class provides:
    1. WebSocket server for device-to-device communication
    2. Connection management for multiple clients
    3. Message handling and routing
    4. Broadcast capabilities for announcements
    
    The handler uses the websockets library for WebSocket support.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the WiFi protocol handler.
        This sets up the WebSocket server and client tracking.
        
        Args:
            agent_core: Reference to the agent core for message handling
        """
        self.agent_core = agent_core
        self.server = None  # WebSocket server instance
        self.clients = {}   # Dictionary of connected clients: {client_id: websocket}
        self.running = False  # Flag to control server operation
        self.loop = None  # Asyncio event loop for async operations
        self.port = settings.WIFI_PORT
        self.host = settings.WIFI_HOST
    
    async def start_server(self):
        """
        Start the WebSocket server.
        This method:
        1. Creates a WebSocket server on the specified port
        2. Sets up connection handling
        3. Listens for incoming connections
        4. Implements proper error handling
        
        The server binds to all network interfaces (0.0.0.0).
        """
        try:
            logger.info(f"Starting WiFi server on {self.host}:{self.port}")
            
            # Check if port is already in use
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((self.host, self.port))
                sock.close()
            except OSError:
                logger.error(f"Port {self.port} is already in use")
                return False
            
            # Create WebSocket server
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port,
                ping_interval=30,  # Keep connections alive
                ping_timeout=10,
                close_timeout=5
            )
            
            logger.info("WiFi server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting WiFi server: {e}")
            return False
    
    async def handle_connection(self, websocket, path):
        """
        Handle a WebSocket connection.
        This method:
        1. Receives initial connection message
        2. Stores client connection information
        3. Processes incoming messages
        4. Handles client disconnection
        5. Implements connection monitoring
        
        Args:
            websocket: WebSocket connection object
            path: Connection path (unused)
        """
        client_id = None
        try:
            # Wait for initial message with timeout
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                client_id = data.get('device_id')
                
                if not client_id:
                    logger.error("No device ID provided")
                    return
                
                logger.info(f"New client connected: {client_id}")
                self.clients[client_id] = websocket
                
                # Send acknowledgment
                await websocket.send(json.dumps({
                    'type': 'connection_ack',
                    'status': 'connected'
                }))
                
                # Monitor connection
                while True:
                    try:
                        message = await websocket.recv()
                        # Handle incoming messages
                        await self.handle_message(client_id, message)
                    except websockets.exceptions.ConnectionClosed:
                        break
                    except Exception as e:
                        logger.error(f"Error handling message from {client_id}: {e}")
                        break
                        
            except asyncio.TimeoutError:
                logger.error("Connection timeout - no initial message received")
                return
            except json.JSONDecodeError:
                logger.error("Invalid JSON in initial message")
                return
                
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"Client disconnected: {client_id}")
    
    async def handle_message(self, client_id: str, message: str):
        """
        Handle a received message.
        This method:
        1. Extracts sender information
        2. Forwards message to agent core for processing
        
        Args:
            client_id: ID of the sending device
            message: Received message
        """
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'heartbeat':
                # Send heartbeat response
                await self.send_data(client_id, {
                    'type': 'heartbeat_ack',
                    'timestamp': time.time()
                })
            else:
                # Forward message to agent core
                await self.agent_core.handle_received_data(client_id, data)
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {client_id}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
    
    async def connect_device(self, device_id: str) -> bool:
        """
        Connect to a device using its ID.
        This method:
        1. Checks if the device is already connected
        2. Tries to establish a WebSocket connection to the device
        3. Sends an initial connection message
        4. Waits for acknowledgment
        5. Handles connection errors
        
        Args:
            device_id: ID of the target device
            
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            logger.info(f"Attempting to connect to device: {device_id}")
            
            # Check if already connected
            if device_id in self.clients:
                logger.info(f"Already connected to device: {device_id}")
                return True
            
            # Try to establish WebSocket connection
            uri = f"ws://{device_id}:{self.port}"
            try:
                websocket = await websockets.connect(
                    uri,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5
                )
                
                # Send initial connection message
                await websocket.send(json.dumps({
                    'type': 'connection_request',
                    'device_id': self.agent_core.device_id
                }))
                
                # Wait for acknowledgment
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'connection_ack':
                        self.clients[device_id] = websocket
                        logger.info(f"Successfully connected to device: {device_id}")
                        return True
                    else:
                        logger.error(f"Invalid connection response from {device_id}")
                        await websocket.close()
                        return False
                        
                except asyncio.TimeoutError:
                    logger.error(f"Connection timeout for device: {device_id}")
                    await websocket.close()
                    return False
                    
            except Exception as e:
                logger.error(f"Error connecting to device {device_id}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error in connect_device: {e}")
            return False
    
    async def send_data(self, device_id: str, data: Dict) -> bool:
        """
        Send data to a connected device.
        This method:
        1. Verifies client connection
        2. Converts data to JSON
        3. Sends data through WebSocket
        4. Implements retry logic
        
        Args:
            device_id: ID of the target device
            data: Data to send (will be converted to JSON)
            
        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        try:
            if device_id not in self.clients:
                logger.error(f"Not connected to device: {device_id}")
                return False
            
            websocket = self.clients[device_id]
            message = json.dumps(data)
            
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await websocket.send(message)
                    return True
                except websockets.exceptions.ConnectionClosed:
                    if attempt < max_retries - 1:
                        logger.warning(f"Connection closed, retrying... (attempt {attempt + 1})")
                        # Try to reconnect
                        if await self.connect_device(device_id):
                            websocket = self.clients[device_id]
                            continue
                    break
                except Exception as e:
                    logger.error(f"Error sending data to {device_id}: {e}")
                    break
            
            return False
            
        except Exception as e:
            logger.error(f"Error in send_data: {e}")
            return False
    
    async def broadcast_data(self, data: Dict) -> bool:
        """
        Broadcast data to all connected devices.
        This method:
        1. Checks for connected devices
        2. Sends data to each device
        3. Continues even if some sends fail
        
        Args:
            data: Data to broadcast (will be converted to JSON)
            
        Returns:
            bool: True if data was sent to at least one device, False otherwise
        """
        try:
            if not self.clients:
                logger.warning("No devices connected for broadcast")
                return False
            
            message = json.dumps(data)
            success = False
            
            for device_id, websocket in list(self.clients.items()):
                try:
                    await websocket.send(message)
                    success = True
                except Exception as e:
                    logger.error(f"Error broadcasting to device {device_id}: {e}")
                    # Remove failed device
                    del self.clients[device_id]
                    continue
            
            return success
            
        except Exception as e:
            logger.error(f"Error in broadcast_data: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the WiFi protocol handler.
        This method:
        1. Creates a new asyncio event loop
        2. Sets up the loop for async operations
        3. Starts the WebSocket server
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.running = True
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.create_task(self.start_server())
            return True
        except Exception as e:
            logger.error(f"Error starting WiFi handler: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the WiFi protocol handler.
        This method:
        1. Stops the WebSocket server
        2. Cleans up the event loop
        3. Releases system resources
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            self.running = False
            if self.server:
                self.server.close()
            if self.loop:
                self.loop.stop()
            return True
        except Exception as e:
            logger.error(f"Error stopping WiFi handler: {e}")
            return False 