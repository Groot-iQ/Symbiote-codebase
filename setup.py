import os
import sys
import shutil
from setuptools import setup
import PyInstaller.__main__
from PIL import Image

def convert_to_ico(png_path):
    """Convert PNG to ICO format."""
    try:
        img = Image.open(png_path)
        ico_path = png_path.replace('.png', '.ico')
        img.save(ico_path, format='ICO')
        return ico_path
    except Exception as e:
        print(f"Warning: Could not convert logo to ICO format: {e}")
        return None

def create_executable():
    """Create executable using PyInstaller."""
    # Get the absolute path to the logo and convert it
    logo_path = os.path.abspath("assets/logo.png")
    ico_path = convert_to_ico(logo_path)
    
    # PyInstaller arguments
    args = [
        'gui/__main__.py',  # Main script
        '--name=GrootiQ_Agent',  # Name of the executable
        '--onefile',  # Create a single executable
        '--windowed',  # Don't show console window
        '--add-data=assets;assets',  # Include assets folder
        '--add-data=config;config',  # Include config folder
        '--add-data=agent;agent',  # Include agent folder
        '--add-data=utils;utils',  # Include utils folder
        '--add-data=requirements.txt;.',  # Include requirements
        '--add-data=LICENSE;.',  # Include license
        '--add-data=README.md;.',  # Include README
        '--hidden-import=PySide6',
        '--hidden-import=bluetooth',
        '--hidden-import=websockets',
        '--hidden-import=groq',
        '--hidden-import=python-dotenv',
        '--hidden-import=psutil',
        '--hidden-import=pycryptodome',
        '--clean',  # Clean PyInstaller cache
        '--noconfirm',  # Replace existing build
        '--add-binary=venv/Lib/site-packages/PySide6/Qt6Core.dll;PySide6',
        '--add-binary=venv/Lib/site-packages/PySide6/Qt6Gui.dll;PySide6',
        '--add-binary=venv/Lib/site-packages/PySide6/Qt6Widgets.dll;PySide6',
        '--add-binary=venv/Lib/site-packages/PySide6/Qt6Network.dll;PySide6',
        '--add-binary=venv/Lib/site-packages/PySide6/Qt6Qml.dll;PySide6',
    ]
    
    # Add icon if conversion was successful
    if ico_path:
        args.append(f'--icon={ico_path}')
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(args)
    except Exception as e:
        print(f"Error creating executable: {e}")
        sys.exit(1)

def create_simple_installer():
    """Create a simple installer by copying files to a distribution folder."""
    try:
        dist_dir = "dist/GrootiQ_Agent"
        os.makedirs(dist_dir, exist_ok=True)
        
        # Copy executable
        shutil.copy("dist/GrootiQ_Agent.exe", dist_dir)
        
        # Copy additional files
        shutil.copytree("assets", os.path.join(dist_dir, "assets"), dirs_exist_ok=True)
        shutil.copytree("config", os.path.join(dist_dir, "config"), dirs_exist_ok=True)
        shutil.copytree("agent", os.path.join(dist_dir, "agent"), dirs_exist_ok=True)
        shutil.copytree("utils", os.path.join(dist_dir, "utils"), dirs_exist_ok=True)
        
        # Copy documentation
        shutil.copy("LICENSE", dist_dir)
        shutil.copy("README.md", dist_dir)
        
        # Create a simple batch file to run the application
        with open(os.path.join(dist_dir, "Run_GrootiQ_Agent.bat"), "w") as f:
            f.write('@echo off\n')
            f.write('start "" "GrootiQ_Agent.exe"\n')
        
        # Create a zip file
        shutil.make_archive("GrootiQ_Agent_Setup", "zip", "dist", "GrootiQ_Agent")
    except Exception as e:
        print(f"Error creating distribution package: {e}")
        sys.exit(1)

def main():
    """Main setup function."""
    # Create executable
    print("Creating executable...")
    create_executable()
    
    # Create simple installer
    print("Creating distribution package...")
    create_simple_installer()
    
    print("\nSetup complete!")
    print("1. Executable created as 'dist/GrootiQ_Agent.exe'")
    print("2. Distribution package created as 'GrootiQ_Agent_Setup.zip'")
    print("\nTo install:")
    print("1. Extract GrootiQ_Agent_Setup.zip")
    print("2. Run Run_GrootiQ_Agent.bat or GrootiQ_Agent.exe")

if __name__ == "__main__":
    main() 