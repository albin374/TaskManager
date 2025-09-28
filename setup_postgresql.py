#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for TaskManager
This script helps set up the PostgreSQL database for the TaskManager application.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible."""
    print("🔍 Checking PostgreSQL connection...")
    
    # Check if psql is available
    if not run_command("psql --version", "Checking psql availability"):
        print("❌ PostgreSQL client (psql) not found. Please install PostgreSQL client tools.")
        return False
    
    # Try to connect to PostgreSQL
    db_name = os.getenv('DB_NAME', 'taskapp')
    db_user = os.getenv('DB_USER', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    connection_test = f"psql -h {db_host} -p {db_port} -U {db_user} -d postgres -c 'SELECT version();'"
    
    if run_command(connection_test, "Testing PostgreSQL connection"):
        print("✅ PostgreSQL connection successful")
        return True
    else:
        print("❌ Cannot connect to PostgreSQL. Please check:")
        print("   - PostgreSQL server is running")
        print("   - Database credentials are correct")
        print("   - Database host and port are accessible")
        return False

def create_database():
    """Create the database if it doesn't exist."""
    print("🗄️ Creating database...")
    
    db_name = os.getenv('DB_NAME', 'taskapp')
    db_user = os.getenv('DB_USER', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    # Check if database exists
    check_db = f"psql -h {db_host} -p {db_port} -U {db_user} -d postgres -c \"SELECT 1 FROM pg_database WHERE datname='{db_name}';\""
    
    try:
        result = subprocess.run(check_db, shell=True, capture_output=True, text=True)
        if db_name in result.stdout:
            print(f"✅ Database '{db_name}' already exists")
            return True
    except:
        pass
    
    # Create database
    create_db = f"psql -h {db_host} -p {db_port} -U {db_user} -d postgres -c \"CREATE DATABASE {db_name};\""
    
    if run_command(create_db, f"Creating database '{db_name}'"):
        print(f"✅ Database '{db_name}' created successfully")
        return True
    else:
        print(f"❌ Failed to create database '{db_name}'")
        return False

def run_migrations():
    """Run Django migrations."""
    print("🔄 Running Django migrations...")
    
    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        return False
    
    # Run migrations
    if not run_command("python manage.py migrate", "Applying migrations"):
        return False
    
    print("✅ Database migrations completed successfully")
    return True

def create_superuser():
    """Create a superuser account."""
    print("👤 Creating superuser account...")
    
    # Check if superuser already exists
    check_superuser = "python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')\""
    
    try:
        result = subprocess.run(check_superuser, shell=True, capture_output=True, text=True)
        if "Superuser exists" in result.stdout:
            print("✅ Superuser already exists")
            return True
    except:
        pass
    
    # Create superuser interactively
    print("📝 Please create a superuser account:")
    create_superuser_cmd = "python manage.py createsuperuser"
    
    try:
        subprocess.run(create_superuser_cmd, shell=True, check=True)
        print("✅ Superuser created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create superuser")
        return False

def load_sample_data():
    """Load sample data if available."""
    print("📊 Loading sample data...")
    
    # Check if there's a management command for loading sample data
    sample_data_commands = [
        "python manage.py loaddata sample_data.json",
        "python manage.py load_sample_data",
    ]
    
    for cmd in sample_data_commands:
        if run_command(cmd, f"Trying: {cmd}"):
            print("✅ Sample data loaded successfully")
            return True
    
    print("ℹ️ No sample data found or loaded")
    return True

def main():
    """Main setup function."""
    print("🚀 TaskManager PostgreSQL Database Setup")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Step 1: Check PostgreSQL connection
    if not check_postgresql_connection():
        print("\n❌ Setup failed: Cannot connect to PostgreSQL")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure PostgreSQL is installed and running")
        print("   2. Check your .env file for correct database credentials")
        print("   3. Verify PostgreSQL is accessible on the specified host/port")
        sys.exit(1)
    
    # Step 2: Create database
    if not create_database():
        print("\n❌ Setup failed: Cannot create database")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_migrations():
        print("\n❌ Setup failed: Database migrations failed")
        sys.exit(1)
    
    # Step 4: Create superuser
    if not create_superuser():
        print("\n❌ Setup failed: Cannot create superuser")
        sys.exit(1)
    
    # Step 5: Load sample data
    load_sample_data()
    
    print("\n🎉 PostgreSQL database setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Start the Django development server: python manage.py runserver")
    print("   2. Access the admin panel at: http://localhost:8000/admin/")
    print("   3. Start the frontend: cd frontend && npm start")
    print("\n🔗 Useful commands:")
    print("   - View database: psql -h localhost -U postgres -d taskmanager")
    print("   - Run migrations: python manage.py migrate")
    print("   - Create superuser: python manage.py createsuperuser")

if __name__ == "__main__":
    main()
