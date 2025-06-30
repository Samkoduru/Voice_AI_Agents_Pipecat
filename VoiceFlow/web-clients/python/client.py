"""
VoiceFlow - Python Test Client
Automated testing client for the VoiceFlow AI Assistant server.

Author: Sam K
License: BSD 2-Clause License
"""

import argparse
import asyncio
import datetime
import io
import os
import sys
import wave
import xml.etree.ElementTree as ET
from uuid import uuid4

import aiofiles
import aiohttp
from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import EndFrame, TransportMessageUrgentFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.network.websocket_client import (
    WebsocketClientParams,
    WebsocketClientTransport,
)

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# Default client session duration
DEFAULT_CLIENT_DURATION = 30


async def download_twiml(server_url: str) -> str:
    """Download TwiML configuration from server."""
    # TODO: Add proper error handling
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url) as response:
            return await response.text()


def get_stream_url_from_twiml(twiml: str) -> str:
    """Extract WebSocket stream URL from TwiML response."""
    root = ET.fromstring(twiml)
    # TODO: Add proper error handling
    stream_element = root.find(".//Stream")  # Find the first <Stream> element
    url = stream_element.get("url")
    return url


async def save_audio(client_name: str, audio: bytes, sample_rate: int, num_channels: int):
    """Save audio recording to WAV file with timestamp."""
    if len(audio) > 0:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{client_name}_recording_{timestamp}.wav"
        
        with io.BytesIO() as buffer:
            with wave.open(buffer, "wb") as wf:
                wf.setsampwidth(2)
                wf.setnchannels(num_channels)
                wf.setframerate(sample_rate)
                wf.writeframes(audio)
            async with aiofiles.open(filename, "wb") as file:
                await file.write(buffer.getvalue())
        logger.info(f"Audio recording saved: {filename}")
    else:
        logger.info("No audio data to save")


async def run_client(client_name: str, server_url: str, duration_secs: int):
    """Run a single test client session."""
    
    # Get TwiML configuration
    twiml = await download_twiml(server_url)
    stream_url = get_stream_url_from_twiml(twiml)

    # Generate unique session IDs
    stream_sid = str(uuid4())
    call_sid = str(uuid4())

    # Set up WebSocket transport
    transport = WebsocketClientTransport(
        uri=stream_url,
        params=WebsocketClientParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            serializer=TwilioFrameSerializer(stream_sid=stream_sid, call_sid=call_sid),
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=1.0)),
        ),
    )

    # Initialize AI services
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="e13cae5c-ec59-4f71-b0a6-266df3c9bb8e",  # Madame Mischief
        push_silence_after_stop=True,
    )

    # Define the client personality (8-year-old child)
    system_messages = [
        {
            "role": "system",
            "content": "You are an 8 year old child. A teacher will explain you new concepts you want to know about. Feel free to change topics whenever you want. Once you are taught something you need to keep asking for clarifications if you think someone your age would not understand what you are being taught.",
        },
    ]

    # Set up conversation context
    context = OpenAILLMContext(system_messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Audio buffer for recording conversations
    # Note: This stores all conversation in memory. Consider using buffer_size for periodic callbacks.
    audiobuffer = AudioBufferProcessor()

    # Build the audio processing pipeline
    pipeline = Pipeline(
        [
            transport.input(),      # WebSocket input from server
            stt,                    # Speech-to-Text conversion
            context_aggregator.user(),
            llm,                    # AI language model
            tts,                    # Text-to-Speech conversion
            transport.output(),     # WebSocket output to server
            audiobuffer,            # Audio recording buffer
            context_aggregator.assistant(),
        ]
    )

    # Configure pipeline task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    # Event handlers
    @transport.event_handler("on_connected")
    async def on_connected(transport: WebsocketClientTransport, client):
        """Handle successful connection to server."""
        await audiobuffer.start_recording()

        # Send connection message
        connection_msg = TransportMessageUrgentFrame(
            message={"event": "connected", "protocol": "Call", "version": "1.0.0"}
        )
        await transport.output().send_message(connection_msg)

        # Send start message
        start_msg = TransportMessageUrgentFrame(
            message={
                "event": "start",
                "streamSid": stream_sid,
                "callSid": call_sid,
                "start": {"streamSid": stream_sid, "callSid": call_sid},
            }
        )
        await transport.output().send_message(start_msg)

    @audiobuffer.event_handler("on_audio_data")
    async def on_audio_data(buffer, audio, sample_rate, num_channels):
        """Handle audio data for recording."""
        await save_audio(client_name, audio, sample_rate, num_channels)

    async def end_call():
        """End the call after specified duration."""
        await asyncio.sleep(duration_secs)
        logger.info(f"Client {client_name} finished after {duration_secs} seconds.")
        await task.queue_frame(EndFrame())

    # Run the pipeline and end call timer concurrently
    runner = PipelineRunner()
    await asyncio.gather(runner.run(task), end_call())


async def main():
    """Main function to run multiple test clients."""
    parser = argparse.ArgumentParser(description="VoiceFlow AI Assistant Test Client")
    parser.add_argument("-u", "--url", type=str, required=True, help="Server URL")
    parser.add_argument(
        "-c", "--clients", type=int, required=True, help="Number of concurrent clients"
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=DEFAULT_CLIENT_DURATION,
        help=f"Duration of each client session in seconds (default: {DEFAULT_CLIENT_DURATION})",
    )
    args, _ = parser.parse_known_args()

    # Create and run multiple client tasks
    client_tasks = []
    for i in range(args.clients):
        task = asyncio.create_task(
            run_client(f"voiceflow_client_{i}", args.url, args.duration)
        )
        client_tasks.append(task)
    
    await asyncio.gather(*client_tasks)


if __name__ == "__main__":
    asyncio.run(main()) 