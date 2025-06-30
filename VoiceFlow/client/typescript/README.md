# TypeScript Client for Server Testing

This TypeScript client enables manual testing of the Twilio chatbot server via WebSocket without the need to make actual phone calls. It provides a web-based interface for real-time voice conversations with the AI chatbot.

## Features

- **Web-based Interface**: Easy-to-use browser interface for testing
- **Real-time Voice**: Full audio pipeline testing with microphone input
- **Visual Feedback**: Real-time connection status and debug information
- **Manual Control**: Connect/disconnect at will for flexible testing
- **Transcript Display**: See both user and bot transcripts in real-time

## Prerequisites

- Node.js 16+ and npm
- All API keys configured in `.env` file (see main README)
- Server running on localhost:8765
- Modern browser with microphone access

## Setup

1. **Start the bot server** (see the [main README](../../README.md)):
   ```sh
   python server.py -t
   ```

2. **Navigate to the TypeScript client directory**:
   ```sh
   cd client/typescript
   ```

3. **Install dependencies**:
   ```sh
   npm install
   ```

4. **Run the client app**:
   ```sh
   npm run dev
   ```

5. **Open your browser** and visit `http://localhost:5173`

## Usage

1. **Connect**: Click the "Connect" button to establish a WebSocket connection
2. **Grant Microphone Access**: Allow browser access to your microphone when prompted
3. **Start Talking**: Speak into your microphone to interact with the AI
4. **Monitor**: Watch the debug panel for real-time conversation logs
5. **Disconnect**: Click "Disconnect" when finished testing

## Interface Elements

- **Status Bar**: Shows connection status and control buttons
- **Debug Panel**: Displays real-time logs of the conversation
- **Audio Element**: Handles bot audio output automatically

## Troubleshooting

### Connection Issues
- Ensure the server is running on port 8765
- Check that the WebSocket endpoint is accessible
- Verify the server is running in test mode (`-t` flag)

### Audio Issues
- Check browser microphone permissions
- Ensure all API keys are properly configured
- Check browser console for error messages

### Browser Compatibility
- Tested with Chrome, Firefox, Safari, and Edge
- Requires WebRTC support for microphone access
- HTTPS required for microphone access in production

## Development

### Project Structure
```
client/typescript/
├── src/
│   ├── app.ts          # Main application logic
│   └── style.css       # Styling
├── index.html          # HTML template
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript configuration
└── vite.config.js      # Vite configuration
```

### Building for Production
```sh
npm run build
```

### Preview Production Build
```sh
npm run preview
```

## Notes

- The client uses the Pipecat JavaScript SDK for WebSocket communication
- Audio is processed at 8kHz sample rate to match the server
- The interface automatically handles WebSocket reconnection
- Debug logs include timestamps for easy troubleshooting
