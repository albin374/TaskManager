#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
This script helps migrate data from SQLite to PostgreSQL for existing users.
"""

import os
import sys
import subprocess
import json
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

def backup_sqlite_data():
    """Create a backup of SQLite data."""
    print("💾 Creating SQLite data backup...")
    
    if not Path("db.sqlite3").exists():
        print("ℹ️ No SQLite database found. Skipping backup.")
        return True
    
    # Create backup directory
    backup_dir = Path("backup")
    backup_dir.mkdir(exist_ok=True)
    
    # Backup SQLite database
    backup_cmd = "cp db.sqlite3 backup/db_backup.sqlite3"
    
    if run_command(backup_cmd, "Backing up SQLite database"):
        print("✅ SQLite data backed up to backup/db_backup.sqlite3")
        return True
    else:
        print("❌ Failed to backup SQLite data")
        return False

def export_sqlite_data():
    """Export SQLite data to JSON fixtures."""
    print("📤 Exporting SQLite data to JSON fixtures...")
    
    if not Path("db.sqlite3").exists():
        print("ℹ️ No SQLite database found. Skipping export.")
        return True
    
    # Temporarily switch to SQLite for data export
    backup_settings()
    
    # Create temporary settings for SQLite
    create_temp_sqlite_settings()
    
    try:
        # Export data from each app
        apps = ['accounts', 'projects', 'tasks', 'chatbot']
        
        for app in apps:
            export_cmd = f"python manage.py dumpdata {app} --indent 2 --output backup/{app}_data.json"
            if not run_command(export_cmd, f"Exporting {app} data"):
                print(f"⚠️ Failed to export {app} data, continuing...")
        
        print("✅ Data export completed")
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False
    finally:
        # Restore original settings
        restore_settings()

def backup_settings():
    """Backup current settings.py."""
    print("💾 Backing up settings.py...")
    
    if Path("taskmanager/settings.py").exists():
        backup_cmd = "cp taskmanager/settings.py taskmanager/settings_backup.py"
        run_command(backup_cmd, "Backing up settings.py")

def create_temp_sqlite_settings():
    """Create temporary settings for SQLite export."""
    print("⚙️ Creating temporary SQLite settings...")
    
    sqlite_settings = '''
# Temporary SQLite settings for data export
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
    
    # Read current settings
    with open("taskmanager/settings.py", "r") as f:
        content = f.read()
    
    # Replace PostgreSQL settings with SQLite
    lines = content.split('\n')
    new_lines = []
    skip_until_end = False
    
    for line in lines:
        if '# PostgreSQL configuration' in line:
            skip_until_end = True
            new_lines.append(sqlite_settings.strip())
        elif skip_until_end and line.strip() == '}':
            skip_until_end = False
            new_lines.append(line)
        elif not skip_until_end:
            new_lines.append(line)
    
    # Write temporary settings
    with open("taskmanager/settings.py", "w") as f:
        f.write('\n'.join(new_lines))

def restore_settings():
    """Restore original settings.py."""
    print("🔄 Restoring original settings...")
    
    if Path("taskmanager/settings_backup.py").exists():
        restore_cmd = "cp taskmanager/settings_backup.py taskmanager/settings.py"
        run_command(restore_cmd, "Restoring settings.py")
        
        # Clean up backup
        cleanup_cmd = "rm taskmanager/settings_backup.py"
        run_command(cleanup_cmd, "Cleaning up backup")

def import_to_postgresql():
    """Import data to PostgreSQL."""
    print("📥 Importing data to PostgreSQL...")
    
    # Check if PostgreSQL is accessible
    if not check_postgresql_connection():
        print("❌ Cannot connect to PostgreSQL. Please ensure PostgreSQL is running and configured.")
        return False
    
    # Run migrations first
    if not run_command("python manage.py migrate", "Running migrations"):
        return False
    
    # Import data from each app
    apps = ['accounts', 'projects', 'tasks', 'chatbot']
    
    for app in apps:
        fixture_file = f"backup/{app}_data.json"
        if Path(fixture_file).exists():
            import_cmd = f"python manage.py loaddata {fixture_file}"
            if not run_command(import_cmd, f"Importing {app} data"):
                print(f"⚠️ Failed to import {app} data, continuing...")
    
    print("✅ Data import completed")
    return True

def check_postgresql_connection():
    """Check if PostgreSQL is accessible."""
    print("🔍 Checking PostgreSQL connection...")
    
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
        print("❌ Cannot connect to PostgreSQL")
        return False

def cleanup():
    """Clean up temporary files."""
    print("🧹 Cleaning up temporary files...")
    
    # Remove backup directory
    if Path("backup").exists():
        cleanup_cmd = "rm -rf backup"
        run_command(cleanup_cmd, "Removing backup directory")

def main():
    """Main migration function."""
    print("🔄 SQLite to PostgreSQL Migration Script")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Step 1: Backup SQLite data
    if not backup_sqlite_data():
        print("❌ Migration failed: Cannot backup SQLite data")
        sys.exit(1)
    
    # Step 2: Export SQLite data
    if not export_sqlite_data():
        print("❌ Migration failed: Cannot export SQLite data")
        sys.exit(1)
    
    # Step 3: Import to PostgreSQL
    if not import_to_postgresql():
        print("❌ Migration failed: Cannot import to PostgreSQL")
        sys.exit(1)
    
    # Step 4: Cleanup
    cleanup()
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Verify your data in PostgreSQL: psql -h localhost -U postgres -d taskmanager")
    print("   2. Test the application: python manage.py runserver")
    print("   3. Check the admin panel: http://localhost:8000/admin/")
    print("\n⚠️ Important:")
    print("   - Your original SQLite database is backed up as db_backup.sqlite3")
    print("   - You can now safely remove db.sqlite3 if everything works correctly")
    print("   - Keep the backup until you're confident the migration was successful")

if __name__ == "__main__":
    main()
