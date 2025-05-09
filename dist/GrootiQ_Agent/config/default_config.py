"""
Default configuration for the Mobile AI Agent System.
"""

# Agent Configuration
DEFAULT_AGENT_ID = 'default_agent'
DEFAULT_SECURITY_KEY = 'your_secret_key_here'
DEFAULT_DEVICE_TYPE = 'desktop'

# Memory Configuration
DEFAULT_SHORT_TERM_CAPACITY = 1000
DEFAULT_LONG_TERM_STORAGE = './agent_memory.db'

# Task Configuration
DEFAULT_MAX_CONCURRENT_TASKS = 5
DEFAULT_PRIORITY_LEVELS = 3

# Communication Configuration
DEFAULT_PROTOCOLS = ['wifi', 'bluetooth']
DEFAULT_SECURITY_LEVEL = 'high'
DEFAULT_DISCOVERY_INTERVAL = 30

# Network Configuration
DEFAULT_WIFI_PORT = 8000
DEFAULT_BLUETOOTH_PORT = 8001
DEFAULT_MAX_CONNECTIONS = 10

# Device-specific Configuration
DESKTOP_CONFIG = {
    'type': 'desktop',
    'capabilities': [
        'has_gpu',
        'has_internet',
        'has_bluetooth',
        'has_wifi',
        'has_camera',
        'has_microphone',
        'has_speakers',
        'has_display',
        'has_keyboard',
        'has_mouse'
    ]
}

MOBILE_CONFIG = {
    'type': 'mobile',
    'capabilities': [
        'has_internet',
        'has_bluetooth',
        'has_wifi',
        'has_camera',
        'has_microphone',
        'has_speakers',
        'has_display',
        'has_touchscreen',
        'has_gps',
        'has_accelerometer',
        'has_gyroscope',
        'has_battery'
    ]
}

IOT_CONFIG = {
    'type': 'iot',
    'capabilities': [
        'has_internet',
        'has_bluetooth',
        'has_wifi',
        'has_sensors',
        'has_actuators',
        'has_gpio',
        'has_led',
        'has_button',
        'has_display',
        'has_speaker',
        'has_microphone',
        'has_camera'
    ]
}

# Device configuration mapping
DEVICE_CONFIGS = {
    'desktop': DESKTOP_CONFIG,
    'mobile': MOBILE_CONFIG,
    'iot': IOT_CONFIG
} 