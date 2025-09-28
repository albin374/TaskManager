#!/usr/bin/env python
"""
Setup script for TaskManager Pro
"""

import os
import sys
import subprocess

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return None

def setup_backend():
    """Setup Django backend"""
    print("Setting up Django backend...")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Run migrations
    print("Running database migrations...")
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")
    
    # Create superuser (optional)
    print("Creating superuser...")
    print("Please run 'python manage.py createsuperuser' manually to create an admin user.")
    
    print("Backend setup complete!")

def setup_frontend():
    """Setup React frontend"""
    print("Setting up React frontend...")
    
    # Change to frontend directory
    os.chdir('frontend')
    
    # Install Node dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install")
    
    # Change back to root directory
    os.chdir('..')
    
    print("Frontend setup complete!")

def main():
    """Main setup function"""
    print("TaskManager Pro Setup")
    print("====================")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup backend
    setup_backend()
    
    # Setup frontend
    if os.path.exists('frontend'):
        setup_frontend()
    else:
        print("Frontend directory not found. Skipping frontend setup.")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Copy env.example to .env and configure your settings")
    print("2. Start PostgreSQL and Redis services")
    print("3. Run 'python manage.py runserver' to start the backend")
    print("4. Run 'cd frontend && npm start' to start the frontend")
    print("5. Visit http://localhost:3000 to access the application")

if __name__ == "__main__":
    main()



