"""
Cerebrium entry point: provides the required 'main' module and runs the LiveKit agent worker.
- Starts the agent worker in a background thread so it connects to LiveKit and handles sessions.
- Exposes /health and a POST endpoint (for Cerebrium's callable endpoint) that accepts JSON (prompt).
"""
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Track agent thread so we can report status
_agent_thread: threading.Thread | None = None


def _run_agent_worker():
    """Run the LiveKit agent worker (blocking). Called in a background thread."""
    try:
        from run import main as run_agent
        run_agent()
    except Exception as e:
        logger.exception("Agent worker exited: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the LiveKit agent worker in a background thread when the app starts."""
    global _agent_thread
    _agent_thread = threading.Thread(target=_run_agent_worker, daemon=True)
    _agent_thread.start()
    logger.info("LiveKit agent worker started in background")
    yield
    # Shutdown: thread is daemon so it will exit when process exits
    _agent_thread = None


app = FastAPI(title="Voice Agent", lifespan=lifespan)


class PredictRequest(BaseModel):
    """JSON body Cerebrium sends (prompt)."""
    prompt: str | None = None


@app.get("/health")
def health():
    return {"status": "healthy", "agent_thread_alive": _agent_thread is not None and _agent_thread.is_alive()}


@app.post("/predict")
def predict(request: PredictRequest):
    """
    Cerebrium callable endpoint: accepts JSON with 'prompt'.
    The real agent runs as a LiveKit worker; this endpoint confirms the app is up.
    """
    return {
        "status": "ok",
        "message": "LiveKit agent worker is running in this container. Connect via LiveKit to use the voice agent.",
        "prompt_received": request.prompt is not None,
    }
