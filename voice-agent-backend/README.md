# Voice Agent Backend

A production-ready AI voice agent for appointment booking built with LiveKit Agents framework. Features real-time speech-to-text (Deepgram), flexible LLM support (OpenAI/OpenRouter/Together AI/Ollama), text-to-speech (Cartesia), and Supabase database integration.

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [LLM Providers](#llm-providers)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
- [Tools & Capabilities](#tools--capabilities)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Architecture

### System Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │──────▶│  LiveKit     │──────▶│   Agent     │
│  (React)    │◀─────│  Server      │◀─────│  (Python)    │
└─────────────┘      └──────────────┘      └─────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Supabase DB    │
                    └─────────────────┘
```

### Components

- **LiveKit Agents Framework**: Orchestrates voice processing pipeline
- **Deepgram STT**: Speech-to-text with built-in VAD (Voice Activity Detection)
- **LLM**: Configurable provider (OpenAI, OpenRouter, Together AI, or local Ollama)
- **Cartesia TTS**: Text-to-speech synthesis
- **Supabase**: PostgreSQL database for appointment management
- **FastAPI**: REST API for token generation
- **Beyond Presence**: Avatar integration for video display

### Data Flow

1. User speaks → Frontend captures audio
2. Audio sent to LiveKit → Deepgram transcribes speech
3. Transcript → LLM processes and generates response
4. LLM response → Cartesia converts to speech
5. Audio → Frontend plays agent's voice
6. Tool calls → Database operations (book, cancel, modify appointments)

## Features

- ✅ Real-time voice conversation
- ✅ Appointment booking, viewing, modification, and cancellation
- ✅ Automatic user identification via phone number
- ✅ Available slot checking
- ✅ Conversation state management
- ✅ Real-time transcript display
- ✅ Tool call tracking and visualization
- ✅ Conversation summary generation
- ✅ Scope enforcement (only handles appointment-related tasks)
- ✅ Duplicate message prevention
- ✅ Flexible LLM provider support
- ✅ Avatar integration (Beyond Presence)

## Project Structure

The codebase is organized into modular components:

```
voice-agent-backend/
├── agent.py                 # Main entry point (169 lines)
├── models/
│   ├── __init__.py
│   └── conversation_state.py    # Conversation state management
├── agents/
│   ├── __init__.py
│   └── appointment_agent.py    # Agent with function tools
├── handlers/
│   ├── __init__.py
│   ├── event_handlers.py        # Event handlers for conversation & tools
│   ├── avatar_handler.py        # Avatar setup logic
│   └── summary_handler.py       # Summary generation
├── config.py                # Configuration management
├── database.py              # Supabase database operations
├── llm_factory.py           # LLM provider factory
├── utils.py                 # Helper functions
├── api.py                   # FastAPI server
├── start_api.py             # API server entry point
└── run.py                   # Agent entry point
```

### Key Modules

- **`agent.py`**: Main entry point, orchestrates agent session setup
- **`models/conversation_state.py`**: Manages conversation state, message deduplication
- **`agents/appointment_agent.py`**: LLM agent with 7 function tools
- **`handlers/event_handlers.py`**: Handles conversation events and tool calls
- **`handlers/avatar_handler.py`**: Sets up Beyond Presence avatar
- **`handlers/summary_handler.py`**: Generates conversation summaries

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Supabase account
- API keys: LiveKit, Deepgram, Cartesia
- LLM provider API key (or Ollama for local)

### Installation

1. **Navigate to backend:**

   ```bash
   cd voice-agent-backend
   ```

2. **Set up virtual environment:**

   ```bash
   # macOS/Linux
   ./setup.sh

   # Windows
   setup.bat

   # Or manually
   python3 -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure environment:**

   ```bash
   cp ENV_EXAMPLE.txt .env
   # Edit .env with your API keys
   ```

4. **Set up database:**

   - Create Supabase project
   - Run SQL schema (see [Database Setup](#database-setup))
   - Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env`

5. **Start services:**

   ```bash
   # Terminal 1: API Server
   python start_api.py

   # Terminal 2: Agent
   python run.py dev
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# LiveKit Configuration (Required)
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# Speech Services (Required)
DEEPGRAM_API_KEY=your-deepgram-api-key
CARTESIA_API_KEY=your-cartesia-api-key

# LLM Provider (Choose one)
LLM_PROVIDER=ollama  # openai, openrouter, together, ollama

# OpenAI Configuration (if LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=https://api.openai.com/v1  # Optional

# OpenRouter Configuration (if LLM_PROVIDER=openrouter)
OPENROUTER_API_KEY=sk-or-v1-...
# LLM_MODEL=meta-llama/llama-3.1-70b-instruct  # Optional

# Together AI Configuration (if LLM_PROVIDER=together)
TOGETHER_API_KEY=your-together-api-key
# LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct-Turbo  # Optional

# Ollama Configuration (if LLM_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b  # or llama3.2, mistral, etc.

# Database (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Avatar Service (Beyond Presence) - Optional
BEYOND_PRESENCE_API_KEY=your-beyond-presence-api-key
BEYOND_PRESENCE_AVATAR_ID=your-avatar-id

# Server Configuration (Optional)
PORT=8080
HOST=0.0.0.0
```

## LLM Providers

### 1. OpenAI

**Best for:** Production, highest quality

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o  # Optional
```

**Models:** `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`

### 2. OpenRouter (Recommended for Free Tier)

**Best for:** Access to multiple models, free tier available

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=meta-llama/llama-3.1-70b-instruct
```

**Free Models:**
- `google/gemini-flash-1.5-8b`
- `meta-llama/llama-3.2-3b-instruct`
- `qwen/qwen-2.5-7b-instruct`

**Get API Key:** https://openrouter.ai/keys

### 3. Together AI

**Best for:** Fast inference, free tier available

```env
LLM_PROVIDER=together
TOGETHER_API_KEY=...
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct-Turbo
```

**Get API Key:** https://api.together.xyz/

### 4. Ollama (Local, Recommended for Development)

**Best for:** Free, unlimited, local development

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
```

**Setup:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull qwen2.5:7b`
3. Start Ollama: `ollama serve` (runs on port 11434)

## Database Setup

### Supabase Schema

Run this SQL in your Supabase SQL editor:

```sql
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  contact_number TEXT NOT NULL,
  user_name TEXT,
  appointment_date DATE NOT NULL,
  appointment_time TIME NOT NULL,
  duration_minutes INTEGER DEFAULT 30,
  status TEXT DEFAULT 'confirmed',
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contact_number ON appointments(contact_number);
CREATE INDEX idx_appointment_datetime ON appointments(appointment_date, appointment_time);
```

## API Endpoints

### FastAPI Server (`start_api.py`)

The API server runs on port 8080 (configurable via `PORT` env var).

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### `POST /api/token`

Generate LiveKit access token for frontend connection.

**Request:**
```json
{
  "room_name": "appointment-room",
  "participant_name": "user-123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "url": "wss://your-livekit-server.com"
}
```

## Tools & Capabilities

The agent implements 7 tools for appointment management:

1. **`identify_user`** - Ask for and validate user's phone number
2. **`fetch_slots`** - Get available appointment slots for next 7 days
3. **`book_appointment`** - Book a new appointment with conflict checking
4. **`retrieve_appointments`** - Get all appointments for a user
5. **`cancel_appointment`** - Cancel an appointment with ownership verification
6. **`modify_appointment`** - Modify date or time of existing appointment
7. **`end_conversation`** - End call and generate conversation summary

## Deployment

### Development

```bash
# Terminal 1: API Server
python start_api.py

# Terminal 2: Agent
python run.py dev
```

### Production

#### Using Process Manager (systemd/supervisor)

**systemd service example:**

```ini
[Unit]
Description=Voice Agent API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/voice-agent-backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python start_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Railway / Render

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Set start command: `python start_api.py` (for API) and `python run.py start` (for agent)
4. Expose WebSocket endpoint

## Troubleshooting

### Common Issues

#### Agent not connecting to room

**Solutions:**
1. Check LiveKit dashboard - verify agent worker is registered
2. Verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` are correct
3. Check agent logs for errors
4. Ensure agent worker is running: `python run.py dev`

#### LLM errors

**"Failed to create LLM"**
- Check API key is set correctly
- Verify model name is correct for provider
- For Ollama: Ensure `ollama serve` is running

#### Database errors

**"Connection failed"**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active
- Verify table schema matches

#### Avatar not appearing

- Check that `BEYOND_PRESENCE_API_KEY` and `BEYOND_PRESENCE_AVATAR_ID` are set
- Verify avatar session started successfully (check backend logs)
- Check browser console for track subscription errors

### Debug Logging

Enable debug logging in `run.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Cost Estimation

Estimated costs per conversation (approximate):

- **Deepgram STT**: $0.0043 per minute
- **LLM**: Varies by provider
  - OpenAI GPT-4o: ~$0.03 per 1K tokens
  - OpenRouter: Varies by model
  - Together AI: Varies by model
  - Ollama: Free (local)
- **Cartesia TTS**: $0.00001 per character
- **Avatar**: $0.05 per minute (if used)

**Note:** Costs are estimated. Actual costs may vary. Ollama is completely free for local use.

## License

MIT
