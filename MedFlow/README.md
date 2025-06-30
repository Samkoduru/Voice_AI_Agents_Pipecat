# MedFlow: AI-Powered Patient Intake Assistant

A sophisticated AI-powered virtual assistant designed to revolutionize the medical intake process. MedFlow streamlines patient information collection through natural voice conversations, reducing administrative burden and improving the patient experience before doctor visits.

💡 Looking to build structured conversations? Check out [Pipecat Flows](https://github.com/pipecat-ai/pipecat-flows) for managing complex conversational states and transitions.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Key Components](#key-components)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Cartesia Best Practices](#cartesia-best-practices)
- [Use Cases](#use-cases)
- [Security & Privacy](#security--privacy)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

For a guided setup experience, run the setup script:

```sh
python src/config/medflow_setup.py
```

This will:
- Check Python version compatibility
- Create `.env` file from template
- Verify all dependencies are available
- Provide next steps for configuration

## Features

- **Identity Verification**: Confirms patient identity by verifying their date of birth
- **Prescription Information**: Collects details about current medications and dosages
- **Allergy Documentation**: Records patient allergies for medical safety
- **Medical Conditions**: Gathers information about existing medical conditions
- **Reason for Visit**: Captures the purpose of the current doctor's visit
- **Natural Voice Interaction**: Conversational AI that feels human and professional

## Technical Stack

- **Language**: Python 3.10+
- **AI Model**: OpenAI's GPT-4 for natural language processing
- **Text-to-Speech**: Cartesia TTS Service for lifelike voice responses
- **Audio Processing**: Silero VAD (Voice Activity Detection) for conversation flow
- **Real-time Communication**: Daily.co API for seamless audio streaming
- **Web Framework**: FastAPI for robust server implementation

## Key Components

- **IntakeProcessor**: Manages the conversation flow and information gathering process
- **DailyTransport**: Handles real-time audio communication with patients
- **CartesiaTTSService**: Converts AI responses to natural-sounding speech
- **OpenAILLMService**: Processes natural language and generates appropriate responses
- **Pipeline**: Orchestrates the flow of information between different components

## How It Works

1. **Patient Introduction**: The AI assistant (Jessica) introduces herself and explains the intake process
2. **Identity Verification**: Verifies the patient's identity by confirming their date of birth
3. **Systematic Information Collection**: 
   - Collects current prescription medications and dosages
   - Documents patient allergies for medical safety
   - Gathers information about existing medical conditions
   - Captures the reason for the current doctor's visit
4. **Data Logging**: All collected information is securely logged for medical professionals
5. **Conversation Completion**: Thanks the patient and concludes the intake process

ℹ️ **Note**: The first time you run the application, it may take extra time to download the VAD (Voice Activity Detection) model.

## Prerequisites

- Python 3.10 or higher
- API keys for:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Daily.co](https://dashboard.daily.co/developers)
  - [Cartesia](https://cartesia.ai/)

## Installation

1. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

## Running the Application

### Development Mode

```bash
python medflow.py
```

Then visit `http://localhost:7860/` in your browser to start a patient intake session.

### Docker Deployment

```bash
# Build the Docker image
docker build -t medflow-intake .

# Run the container
docker run --env-file .env -p 7860:7860 medflow-intake
```

## Cartesia Best Practices

Since this application uses Cartesia for text-to-speech, follow these best practices for optimal voice quality:

### Documentation Resources
- [Formatting Text for Sonic](https://docs.cartesia.ai/build-with-sonic/formatting-text-for-sonic/best-practices)
- [Inserting Breaks and Pauses](https://docs.cartesia.ai/build-with-sonic/formatting-text-for-sonic/inserting-breaks-pauses)
- [Spelling Out Input Text](https://docs.cartesia.ai/build-with-sonic/formatting-text-for-sonic/spelling-out-input-text)

### Example Implementation

```python
messages = [
    {
        "role": "system",
        "content": '''You are Jessica, a professional medical intake assistant. Format all responses following these guidelines:

1. Use proper punctuation and end each response with appropriate punctuation
2. Format dates as MM/DD/YYYY
3. Insert pauses using - or <break time='1s' /> for longer pauses
4. Use ?? for emphasized questions
5. Avoid quotation marks unless citing
6. Add spaces between URLs/emails and punctuation marks
7. For medical terms, provide pronunciation guidance in [brackets]
8. Keep responses clear and concise
9. Maintain a professional, caring tone

Your goal is to collect patient information efficiently while maintaining a warm, professional demeanor. Your output will be converted to audio, so maintain natural communication flow.'''
    }
]
```

## Use Cases

- **Medical Clinics**: Streamline patient intake processes
- **Telemedicine**: Pre-visit information collection
- **Healthcare Systems**: Standardize intake procedures
- **Medical Research**: Automated data collection for studies

## Security & Privacy

- All patient data is processed securely
- No data is stored permanently in the demo version
- HIPAA-compliant data handling practices
- Secure API key management

## Project Structure

```
MedFlow/
├── src/
│   ├── api/
│   │   └── medflow_server.py      # FastAPI server application
│   ├── core/
│   │   └── patient_intake.py      # Core patient intake logic
│   ├── config/
│   │   ├── medflow_setup.py       # Setup and configuration script
│   │   └── daily_config.py        # Daily.co configuration
│   └── utils/
│       └── assets/                # Audio feedback files
├── tests/                         # Test files (future)
├── docs/                          # Documentation (future)
├── medflow.py                     # Main entry point
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── env.example                    # Environment variables template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the BSD 2-Clause License - see the LICENSE file for details.