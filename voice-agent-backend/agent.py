"""Main LiveKit agent implementation."""
import asyncio
import json
import logging
from datetime import datetime

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, deepgram

from config import Config
from models.conversation_state import ConversationState
from agents.appointment_agent import AppointmentAgent
from handlers.event_handlers import setup_event_handlers, setup_room_listeners
from handlers.avatar_handler import setup_avatar
from handlers.summary_handler import generate_conversation_summary
from llm_factory import create_llm

logger = logging.getLogger(__name__)
load_dotenv()

# Global state for conversation (in production, use proper state management)
conversation_state = {}

# Create server
server = AgentServer()


def prewarm(proc: JobProcess):
    """Prewarm function - Deepgram STT includes built-in VAD."""
    proc.userdata["vad"] = None


server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: JobContext):
    """Main agent entry point."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    room_name = ctx.room.name
    
    # Create conversation state for this session
    state = ConversationState()
    conversation_state[room_name] = state
    
    # Initialize LLM
    try:
        llm_model = create_llm()
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}")
        if Config.OPENAI_API_KEY:
            llm_model = inference.LLM(model=f"openai/{Config.get_default_model()}")
        else:
            raise ValueError(f"Cannot create LLM: {e}")
    
    # Set up voice AI pipeline
    stt_model = deepgram.STT(language="en-US", model="nova-2")
    
    if not Config.CARTESIA_API_KEY:
        logger.warning("CARTESIA_API_KEY not set! TTS may not work.")
    
    tts_model = inference.TTS(
        model="cartesia/sonic-3",
        voice="79a125e8-cd45-4c13-8a67-188112f4dd22"
    )
    
    # Create AgentSession
    session = AgentSession(
        stt=stt_model,
        llm=llm_model,
        tts=tts_model,
        preemptive_generation=True,
    )
    
    # Set up event handlers
    setup_event_handlers(session, state, ctx)
    
    # Create agent instance
    agent = AppointmentAgent(state, ctx)
    
    # Set up avatar
    avatar_session = await setup_avatar(session, ctx.room)

    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )
    
    # Set up room listeners
    setup_room_listeners(ctx.room, state)
    
    # Connect to the room
    await ctx.connect()
    
    # Monitor for end conversation
    async def monitor_conversation():
        while not state.should_end:
            await asyncio.sleep(1)
        
        # Generate summary
        try:
            await generate_conversation_summary(state, ctx)
            await asyncio.sleep(1.0)
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
        
        # Notify frontend that conversation is ending
        try:
            if ctx.room and ctx.room.local_participant:
                await ctx.room.local_participant.publish_data(
                    json.dumps({
                        "type": "conversation_ended",
                        "message": "Conversation ended by agent",
                        "timestamp": datetime.utcnow().isoformat()
                    }).encode(),
                    reliable=True
                )
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Error sending conversation_ended event: {e}")
        
        # Close avatar session if active
        if avatar_session:
            try:
                await avatar_session.aclose()
            except Exception as e:
                logger.warning(f"Error closing avatar session: {e}")
        
        # Close session gracefully
        try:
            await session.aclose()
        except Exception as e:
            if "timeout" not in str(e).lower() and "closed" not in str(e).lower():
                logger.warning(f"Error closing session: {e}")
    
    # Start monitoring task
    asyncio.create_task(monitor_conversation())


if __name__ == "__main__":
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    
    cli.run_app(server)
