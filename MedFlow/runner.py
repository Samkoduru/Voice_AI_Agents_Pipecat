"""
MedFlow: AI-Powered Patient Intake Assistant - Runner Configuration
Handles Daily.co room configuration and token generation for patient intake sessions.

Author: Sam K
License: BSD 2-Clause License
"""

import argparse
import os

import aiohttp

from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper


async def configure(aiohttp_session: aiohttp.ClientSession):
    """Configure Daily.co room and generate authentication token."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MedFlow Patient Intake Configuration")
    parser.add_argument(
        "-u", "--url", 
        type=str, 
        required=False, 
        help="Daily.co room URL for the intake session"
    )
    parser.add_argument(
        "-k", "--apikey",
        type=str, 
        required=False, 
        help="Daily.co API Key for room authentication"
    )

    args, unknown = parser.parse_known_args()

    # Get configuration from arguments or environment variables
    url = args.url or os.getenv("DAILY_SAMPLE_ROOM_URL")
    key = args.apikey or os.getenv("DAILY_API_KEY")

    # Validate required configuration
    if not url:
        raise Exception(
            "No Daily.co room URL specified. Use the -u/--url option from the command line, "
            "or set DAILY_SAMPLE_ROOM_URL in your environment to specify a Daily.co room URL."
        )

    if not key:
        raise Exception(
            "No Daily.co API key specified. Use the -k/--apikey option from the command line, "
            "or set DAILY_API_KEY in your environment. Get your API key from "
            "https://dashboard.daily.co/developers."
        )

    # Initialize Daily.co REST helper
    daily_rest_helper = DailyRESTHelper(
        daily_api_key=key,
        daily_api_url=os.getenv("DAILY_API_URL", "https://api.daily.co/v1"),
        aiohttp_session=aiohttp_session,
    )

    # Generate authentication token with 1-hour expiration
    expiry_time: float = 60 * 60  # 1 hour in seconds
    token = await daily_rest_helper.get_token(url, expiry_time)

    return (url, token)
