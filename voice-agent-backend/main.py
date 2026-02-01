"""
Cerebrium entry point: provides the required 'main' module so the platform can load the user app.
This deployment runs the LiveKit agent via the custom runtime entrypoint; this module exists
so that if the platform imports 'main' (e.g. for health or fallback), the import succeeds.
"""
from fastapi import FastAPI

app = FastAPI(title="Voice Agent")


@app.get("/health")
def health():
    return {"status": "healthy"}
