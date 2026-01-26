"""Start the FastAPI server for token generation."""
import logging
import uvicorn
from api import app
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Validate that LiveKit config is present (required for token generation)
        if not Config.LIVEKIT_API_KEY or not Config.LIVEKIT_API_SECRET:
            logger.error("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
            exit(1)
        
        logger.info(f"Starting API server on {Config.HOST}:{Config.PORT}")
        uvicorn.run(
            app,
            host=Config.HOST,
            port=Config.PORT,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        exit(1)
