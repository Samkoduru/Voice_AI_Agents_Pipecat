#!/usr/bin/env python3
"""
VoiceFlow - AI-Powered Voice Assistant
Main entry point for the VoiceFlow application.

Author: Sam K
License: BSD 2-Clause License
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.voiceflow_server import main

if __name__ == "__main__":
    main() 