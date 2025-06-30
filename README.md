# Voice AI Agents with Pipecat

A collection of advanced voice AI agents built with Pipecat, demonstrating real-world applications of conversational AI for healthcare and telephony.

## 🎯 Projects

### 1. MedFlow: AI-Powered Patient Intake Assistant
A sophisticated AI-powered virtual assistant designed to revolutionize the medical intake process. MedFlow streamlines patient information collection through natural voice conversations, reducing administrative burden and improving the patient experience before doctor visits.

**Key Features:**
- Identity verification (DOB)
- Prescription information collection
- Allergy documentation
- Medical conditions tracking
- Visit reason documentation
- Natural, professional voice interaction

**Tech Stack:** Python, FastAPI, OpenAI GPT-4, Cartesia TTS, Daily.co API

[📁 View MedFlow Project](./patient-intake/)

---

### 2. VoiceFlow: AI-Powered Twilio Voice Assistant
A comprehensive, real-time voice conversation system that transforms Twilio phone calls into intelligent AI interactions. VoiceFlow enables natural, full-duplex conversations with AI assistants through any phone call.

**Key Features:**
- Real-time phone conversations via Twilio
- Speech-to-Text with Deepgram
- Text-to-Speech with Cartesia
- OpenAI LLM integration
- WebSocket-based audio pipeline
- Dockerized for easy deployment

**Tech Stack:** Python, FastAPI, Twilio, OpenAI, Deepgram, Cartesia, Pipecat

[📁 View VoiceFlow Project](./twilio-chatbot/)

---

## 🚀 Quick Start

Each project is independent and can be run separately. For a guided setup, use the included setup script in each directory:

### MedFlow (Patient Intake)
```bash
cd patient-intake
python3 -m venv venv
source venv/bin/activate
python setup.py
# Follow the instructions to configure your .env and run the server
```

### VoiceFlow (Twilio Voice Assistant)
```bash
cd twilio-chatbot
python3 -m venv venv
source venv/bin/activate
python setup.py
# Follow the instructions to configure your .env and run the server
```

## 📋 Prerequisites

- Python 3.10+
- OpenAI API Key
- Deepgram API Key (for VoiceFlow)
- Cartesia API Key
- Twilio Account (for VoiceFlow)
- Daily.co Account (for MedFlow)

## 🔧 Configuration

Each project has its own configuration and setup script:
- **MedFlow:** Uses Daily.co for real-time communication and patient intake
- **VoiceFlow:** Uses Twilio for phone integration and real-time AI conversations

See the individual project READMEs for detailed setup and deployment instructions.

## 📚 Documentation

- [MedFlow Documentation](./patient-intake/README.md)
- [VoiceFlow Documentation](./twilio-chatbot/README.md)

## 🤝 Contributing

These projects are built on the excellent [Pipecat](https://github.com/pipecat-ai/pipecat) framework. Each project is fully independent, professionally documented, and ready for real-world use or further development.

## 📄 License

This project is licensed under the BSD 2-Clause License. See individual subproject LICENSE files for details.

---

**Built with ❤️ using [Pipecat](https://github.com/pipecat-ai/pipecat)** 