"""
VoiceFlow - FastAPI Server
Main server application that handles Twilio webhooks and WebSocket connections.

Author: Sam K
License: BSD 2-Clause License
"""

import argparse
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import uvicorn
from core.voice_assistant import run_voice_assistant
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

# Initialize FastAPI application
app = FastAPI(title="VoiceFlow AI Assistant", version="1.0.0")

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
async def start_call():
    """Handle Twilio webhook for incoming calls."""
    print("Received TwiML request")
    return HTMLResponse(
        content=open("src/config/templates/streams.xml").read(), 
        media_type="application/xml"
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time audio streaming."""
    await websocket.accept()
    
    # Process initial connection messages
    start_data = websocket.iter_text()
    await start_data.__anext__()  # Skip first message
    
    # Parse call data from second message
    call_data = json.loads(await start_data.__anext__())
    print(f"Call data received: {call_data}", flush=True)
    
    # Extract stream and call IDs
    stream_sid = call_data["start"]["streamSid"]
    call_sid = call_data["start"]["callSid"]
    
    print("WebSocket connection established")
    await run_voice_assistant(websocket, stream_sid, call_sid, app.state.testing)


def main():
    """Main function to start the VoiceFlow server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="VoiceFlow AI Assistant Server")
    parser.add_argument(
        "-t", "--test", 
        action="store_true", 
        default=False, 
        help="Enable testing mode"
    )
    args, _ = parser.parse_known_args()

    # Store testing mode in app state
    app.state.testing = args.test

    # Start the server
    print(f"Starting VoiceFlow AI Assistant server on port 8765 (test mode: {args.test})")
    uvicorn.run(app, host="0.0.0.0", port=8765)


if __name__ == "__main__":
    main()
