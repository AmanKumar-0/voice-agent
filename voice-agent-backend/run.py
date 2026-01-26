"""Entry point for running the LiveKit agent."""
import logging
import sys
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


def main():
    """Main entry point."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Run the agent
    # cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    cli.run_app(server)


if __name__ == "__main__":
    main()
