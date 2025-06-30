"""
VoiceFlow - Core Voice Assistant Logic
Handles real-time voice conversations with AI-powered responses.

Author: Sam K
License: BSD 2-Clause License
"""

import datetime
import io
import os
import sys
import wave

import aiofiles
from dotenv import load_dotenv
from fastapi import WebSocket
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def save_audio(server_name: str, audio: bytes, sample_rate: int, num_channels: int):
    """Save audio recording to WAV file with timestamp."""
    if len(audio) > 0:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{server_name}_recording_{timestamp}.wav"
        
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


async def run_voice_assistant(websocket_client: WebSocket, stream_sid: str, call_sid: str, testing: bool):
    """Main voice assistant function that handles the AI conversation pipeline."""
    
    # Initialize Twilio serializer
    serializer = TwilioFrameSerializer(
        stream_sid=stream_sid,
        call_sid=call_sid,
        account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
    )

    # Set up WebSocket transport
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=serializer,
        ),
    )

    # Initialize AI services
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"), audio_passthrough=True)
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady
        push_silence_after_stop=testing,
    )

    # Define the AI personality
    system_messages = [
        {
            "role": "system",
            "content": "You are an elementary teacher in an audio call. Your output will be converted to audio so don't include special characters in your answers. Respond to what the student said in a short short sentence.",
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
            transport.input(),      # WebSocket input from client
            stt,                    # Speech-to-Text conversion
            context_aggregator.user(),
            llm,                    # AI language model
            tts,                    # Text-to-Speech conversion
            transport.output(),     # WebSocket output to client
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
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        """Handle new client connection."""
        await audiobuffer.start_recording()
        # Start the conversation
        system_messages.append({"role": "system", "content": "Please introduce yourself to the user."})
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        """Handle client disconnection."""
        await task.cancel()

    @audiobuffer.event_handler("on_audio_data")
    async def on_audio_data(buffer, audio, sample_rate, num_channels):
        """Handle audio data for recording."""
        server_name = f"voiceflow_server_{websocket_client.client.port}"
        await save_audio(server_name, audio, sample_rate, num_channels)

    # Initialize and run the pipeline
    # Note: handle_sigint=False because uvicorn handles keyboard interrupts
    # force_gc=True helps with memory management for long-running applications
    runner = PipelineRunner(handle_sigint=False, force_gc=True)
    await runner.run(task)
