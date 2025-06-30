#!/usr/bin/env python3
"""
VoiceFlow Setup Script
This script helps users quickly configure the VoiceFlow project with their API keys and settings.
"""

import os
import sys
import shutil
from pathlib import Path


def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🚀 VoiceFlow AI Assistant Setup")
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


def create_streams_xml():
    """Create streams.xml from template"""
    template_file = Path("src/config/templates/streams.xml.template")
    streams_file = Path("src/config/templates/streams.xml")
    
    if streams_file.exists():
        print("⚠️  src/config/templates/streams.xml already exists")
        response = input("   Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("   Skipping streams.xml creation")
            return
    
    if template_file.exists():
        shutil.copy(template_file, streams_file)
        print("✅ Created src/config/templates/streams.xml from template")
        print("   Please update the WebSocket URL with your ngrok domain")
    else:
        print("❌ Error: src/config/templates/streams.xml.template not found")


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


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 VoiceFlow Setup Complete!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OPENAI_API_KEY")
    print("   - DEEPGRAM_API_KEY") 
    print("   - CARTESIA_API_KEY")
    print("   - TWILIO_ACCOUNT_SID")
    print("   - TWILIO_AUTH_TOKEN")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Set up ngrok tunnel:")
    print("   ngrok http 8765")
    print("\n4. Update src/config/templates/streams.xml with your ngrok URL")
    print("\n5. Configure Twilio webhook URL")
    print("\n6. Run the VoiceFlow server:")
    print("   python voiceflow.py")
    print("\n📚 For detailed instructions, see README.md")
    print("\n🧪 For testing without phone calls:")
    print("   - Python client: cd web-clients/python && python client.py -u http://localhost:8765")
    print("   - TypeScript client: cd web-clients/typescript && npm install && npm run dev")


def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Create necessary files
    print("\n📁 Creating configuration files...")
    create_env_file()
    create_streams_xml()
    
    # Check dependencies
    check_dependencies()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main() 