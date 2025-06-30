# Python Client for Server Testing

This Python client enables automated testing of the Twilio chatbot server via WebSocket without the need to make actual phone calls. It simulates multiple concurrent users interacting with the AI chatbot.

## Features

- **Automated Testing**: Simulates multiple concurrent client connections
- **Real-time Audio**: Full audio pipeline testing with STT, LLM, and TTS
- **Configurable Duration**: Set custom test session lengths
- **Audio Recording**: Saves conversation audio for analysis
- **Concurrent Testing**: Test multiple simultaneous connections

## Prerequisites

- Python 3.10+
- All API keys configured in `.env` file (see main README)
- Server running on localhost:8765

## Setup Instructions

### 1. Configure the Stream Template

Edit the `templates/streams.xml` file to point to your server's WebSocket endpoint:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="ws://localhost:8765/ws" />
  </Connect>
  <Pause length="40"/>
</Response>
```

### 2. Start the Server in Test Mode

Run the server with the `-t` flag to indicate test mode:

```sh
# Ensure you're in the project directory and your virtual environment is activated
python server.py -t
```

### 3. Run the Client

Start the client and point it to the server URL:

```sh
python client.py -u http://localhost:8765 -c 2
```

## Command Line Options

- `-u, --url`: Server URL (default: `http://localhost:8765`)
- `-c, --clients`: Number of concurrent client connections (default: 1)
- `-d, --duration`: Duration of each client session in seconds (default: 30)

## Examples

```sh
# Test with 1 client for 30 seconds
python client.py -u http://localhost:8765 -c 1

# Test with 5 clients for 60 seconds each
python client.py -u http://localhost:8765 -c 5 -d 60

# Test against a remote server
python client.py -u https://your-server.com -c 3 -d 45
```

## Output

The client will:
- Connect to the server and establish WebSocket connections
- Simulate user conversations with the AI
- Save audio recordings as WAV files (format: `client_X_recording_YYYYMMDD_HHMMSS.wav`)
- Display real-time logs of the conversation
- Automatically disconnect after the specified duration

## Troubleshooting

1. **Connection Failed**: Ensure the server is running and accessible
2. **Audio Issues**: Check that all API keys are properly configured
3. **Permission Errors**: Ensure write permissions in the current directory for audio files

## Notes

- The client uses the same AI services as the server (OpenAI, Deepgram, Cartesia)
- Audio files are saved in the current working directory
- Each client simulates a different persona (8-year-old child asking questions)
- The server should be running in test mode (`-t` flag) for optimal testing
