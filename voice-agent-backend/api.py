"""FastAPI endpoints for token generation and health checks."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api
from config import Config
import logging
import asyncio

logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Agent API")

# CORS middleware - allow all origins for development
# In production, replace "*" with your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class TokenRequest(BaseModel):
    room_name: str
    participant_name: str


class TokenResponse(BaseModel):
    token: str
    url: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """Generate a LiveKit access token."""
    try:
        # Validate configuration
        if not Config.LIVEKIT_API_KEY or not Config.LIVEKIT_API_SECRET:
            logger.error("LIVEKIT_API_KEY or LIVEKIT_API_SECRET not configured")
            raise HTTPException(
                status_code=500,
                detail="LiveKit API credentials not configured"
            )
        
        # Create access token
        token = api.AccessToken(Config.LIVEKIT_API_KEY, Config.LIVEKIT_API_SECRET) \
            .with_identity(request.participant_name) \
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=request.room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                )
            )
        
        token_str = token.to_jwt()
        
        logger.info(f"Generated token for participant: {request.participant_name}, room: {request.room_name}")
        
        # Try to explicitly dispatch agent to the room
        # This ensures the agent is assigned when the user connects
        try:
            # Import here to avoid circular dependencies
            from livekit import api as lk_api
            
            # Create LiveKit API client
            lkapi = lk_api.LiveKitAPI(
                url=Config.LIVEKIT_URL,
                api_key=Config.LIVEKIT_API_KEY,
                api_secret=Config.LIVEKIT_API_SECRET
            )
            
            # Explicitly dispatch agent to the room (this is async, so we need to await it)
            # This tells LiveKit to assign an available agent to this room
            dispatch_response = await lkapi.agent_dispatch.create_dispatch(
                lk_api.CreateAgentDispatchRequest(
                    room=request.room_name,
                    # Don't specify agent_name - let LiveKit choose an available agent
                )
            )
            logger.info(f"Agent dispatch created for room: {request.room_name}")
            await lkapi.aclose()
        except Exception as e:
            # If dispatch fails, log but don't fail the token generation
            # The agent might still work with automatic dispatch
            logger.warning(f"Could not create agent dispatch (agent may still auto-join): {e}")
        
        return TokenResponse(
            token=token_str,
            url=Config.LIVEKIT_URL
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating token: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
