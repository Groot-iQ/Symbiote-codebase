import os
import sys
import subprocess
import platform

def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def install_requirements():
    """Install required packages."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Successfully installed requirements")
    except subprocess.CalledProcessError:
        print("Error installing requirements")
        sys.exit(1)

def setup_environment():
    """Set up environment variables."""
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write(f"AGENT_ID={platform.node()}\n")  # Use computer name as agent ID
            f.write("SECURITY_LEVEL=high\n")
            f.write("PROTOCOLS=wifi,bluetooth\n")
            f.write("WIFI_PORT=8000\n")
            f.write("BLUETOOTH_PORT=8001\n")
            f.write("MAX_CONNECTIONS=10\n")
    print("Environment file created")

def main():
    """Main installation function."""
    print("Starting installation...")
    
    # Check Python version
    check_python()
    print("Python version check passed")
    
    # Install requirements
    print("Installing requirements...")
    install_requirements()
    
    # Set up environment
    print("Setting up environment...")
    setup_environment()
    
    print("\nInstallation complete!")
    print("\nTo start the agent:")
    print("1. As GUI: python -m gui")
    print("2. As service: python -m agent.service")

if __name__ == "__main__":
    main() 