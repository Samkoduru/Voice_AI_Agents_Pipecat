"""
MedFlow: AI-Powered Patient Intake Assistant
Core bot logic for managing patient intake conversations and data collection.

Author: Sam K
License: BSD 2-Clause License
"""

import asyncio
import os
import sys
import wave

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from runner import configure

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import OutputAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContextFrame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.processors.logger import FrameLogger
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.llm_service import FunctionCallParams
from pipecat.services.openai.llm import OpenAILLMContext, OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# Audio feedback sounds for better user experience
sounds = {}
sound_files = [
    "clack-short.wav",
    "clack.wav",
    "clack-short-quiet.wav",
    "ding.wav",
    "ding2.wav",
]

# Load audio files for user feedback
script_dir = os.path.dirname(__file__)
for file in sound_files:
    full_path = os.path.join(script_dir, "assets", file)
    filename = os.path.splitext(os.path.basename(full_path))[0]
    with wave.open(full_path) as audio_file:
        sounds[file] = OutputAudioRawFrame(
            audio_file.readframes(-1), 
            audio_file.getframerate(), 
            audio_file.getnchannels()
        )


class IntakeProcessor:
    """Manages the patient intake conversation flow and data collection."""
    
    def __init__(self, context: OpenAILLMContext):
        """Initialize the intake processor with conversation context."""
        print("Initializing MedFlow intake processor")
        context.add_message(
            {
                "role": "system",
                "content": "You are Jessica, a professional medical intake assistant for MedFlow. Your role is to collect essential patient information before their doctor visit. You're speaking with Chad Bailey. Address the patient by their first name and maintain a polite, professional demeanor. You're not a medical professional, so avoid providing medical advice. Keep responses concise and focused on information collection. Don't make assumptions about patient data - ask for clarification if responses are unclear. Start by introducing yourself, then ask the patient to confirm their identity by providing their birthday including the year. When they respond, call the verify_birthday function.",
            }
        )
        context.set_tools(
            [
                {
                    "type": "function",
                    "function": {
                        "name": "verify_birthday",
                        "description": "Verify the patient's birthday to confirm their identity.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "birthday": {
                                    "type": "string",
                                    "description": "The patient's birthdate in YYYY-MM-DD format. Convert any provided format to this standard.",
                                }
                            },
                        },
                    },
                }
            ]
        )

    async def verify_birthday(self, params: FunctionCallParams):
        """Verify patient's birthday and proceed to next intake step."""
        if params.arguments["birthday"] == "1983-01-01":
            # Identity verified - proceed to prescription collection
            params.context.set_tools(
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "list_prescriptions",
                            "description": "Collect the patient's current prescription medications.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "prescriptions": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "medication": {
                                                    "type": "string",
                                                    "description": "The medication name",
                                                },
                                                "dosage": {
                                                    "type": "string",
                                                    "description": "The prescription dosage",
                                                },
                                            },
                                        },
                                    }
                                },
                            },
                        },
                    }
                ]
            )
            
            await params.result_callback(
                [
                    {
                        "role": "system",
                        "content": "Thank the patient for confirming their identity, then ask them to list their current prescriptions. Each prescription should include both the medication name and dosage. Only call the list_prescriptions function when you have complete information.",
                    }
                ]
            )
        else:
            # Incorrect birthday - ask for retry
            await params.result_callback(
                [
                    {
                        "role": "system",
                        "content": "The provided birthday is incorrect. Please ask the patient for their birthday again and call the verify_birthday function when they respond.",
                    }
                ]
            )

    async def list_prescriptions(self, params: FunctionCallParams):
        """Collect prescription information and proceed to allergies."""
        print("Processing prescription information")
        
        # Move to allergy collection
        params.context.set_tools(
            [
                {
                    "type": "function",
                    "function": {
                        "name": "list_allergies",
                        "description": "Collect the patient's allergy information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "allergies": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "What the patient is allergic to",
                                            }
                                        },
                                    },
                                }
                            },
                        },
                    },
                }
            ]
        )
        params.context.add_message(
            {
                "role": "system",
                "content": "Next, ask the patient about their allergies. Once they've provided their allergy information or confirmed they have none, call the list_allergies function.",
            }
        )
        
        await params.llm.queue_frame(
            OpenAILLMContextFrame(params.context), FrameDirection.DOWNSTREAM
        )
        await self.save_data(params.arguments, params.result_callback)

    async def list_allergies(self, params: FunctionCallParams):
        """Collect allergy information and proceed to medical conditions."""
        print("Processing allergy information")
        
        # Move to medical conditions
        params.context.set_tools(
            [
                {
                    "type": "function",
                    "function": {
                        "name": "list_conditions",
                        "description": "Collect the patient's medical conditions.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "conditions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "The patient's medical condition",
                                            }
                                        },
                                    },
                                }
                            },
                        },
                    },
                },
            ]
        )
        params.context.add_message(
            {
                "role": "system",
                "content": "Now ask the patient about any medical conditions the doctor should be aware of. Once they've answered, call the list_conditions function.",
            }
        )
        
        await params.llm.queue_frame(
            OpenAILLMContextFrame(params.context), FrameDirection.DOWNSTREAM
        )
        await self.save_data(params.arguments, params.result_callback)

    async def list_conditions(self, params: FunctionCallParams):
        """Collect medical conditions and proceed to visit reasons."""
        print("Processing medical conditions")
        
        # Move to visit reasons
        params.context.set_tools(
            [
                {
                    "type": "function",
                    "function": {
                        "name": "list_visit_reasons",
                        "description": "Collect the reason for the patient's doctor visit.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "visit_reasons": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "The patient's reason for visiting the doctor",
                                            }
                                        },
                                    },
                                }
                            },
                        },
                    },
                }
            ]
        )
        params.context.add_message(
            {
                "role": "system",
                "content": "Finally, ask the patient the reason for their doctor visit today. Once they answer, call the list_visit_reasons function.",
            }
        )
        
        await params.llm.queue_frame(
            OpenAILLMContextFrame(params.context), FrameDirection.DOWNSTREAM
        )
        await self.save_data(params.arguments, params.result_callback)

    async def list_visit_reasons(self, params: FunctionCallParams):
        """Collect visit reasons and conclude the intake process."""
        print("Processing visit reasons")
        
        # Conclude the intake process
        params.context.set_tools([])
        params.context.add_message(
            {"role": "system", "content": "Thank the patient for completing their intake and conclude the conversation professionally."}
        )
        
        await params.llm.queue_frame(
            OpenAILLMContextFrame(params.context), FrameDirection.DOWNSTREAM
        )
        await self.save_data(params.arguments, params.result_callback)

    async def save_data(self, args, result_callback):
        """Save collected patient data for medical professionals."""
        logger.info(f"Saving patient intake data: {args}")
        # Return None to prevent adding to context or re-prompting
        await result_callback(None)


