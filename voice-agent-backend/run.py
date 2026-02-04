"""Entry point for running the LiveKit agent."""
import asyncio
import logging
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
# from agent import entrypoint
from livekit.agents import cli, WorkerOptions
from config import Config
from agent import server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Reduce noise from expected timeout warnings when using Ollama
# Ollama can be slow, and the framework retries automatically
if Config.LLM_PROVIDER.lower() == "ollama":
    # Set LiveKit agents LLM logger to WARNING to reduce timeout noise
    # The framework handles retries automatically, so these are expected
    logging.getLogger("livekit.agents.llm").setLevel(logging.WARNING)
    logging.getLogger("livekit.agents.inference").setLevel(logging.WARNING)
    logger.info("Ollama LLM provider detected - timeout warnings are expected and will be retried automatically")


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""
    
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_health_server(port):
    """Start a simple HTTP server for health checks."""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info(f"Health check server listening on port {port}")
    httpd.serve_forever()


def main():
    """Main entry point."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Get port from environment (Cloud Run sets PORT, default to 8080 for local)
    health_port = int(os.getenv("PORT", "8080"))
    
    # Start health check server in background thread
    health_thread = threading.Thread(
        target=start_health_server,
        args=(health_port,),
        daemon=True
    )
    health_thread.start()
    
    # Run the LiveKit agent (it will use its default behavior)
    logger.info("Starting LiveKit agent...")
    cli.run_app(server)


if __name__ == "__main__":
    main()


# run the agent