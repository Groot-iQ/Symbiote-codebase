import os
import json
import base64
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Device settings
    DEVICE_TYPE: str = "desktop"  # desktop, mobile, or iot
    DEVICE_NAME: str = "default_device"
    
    # Memory settings
    SHORT_TERM_CAPACITY: int = 1000
    LONG_TERM_STORAGE: str = "memory.db"
    
    # Task settings
    MAX_CONCURRENT_TASKS: int = 5
    PRIORITY_LEVELS: int = 5
    
    # Communication settings
    COMMUNICATION_PORT: int = 8000
    COMMUNICATION_TIMEOUT: float = 5.0
    DISCOVERY_INTERVAL: int = 30
    
    # BLE settings
    BLE_CHARACTERISTIC_UUID: str = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Nordic UART characteristic
    
    # Security settings
    ENCRYPTION_KEY: str = base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    # LLM settings
    GROQ_API_KEY: str = "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"
    GROQ_MODEL: str = "deepseek-r1-distill-llama-70b"
    
    # Agent Configuration
    AGENT_ID: str = os.getenv('AGENT_ID', 'default_agent')
    SECURITY_KEY: str = os.getenv('SECURITY_KEY', 'default_key')
    
    # Communication Configuration
    PROTOCOLS: list = os.getenv('PROTOCOLS', 'wifi,bluetooth').split(',')
    SECURITY_LEVEL: str = os.getenv('SECURITY_LEVEL', 'high')
    
    # Network Configuration
    WIFI_PORT: int = int(os.getenv('WIFI_PORT', '8000'))
    BLUETOOTH_PORT: int = int(os.getenv('BLUETOOTH_PORT', '8001'))
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '10'))
    
    def update_from_file(self, config_file: str):
        """Update settings from a configuration file."""
        if not os.path.exists(config_file):
            return
        
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    class Config:
        env_file = '.env'

# Create global settings instance
settings = Settings() 