async def main():
    """Main function to initialize and run the MedFlow intake assistant."""
    async with aiohttp.ClientSession() as session:
        # Configure Daily.co room and token
        (room_url, token) = await configure(session)

        # Set up Daily.co transport for real-time audio
        transport = DailyTransport(
            room_url,
            token,
            "MedFlow Assistant",
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                transcription_enabled=True,
            ),
        )

        # Initialize text-to-speech service
        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady
        )

        # Initialize OpenAI language model
        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

        # Set up conversation context
        messages = []
        context = OpenAILLMContext(messages=messages)
        context_aggregator = llm.create_context_aggregator(context)

        # Initialize intake processor and register functions
        intake = IntakeProcessor(context)
        llm.register_function("verify_birthday", intake.verify_birthday)
        llm.register_function("list_prescriptions", intake.list_prescriptions)
        llm.register_function("list_allergies", intake.list_allergies)
        llm.register_function("list_conditions", intake.list_conditions)
        llm.register_function("list_visit_reasons", intake.list_visit_reasons)

        # Set up frame logging for debugging
        fl = FrameLogger("LLM Output")

        # Build the audio processing pipeline
        pipeline = Pipeline(
            [
                transport.input(),           # Audio input from patient
                context_aggregator.user(),   # Process user responses
                llm,                         # AI language processing
                fl,                          # Frame logging
                tts,                         # Text-to-speech conversion
                transport.output(),          # Audio output to patient
                context_aggregator.assistant(), # Process assistant responses
            ]
        )

        # Configure pipeline task
        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )

        # Handle participant joining
        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            """Handle when the first patient joins the session."""
            await transport.capture_participant_transcription(participant["id"])
            print(f"Patient joined - Context: {context}")
            await task.queue_frames([OpenAILLMContextFrame(context)])

        # Run the pipeline
        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
