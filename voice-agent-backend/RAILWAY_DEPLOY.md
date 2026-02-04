# Railway Deployment Guide

## Setup

Railway doesn't use Procfile. You need to create **two separate services** in Railway:

### Service 1: API

- **Start Command**: `python start_api.py`
- **Port**: Railway will auto-assign (use `PORT` env var)

### Service 2: Worker

- **Start Command**: `python run.py`
- **Port**: Not needed (no HTTP server)

## Steps

1. **Connect GitHub repo** to Railway
2. **Create first service (API)**:
   - Railway will auto-detect from `railway.json`
   - Start command: `python start_api.py`
3. **Create second service (Worker)**:
   - Add new service from same repo
   - Override start command: `python run.py`
4. **Set environment variables** for both services:
   - `LIVEKIT_URL`
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
   - `DEEPGRAM_API_KEY`
   - `CARTESIA_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `LLM_PROVIDER`
   - `OPENAI_API_KEY` (or other LLM provider keys)
   - `BEYOND_PRESENCE_API_KEY` (optional)
   - `BEYOND_PRESENCE_AVATAR_ID` (optional)

## Alternative: Single Service with Script

If you want to run both in one service, create `start.sh`:

```bash
#!/bin/bash
python start_api.py &
python run.py
```

Then set start command to: `bash start.sh`

But **recommended approach**: Use two separate services as above.
