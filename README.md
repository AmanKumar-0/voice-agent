# Superbryn - Voice Agent Platform

A complete voice agent platform for appointment booking with real-time conversation, avatar integration, and comprehensive tool management.

## Overview

Superbryn is a full-stack voice agent system that enables natural language appointment booking through voice conversations. The platform consists of a Python backend using LiveKit Agents framework and a React frontend for real-time interaction.

## Project Structure

```
superbryn/
├── voice-agent-backend/      # Python backend (LiveKit Agents)
│   ├── agent.py              # Main agent entry point
│   ├── models/               # Data models
│   ├── agents/               # Agent implementations
│   ├── handlers/             # Event and service handlers
│   └── ...
├── voice-agent-frontend/      # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   └── services/        # Service integrations
│   └── ...
└── Documentation files        # Technical documentation
```

## Quick Start

### Backend Setup

```bash
cd voice-agent-backend
./setup.sh  # or setup.bat on Windows
cp ENV_EXAMPLE.txt .env
# Edit .env with your API keys
python start_api.py  # Terminal 1
python run.py dev    # Terminal 2
```

### Frontend Setup

```bash
cd voice-agent-frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm start
```

See individual README files for detailed setup:

- [Backend README](voice-agent-backend/README.md)
- [Frontend README](voice-agent-frontend/README.md)

## Features

### Core Features

- ✅ **Real-time voice conversation** with speech-to-text and text-to-speech
- ✅ **Appointment management** (book, view, modify, cancel)
- ✅ **Avatar integration** with Beyond Presence
- ✅ **Tool call visualization** in real-time
- ✅ **Conversation summaries** with cost breakdown
- ✅ **Flexible LLM support** (OpenAI, OpenRouter, Together AI, Ollama)
- ✅ **Supabase database** integration

### Technical Features

- **Modular architecture** - Clean separation of concerns
- **Type-safe** - TypeScript frontend, type hints in Python
- **Real-time updates** - WebSocket-based communication
- **Error handling** - Comprehensive error recovery
- **Cost tracking** - Per-service cost breakdown

## Architecture

### System Flow

```
User → Frontend → LiveKit Server → Agent Backend → LLM/Database
                ↓
            Avatar (Beyond Presence)
```

### Components

1. **Frontend (React)**

   - Real-time UI with LiveKit client
   - Avatar display
   - Tool call visualization
   - Conversation management

2. **Backend (Python)**

   - LiveKit Agents framework
   - LLM integration (multiple providers)
   - Database operations (Supabase)
   - Event handling and state management

3. **Services**
   - LiveKit: Real-time communication
   - Deepgram: Speech-to-text
   - Cartesia: Text-to-speech
   - Beyond Presence: Avatar generation
   - Supabase: Database

## Documentation

### Main Documentation

- **[Backend README](voice-agent-backend/README.md)** - Complete backend setup and configuration
- **[Frontend README](voice-agent-frontend/README.md)** - Frontend setup and component documentation

### Technical Documentation

- **[AGENT_PY_EXPLAINED.md](AGENT_PY_EXPLAINED.md)** - Detailed explanation of agent.py (legacy, now modular)
- **[TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)** - Technical architecture and implementation details
- **[EVENTS_AND_PUBLISH_DATA_EXPLAINED.md](EVENTS_AND_PUBLISH_DATA_EXPLAINED.md)** - Event system and data channel usage
- **[TOOL_DEFINITIONS_EXPLAINED.md](TOOL_DEFINITIONS_EXPLAINED.md)** - Function tool definitions and usage

### Setup Guides

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[QUICK_START_CONVERSATION.md](QUICK_START_CONVERSATION.md)** - Quick start guide
- **[START_CONVERSATION.md](START_CONVERSATION.md)** - Starting conversations guide
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - High-level project overview

## Configuration

### Required Services

1. **LiveKit** - Real-time communication server
2. **Deepgram** - Speech-to-text API
3. **Cartesia** - Text-to-speech API
4. **Supabase** - PostgreSQL database
5. **LLM Provider** - OpenAI, OpenRouter, Together AI, or Ollama
6. **Beyond Presence** - Avatar service (optional)

### Environment Variables

See individual README files for complete environment variable documentation:

- [Backend Configuration](voice-agent-backend/README.md#configuration)
- [Frontend Configuration](voice-agent-frontend/README.md#configuration)

## Development

### Backend Development

```bash
cd voice-agent-backend
source venv/bin/activate
python run.py dev
```

### Frontend Development

```bash
cd voice-agent-frontend
npm start
```

### Code Structure

The backend follows a modular architecture:

- **`models/`** - Data models (ConversationState)
- **`agents/`** - Agent implementations (AppointmentAgent)
- **`handlers/`** - Event handlers, avatar setup, summary generation
- **`agent.py`** - Main entry point (clean and focused)

## Deployment

### Backend

- **Railway/Render**: Set start command to `python start_api.py` (API) and `python run.py start` (agent)
- **Fly.io**: Use provided Dockerfile or buildpack
- **systemd**: Use provided service file template

### Frontend

- **Netlify**: Connect repo, set build command `npm run build`
- **Vercel**: Connect repo, framework preset: Create React App
- **Static hosting**: Build and deploy `build/` directory

See individual README files for detailed deployment instructions.

## Troubleshooting

### Common Issues

1. **Agent not connecting**: Check LiveKit credentials and agent worker status
2. **No audio**: Verify microphone permissions and browser compatibility
3. **Avatar not showing**: Check Beyond Presence API key and avatar session
4. **Database errors**: Verify Supabase credentials and table schema

See individual README files for detailed troubleshooting:

- [Backend Troubleshooting](voice-agent-backend/README.md#troubleshooting)
- [Frontend Troubleshooting](voice-agent-frontend/README.md#troubleshooting)

## Cost Estimation

Approximate costs per conversation:

- **Deepgram STT**: $0.0043/minute
- **LLM**: Varies by provider (Ollama is free)
- **Cartesia TTS**: $0.00001/character
- **Avatar**: $0.05/minute (if used)

See [Backend README](voice-agent-backend/README.md#cost-estimation) for detailed cost breakdown.

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:

- Check the troubleshooting sections in individual README files
- Review technical documentation files
- Check backend and frontend logs for errors

---

**Note**: This is an internal project. For detailed setup and configuration, refer to the individual README files in `voice-agent-backend/` and `voice-agent-frontend/` directories.
