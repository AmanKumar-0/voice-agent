"""
Cerebrium entry point: provides the required 'main' module and runs the LiveKit agent worker.
- Starts the agent as a subprocess (python run.py dev) so it runs like the CLI.
- Exposes /health (with agent status) and POST /predict for Cerebrium's callable endpoint.
"""
import logging
import os
import subprocess
import sys
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_agent_process: subprocess.Popen | None = None
_agent_stderr_tail: list[str] = []
_AGENT_STDERR_LINES = 20


def _capture_stderr_when_done(proc: subprocess.Popen) -> None:
    """Background: wait for process, then read stderr into _agent_stderr_tail for debugging."""
    global _agent_stderr_tail
    try:
        proc.wait(timeout=None)
        if proc.stderr:
            lines = proc.stderr.readlines()
            _agent_stderr_tail = [s.strip() for s in lines if s.strip()][-_AGENT_STDERR_LINES:]
    except Exception as e:
        _agent_stderr_tail = [str(e)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the LiveKit agent worker as a subprocess when the app starts."""
    global _agent_process, _agent_stderr_tail
    cwd = os.path.dirname(os.path.abspath(__file__))
    try:
        _agent_process = subprocess.Popen(
            [sys.executable, "run.py", "dev"],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
            text=True,
        )
        t = threading.Thread(target=_capture_stderr_when_done, args=(_agent_process,), daemon=True)
        t.start()
        logger.info("LiveKit agent worker started as subprocess (pid=%s)", _agent_process.pid)
    except Exception as e:
        logger.exception("Failed to start agent subprocess: %s", e)
        _agent_stderr_tail = [str(e)]
    yield
    if _agent_process is not None:
        try:
            _agent_process.terminate()
            _agent_process.wait(timeout=10)
        except Exception as e:
            logger.warning("Agent shutdown: %s", e)
        _agent_process = None
    _agent_stderr_tail = []


app = FastAPI(title="Voice Agent", lifespan=lifespan)


class PredictRequest(BaseModel):
    """JSON body Cerebrium sends (prompt)."""
    prompt: str | None = None


@app.get("/health")
def health():
    alive = _agent_process is not None and _agent_process.poll() is None
    out: dict = {
        "status": "healthy",
        "agent_alive": alive,
    }
    if _agent_process is not None and not alive:
        out["agent_exit_code"] = _agent_process.poll()
    if _agent_stderr_tail:
        out["agent_stderr_last_lines"] = _agent_stderr_tail
    return out


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
