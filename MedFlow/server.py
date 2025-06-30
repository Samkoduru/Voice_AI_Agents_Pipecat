"""
MedFlow: AI-Powered Patient Intake Assistant - Server
FastAPI server for managing patient intake sessions and Daily.co room creation.

Author: Sam K
License: BSD 2-Clause License
"""

import argparse
import os
import subprocess
from contextlib import asynccontextmanager

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper, DailyRoomParams

# Load environment variables
load_dotenv(override=True)

# Configuration constants
MAX_BOTS_PER_ROOM = 1

# Global state management
bot_procs = {}
daily_helpers = {}


def cleanup():
    """Clean up function to terminate all running bot processes."""
    for entry in bot_procs.values():
        proc = entry[0]
        proc.terminate()
        proc.wait()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for resource initialization and cleanup."""
    # Initialize aiohttp session
    aiohttp_session = aiohttp.ClientSession()
    
    # Set up Daily.co REST helper
    daily_helpers["rest"] = DailyRESTHelper(
        daily_api_key=os.getenv("DAILY_API_KEY", ""),
        daily_api_url=os.getenv("DAILY_API_URL", "https://api.daily.co/v1"),
        aiohttp_session=aiohttp_session,
    )
    
    yield
    
    # Cleanup
    await aiohttp_session.close()
    cleanup()


# Initialize FastAPI application
app = FastAPI(
    title="MedFlow Patient Intake Server",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def start_agent(request: Request):
    """Create a new patient intake session and redirect to the room."""
    print("Creating new MedFlow intake session")
    
    # Create Daily.co room for the session
    room = await daily_helpers["rest"].create_room(DailyRoomParams())
    print(f"Room created: {room.url}")
    
    # Validate room creation
    if not room.url:
        raise HTTPException(
            status_code=500,
            detail="Failed to create room. Cannot start intake session without a valid room URL.",
        )

    # Check for existing bots in the room
    num_bots_in_room = sum(
        1 for proc in bot_procs.values() 
        if proc[1] == room.url and proc[0].poll() is None
    )
    
    if num_bots_in_room >= MAX_BOTS_PER_ROOM:
        raise HTTPException(
            status_code=500, 
            detail=f"Maximum bot limit reached for room: {room.url}"
        )

    # Get authentication token for the room
    token = await daily_helpers["rest"].get_token(room.url)

    if not token:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate authentication token for room: {room.url}"
        )

    # Spawn the MedFlow intake assistant process
    try:
        proc = subprocess.Popen(
            [f"python3 -m bot -u {room.url} -t {token}"],
            shell=True,
            bufsize=1,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        bot_procs[proc.pid] = (proc, room.url)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start MedFlow assistant: {e}"
        )

    return RedirectResponse(room.url)


@app.get("/status/{pid}")
def get_status(pid: int):
    """Get the status of a running MedFlow assistant process."""
    # Look up the subprocess
    proc = bot_procs.get(pid)

    # Check if process exists
    if not proc:
        raise HTTPException(
            status_code=404, 
            detail=f"MedFlow assistant with process ID {pid} not found"
        )

    # Determine process status
    if proc[0].poll() is None:
        status = "running"
    else:
        status = "finished"

    return JSONResponse({"bot_id": pid, "status": status})


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    default_host = os.getenv("HOST", "0.0.0.0")
    default_port = int(os.getenv("FAST_API_PORT", "7860"))

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MedFlow Patient Intake Server")
    parser.add_argument("--host", type=str, default=default_host, help="Host address")
    parser.add_argument("--port", type=int, default=default_port, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")

    config = parser.parse_args()
    
    print(f"MedFlow Patient Intake Server starting on http://localhost:{config.port}/")
    
    # Start the server
    uvicorn.run(
        "server:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
    )
