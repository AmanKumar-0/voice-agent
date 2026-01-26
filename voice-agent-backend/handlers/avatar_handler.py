"""Avatar session management."""
import asyncio
import logging
from typing import Optional

from livekit.plugins import bey
from livekit.agents import AgentSession
from livekit import rtc

from config import Config

logger = logging.getLogger(__name__)


async def setup_avatar(session: AgentSession, room: rtc.Room) -> Optional[bey.AvatarSession]:
    """Set up and start Beyond Presence avatar session."""
    if not Config.BEYOND_PRESENCE_API_KEY or not Config.BEYOND_PRESENCE_AVATAR_ID:
        return None
    
    # Check if avatar already exists in room
    avatar_already_exists = False
    if room:
        for participant in room.remote_participants.values():
            if participant.identity == "bey-avatar-agent":
                avatar_already_exists = True
                break
        
        if not avatar_already_exists and room.local_participant:
            if room.local_participant.identity == "bey-avatar-agent":
                avatar_already_exists = True
        
        # Wait and check again to handle race conditions
        if not avatar_already_exists:
            await asyncio.sleep(0.5)
            for participant in room.remote_participants.values():
                if participant.identity == "bey-avatar-agent":
                    avatar_already_exists = True
                    break
    
    if avatar_already_exists:
        return None
    
    # Initialize and start avatar session
    try:
        avatar_session = bey.AvatarSession(
            avatar_id=Config.BEYOND_PRESENCE_AVATAR_ID,
            api_key=Config.BEYOND_PRESENCE_API_KEY,
        )
        await avatar_session.start(session, room=room)
        return avatar_session
    except Exception as e:
        logger.error(f"Failed to start Beyond Presence avatar: {e}")
        return None
