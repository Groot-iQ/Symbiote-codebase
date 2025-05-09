import os
import json
import base64
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Global settings for the agent system.
    This class manages all configuration parameters for the agent, including:
    1. Device settings (type, name)
    2. Memory management (capacity, storage)
    3. Task management (concurrency, priorities)
    4. Communication settings (ports, timeouts)
    5. Security settings (encryption, keys)
    6. LLM integration (API keys, models)
    
    Settings can be loaded from:
    - Environment variables
    - .env file
    - Configuration file
    - Default values
    """
    
    # Device settings - Controls the type and name of the device
    DEVICE_TYPE: str = "desktop"  # Options: desktop, mobile, or iot
    DEVICE_NAME: str = "default_device"  # Name of the device for identification
    
    # Memory settings - Controls how the agent stores and manages information
    SHORT_TERM_CAPACITY: int = 1000  # Number of items in short-term memory
    LONG_TERM_STORAGE: str = "memory.db"  # File for persistent storage
    
    # Task settings - Controls how the agent manages tasks
    MAX_CONCURRENT_TASKS: int = 5  # Maximum number of tasks that can run simultaneously
    PRIORITY_LEVELS: int = 5  # Number of priority levels for task management
    
    # Communication settings - Controls how devices communicate with each other
    COMMUNICATION_PORT: int = 8000  # Default port for communication
    COMMUNICATION_TIMEOUT: float = 5.0  # Timeout for communication operations in seconds
    DISCOVERY_INTERVAL: int = 30  # Time between device discovery attempts in seconds
    
    # BLE (Bluetooth Low Energy) settings
    BLE_CHARACTERISTIC_UUID: str = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # UUID for BLE communication
    
    # Security settings - Controls encryption and security features
    ENCRYPTION_KEY: str = base64.urlsafe_b64encode(os.urandom(32)).decode()  # Random encryption key
    
    # LLM (Language Model) settings - Controls AI model integration
    GROQ_API_KEY: str = "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"
    GROQ_MODEL: str = "deepseek-r1-distill-llama-70b"
    
    # Agent Configuration - Basic agent identification and security
    AGENT_ID: str = os.getenv('AGENT_ID', 'default_agent')  # Unique identifier for the agent
    SECURITY_KEY: str = os.getenv('SECURITY_KEY', 'default_key')  # Key for secure communication
    
    # Communication Configuration - Controls which protocols are used
    PROTOCOLS: list = os.getenv('PROTOCOLS', 'wifi,bluetooth').split(',')  # Available communication protocols
    SECURITY_LEVEL: str = os.getenv('SECURITY_LEVEL', 'high')  # Level of security for communication
    
    # Network Configuration - Controls network-related settings
    WIFI_PORT: int = int(os.getenv('WIFI_PORT', '8000'))  # Port for WiFi communication
    BLUETOOTH_PORT: int = int(os.getenv('BLUETOOTH_PORT', '8001'))  # Port for Bluetooth communication
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '10'))  # Maximum number of simultaneous connections
    
    # WiFi settings
    WIFI_HOST: str = os.getenv('WIFI_HOST', '0.0.0.0')  # Host to bind WiFi server to
    WIFI_PORT: int = int(os.getenv('WIFI_PORT', '8765'))  # Port for WiFi communication
    
    # Token settings
    TOKEN_EXPIRY: int = int(os.getenv('TOKEN_EXPIRY', '3600'))  # Token expiry time in seconds
    
    def update_from_file(self, config_file: str):
        """
        Update settings from a configuration file.
        This method:
        1. Loads settings from a JSON file
        2. Updates only existing settings
        3. Preserves default values for missing settings
        
        Args:
            config_file: Path to the configuration file containing:
                        - JSON format settings
                        - Key-value pairs matching class attributes
        """
        if not os.path.exists(config_file):
            return
        
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    class Config:
        """
        Pydantic configuration class.
        This class controls how settings are loaded and validated.
        """
        env_file = '.env'  # Specifies the environment file to use

# Create global settings instance
settings = Settings() 