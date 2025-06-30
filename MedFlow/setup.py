#!/usr/bin/env python3
"""
Setup script for MedFlow Patient Intake Assistant
This script helps users quickly configure the project with their API keys and settings.
"""

import os
import sys
import shutil
from pathlib import Path


def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🏥 MedFlow Patient Intake Assistant Setup")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 10):
        print("❌ Error: Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print("✅ Python version check passed")


def create_env_file():
    """Create .env file from template"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("   Skipping .env file creation")
            return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("   Please edit .env file with your API keys")
    else:
        print("❌ Error: env.example file not found")


def check_dependencies():
    """Check if required dependencies are available"""
    print("\n📋 Checking dependencies...")
    
    # Check if requirements.txt exists
    if Path("requirements.txt").exists():
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found")
    
    # Check if Dockerfile exists
    if Path("Dockerfile").exists():
        print("✅ Dockerfile found")
    else:
        print("❌ Dockerfile not found")
    
    # Check if assets directory exists
    if Path("assets").exists():
        print("✅ assets directory found")
    else:
        print("❌ assets directory not found")


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("1. Edit .env file with your API keys:")
    print("   - DAILY_SAMPLE_ROOM_URL (optional, for development)")
    print("   - DAILY_API_KEY")
    print("   - OPENAI_API_KEY")
    print("   - CARTESIA_API_KEY")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Run the server:")
    print("   python server.py")
    print("\n4. Visit http://localhost:7860/ to start a patient intake session")
    print("\n📚 For detailed instructions, see README.md")
    print("\n🐳 For Docker deployment:")
    print("   docker build -t medflow-intake .")
    print("   docker run --env-file .env -p 7860:7860 medflow-intake")


def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Create necessary files
    print("\n📁 Creating configuration files...")
    create_env_file()
    
    # Check dependencies
    check_dependencies()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main() 