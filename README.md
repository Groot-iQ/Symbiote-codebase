# Mobile AI Agent System

A sophisticated mobile AI agent system that enables seamless communication and task management between multiple devices using WiFi and Bluetooth protocols.

## Features

- Multi-device communication using WiFi and Bluetooth
- Real-time task management and monitoring
- Secure encrypted communication
- Device type detection (Desktop, Mobile, IoT)
- Modern GUI interface
- Background service mode
- LLM-powered task analysis
- Memory system for task persistence

## System Requirements

- Python 3.8 or higher
- Operating System: Windows, Linux, or macOS
- Network connectivity (for WiFi communication)
- Bluetooth capability (for Bluetooth communication)

## Installation

### Option 1: Using the Distribution Package (Recommended)

1. Download the `GrootiQ_Agent_Setup.zip` from the releases page
2. Extract the zip file to your desired location
3. Run `Run_GrootiQ_Agent.bat` or `GrootiQ_Agent.exe` to start the application

### Option 2: Manual Installation

#### Central Device (Control Center)

1. Clone the repository:
   ```bash
   git clone https://github.com/Groot-iQ/Symbiote-codebase.git
   cd mobile-ai-agent
   ```

2. Run the installation script:
   ```bash
   python install.py
   ```

3. Start the GUI:
   ```bash
   python -m gui
   ```

### Client Devices

1. Copy the project files to the client device

2. Run the installation script:
   ```bash
   python install.py
   ```

3. Start the agent service:
   ```bash
   python -m agent.service
   ```

## Building from Source

If you want to build the application from source:

1. Install the required build tools:
   ```bash
   pip install pyinstaller
   ```

2. Place your logo image as `assets/logo.png`

3. Run the setup script:
   ```bash
   python setup.py
   ```

4. The distribution package will be created as `GrootiQ_Agent_Setup.zip`

## Usage Guide

### Central Device (Control Center)

1. **Starting the System**
   - Launch the GUI using `python -m gui`
   - The dashboard will show system status and connected devices

2. **Managing Devices**
   - Go to the Devices tab
   - Click "Scan for Devices" to discover nearby agents
   - Select a device and click "Connect" to establish connection

3. **Task Management**
   - Go to the Tasks tab
   - Enter task description in the input field
   - Click "Add Task" to assign tasks to connected devices
   - Monitor task progress in the dashboard

4. **System Configuration**
   - Go to the Settings tab
   - Select preferred communication protocol (WiFi/Bluetooth)
   - Set security level (Low/Medium/High)
   - Click "Save Settings" to apply changes

### Client Devices

1. **Service Mode**
   - Run `python -m agent.service` to start the agent in background mode
   - The service will automatically:
     - Detect device type
     - Generate unique agent ID
     - Start communication services
     - Log activities to `agent.log`

2. **Monitoring**
   - Check `agent.log` for service status and activities
   - The service will automatically connect to the central device when available

## Connection Methods

### WiFi Connection
- Devices must be on the same network
- Default port: 8000
- Automatic device discovery
- Encrypted communication

### Bluetooth Connection
- Devices must be within Bluetooth range
- Default port: 8001
- Manual device pairing
- Secure data transfer

## Security Features

- End-to-end encryption
- Configurable security levels
- Secure device authentication
- Protected task execution

## Troubleshooting

### Common Issues

1. **Devices Not Connecting**
   - Check network connectivity
   - Verify Bluetooth is enabled
   - Ensure ports 8000 and 8001 are open
   - Check firewall settings

2. **Service Not Starting**
   - Verify Python version (3.8+ required)
   - Check all dependencies are installed
   - Review `agent.log` for error messages

3. **Connection Drops**
   - Check network stability
   - Verify device proximity for Bluetooth
   - Review security settings

### Logs and Debugging

- Central device: Check GUI log viewer
- Client devices: Review `agent.log`
- Service logs: Located in project directory

## Support

For technical support or inquiries, please contact:
- Email: adityajaiswal17ten@gmail.com
- Company: GrootiQ

## License

This software is proprietary and confidential. All rights reserved.

Copyright (c) 2024 GrootiQ

Unauthorized copying, distribution, or use of this software, via any medium, is strictly prohibited. 
