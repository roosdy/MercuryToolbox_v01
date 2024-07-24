import subprocess
import sys
import os

def create_virtual_environment():
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    print("Virtual environment created.")

def install_requirements():
    venv_python = os.path.join("venv", "Scripts", "python") if os.name == 'nt' else os.path.join("venv", "bin", "python")
    
    requirements = [
        'customtkinter',
        'markdown',
        'python-dotenv',
        'pystray',
        'pillow'  # Required by pystray for image handling
    ]
    
    for package in requirements:
        subprocess.check_call([venv_python, "-m", "pip", "install", package])
        print(f"Installed {package}")

def verify_tkinter():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        print("tkinter is installed and working.")
    except ImportError:
        print("tkinter is not installed. Please install it using your system's package manager.")

if __name__ == "__main__":
    create_virtual_environment()
    install_requirements()
    verify_tkinter()
    print("Project setup complete!")
