# VoiceFlow: AI-Powered Twilio Voice Assistant

A sophisticated real-time voice conversation system that transforms Twilio phone calls into intelligent AI interactions. Built with FastAPI and Pipecat, this project creates a seamless audio pipeline that enables natural voice conversations with AI assistants through any phone call.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Deployment](#deployment)

## Quick Start

For a guided setup experience, run the setup script:

```sh
python setup.py
```

This will:
- Check Python version compatibility
- Create `.env` file from template
- Create `templates/streams.xml` from template
- Provide next steps for configuration

## Features

- **Real-time Voice Conversations**: Full-duplex audio communication via WebSockets
- **AI-Powered Responses**: Uses OpenAI GPT for intelligent conversation
- **High-Quality Speech Processing**: 
  - Deepgram for Speech-to-Text
  - Cartesia for Text-to-Speech
  - Silero VAD for voice activity detection
- **Twilio Integration**: Seamless integration with Twilio's voice services
- **Docker Support**: Easy containerized deployment
- **Testing Clients**: Both Python and TypeScript clients for testing without phone calls

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.10+**
- **Docker** (optional, for containerized deployment)
- **ngrok** (for local development tunneling)
- **API Keys**:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Deepgram API Key](https://console.deepgram.com/)
  - [Cartesia API Key](https://cartesia.ai/)
  - [Twilio Account](https://www.twilio.com/) with Account SID and Auth Token

## Installation

1. **Clone the repository**:
   ```sh
   git clone <your-repo-url>
   cd voiceflow-twilio
   ```

2. **Set up a virtual environment** (recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Install ngrok**:
   Download and install from [ngrok.com](https://ngrok.com/download)

## Configuration

1. **Set up environment variables**:
   ```sh
   cp env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   # AI Services
   OPENAI_API_KEY=sk-your-openai-key-here
   DEEPGRAM_API_KEY=your-deepgram-key-here
   CARTESIA_API_KEY=your-cartesia-key-here
   
   # Twilio Credentials
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   ```

2. **Configure Twilio**:
   - Go to your [Twilio Console](https://console.twilio.com/)
   - Navigate to Phone Numbers → Manage → Active numbers
   - Click on your phone number
   - Under "Voice Configuration":
     - Set "A call comes in" to "Webhook"
     - Enter your webhook URL (you'll get this after starting ngrok)
     - Set HTTP method to "POST"
   - Save the configuration

3. **Set up ngrok tunnel**:
   ```sh
   ngrok http 8765
   ```
   
   Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

4. **Configure the WebSocket URL**:
   ```sh
   cp templates/streams.xml.template templates/streams.xml
   ```
   
   Edit `templates/streams.xml` and replace `<your server url>` with your ngrok domain:
   ```xml
   <Stream url="wss://abc123.ngrok.io/ws"></Stream>
   ```

## Running the Application

### Option 1: Python (Development)

```sh
python server.py
```

### Option 2: Docker (Production)

```sh
# Build the image
docker build -t voiceflow-twilio .

# Run the container
docker run -it --rm -p 8765:8765 --env-file .env voiceflow-twilio
```

The server will start on port 8765. Keep it running while testing.

## Testing

You can test the voice assistant without making actual phone calls using the included test clients:

### Python Client (Automated Testing)
```sh
cd client/python
python client.py -u http://localhost:8765 -c 2
```

### TypeScript Client (Manual Testing)
```sh
cd client/typescript
npm install
npm run dev
```
Then visit `http://localhost:5173` in your browser.

## Usage

1. **Start the server** (see Running the Application above)
2. **Start ngrok** if not already running
3. **Make a call** to your Twilio phone number
4. **Talk to the AI** - the assistant will respond with an elementary teacher persona

## Deployment

### Local Development
- Use ngrok for tunneling
- Keep the server running locally
- Update Twilio webhook URL when ngrok URL changes

### Production Deployment
- Deploy to a cloud provider (AWS, GCP, Azure, etc.)
- Use a proper domain name instead of ngrok
- Set up SSL certificates
- Configure environment variables securely
- Use Docker for consistent deployment

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**:
   - Check that ngrok is running
   - Verify the URL in `templates/streams.xml`
   - Ensure the server is running on port 8765

2. **Audio Not Working**:
   - Check API keys in `.env`
   - Verify all services (OpenAI, Deepgram, Cartesia) are accessible
   - Check browser console for errors (TypeScript client)

3. **Twilio Webhook Not Responding**:
   - Verify the webhook URL in Twilio console
   - Check that the server is accessible from the internet
   - Ensure the webhook method is set to POST

### Logs
The application uses loguru for logging. Check the console output for detailed error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the BSD 2-Clause License - see the LICENSE file for details.