# Voice agent: LiveKit agent (run.py dev), not the default Cerebrium Uvicorn + main
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app (main.py for Cerebrium import, run.py + agent code for the agent)
COPY . .

# Run the LiveKit agent; Cerebrium may still start its server, so main.py must exist for import
# Cloud Run sets PORT env var, which run.py reads programmatically
CMD ["python", "run.py", "dev"]
