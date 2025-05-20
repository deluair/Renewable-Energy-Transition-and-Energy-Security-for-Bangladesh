"""
Script to initialize the Bangladesh Energy Transition simulation project structure.
"""

import os
import sys
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the project directory structure."""
    # Define directories to create
    directories = [
        'bangladesh_energy',
        'bangladesh_energy/models',
        'bangladesh_energy/utils',
        'bangladesh_energy/config',
        'bangladesh_energy/tests',
        'bangladesh_energy/data',
        'bangladesh_energy/analysis',
        'docs'
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files
    init_files = [
        'bangladesh_energy/__init__.py',
        'bangladesh_energy/models/__init__.py',
        'bangladesh_energy/utils/__init__.py',
        'bangladesh_energy/config/__init__.py',
        'bangladesh_energy/tests/__init__.py',
        'bangladesh_energy/analysis/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"Created file: {init_file}")

def create_virtual_environment():
    """Create a Python virtual environment."""
    try:
        import venv
        venv.create('venv', with_pip=True)
        print("Created virtual environment: venv")
    except Exception as e:
        print(f"Error creating virtual environment: {e}")

def install_dependencies():
    """Install project dependencies."""
    try:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Installed project dependencies")
    except Exception as e:
        print(f"Error installing dependencies: {e}")

def main():
    """Main function to initialize the project."""
    print("Initializing Bangladesh Energy Transition Simulation Project...")
    
    # Create directory structure
    create_directory_structure()
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    print("\nProject initialization complete!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    print("   - Windows: .\\venv\\Scripts\\activate")
    print("   - Unix/MacOS: source venv/bin/activate")
    print("2. Run the tests: python run_tests.py")
    print("3. Run the simulation: python -m bangladesh_energy.run_simulation")

if __name__ == '__main__':
    main() 