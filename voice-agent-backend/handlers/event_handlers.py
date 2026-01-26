"""Event handlers for agent session."""
import asyncio
import json
import logging
from datetime import datetime

from livekit.agents import AgentSession
from livekit import rtc

from models.conversation_state import ConversationState

logger = logging.getLogger(__name__)


def setup_event_handlers(session: AgentSession, state: ConversationState, ctx):
    """Set up event handlers for conversation and tool calls."""
    
    def on_conversation_item_added(event):
        """Handle conversation items being added (both user and assistant messages)."""
        async def handle_conversation_item_added():
            # Extract text from the event item
            text = None
            role = None
            
            if hasattr(event, 'item'):
                item = event.item
                
                # Get role from item
                if hasattr(item, 'role'):
                    role = item.role
                
                # Extract text from content (ChatMessage has content as a list)
                if hasattr(item, 'content'):
                    content = item.content
                    if isinstance(content, list):
                        text = ' '.join(str(c) for c in content if c)
                    elif content:
                        text = str(content)
                
                # Fallback: try text or text_content attributes
                if not text:
                    if hasattr(item, 'text') and item.text:
                        text = str(item.text)
                    elif hasattr(item, 'text_content') and item.text_content:
                        text = str(item.text_content)
            
            # Process user and assistant messages differently
            if text and role == 'user':
                # Update last message time
                state.last_user_message_time = datetime.utcnow()
                
                # Cancel previous pending task if exists
                if state.pending_user_task and not state.pending_user_task.done():
                    state.pending_user_task.cancel()
                
                # Update pending message (always use the latest/longest version)
                normalized_new = state._normalize_text(text)
                if state.pending_user_message:
                    normalized_pending = state._normalize_text(state.pending_user_message)
                    is_incremental = (
                        normalized_new.startswith(normalized_pending) or
                        normalized_pending.startswith(normalized_new) or
                        len(normalized_new) >= len(normalized_pending) * 0.8
                    )
                    
                    if is_incremental:
                        if len(normalized_new) >= len(normalized_pending):
                            state.pending_user_message = text
                    else:
                        # Completely different text - process pending immediately
                        if state.pending_user_task and not state.pending_user_task.done():
                            state.pending_user_task.cancel()
                        
                        async def process_pending_now():
                            pending_msg = state.pending_user_message
                            if pending_msg and not state.has_been_sent('user', pending_msg):
                                previous_count = len(state.conversation_history)
                                state.add_message('user', pending_msg)
                                if len(state.conversation_history) > previous_count:
                                    try:
                                        if ctx.room and ctx.room.local_participant:
                                            await ctx.room.local_participant.publish_data(
                                                json.dumps({
                                                    "type": "transcript",
                                                    "role": "user",
                                                    "text": pending_msg,
                                                    "timestamp": datetime.utcnow().isoformat()
                                                }).encode(),
                                                reliable=True
                                            )
                                            state.mark_as_sent('user', pending_msg)
                                    except Exception as e:
                                        logger.error(f"Error sending transcript: {e}")
                        
                        asyncio.create_task(process_pending_now())
                        state.pending_user_message = text
                else:
                    state.pending_user_message = text
                
                # Create debounced task to process after silence
                async def process_user_message_after_debounce():
                    await asyncio.sleep(state.user_message_debounce_delay)
                    
                    if state.last_user_message_time:
                        time_since_last = (datetime.utcnow() - state.last_user_message_time).total_seconds()
                        if time_since_last < state.user_message_debounce_delay - 0.2:
                            return
                    
                    if not state.pending_user_message:
                        return
                    
                    final_text = state.pending_user_message.strip()
                    
                    if not final_text or len(final_text) < 2:
                        state.pending_user_message = None
                        state.last_user_message_time = None
                        return
                    
                    state.pending_user_message = None
                    state.last_user_message_time = None
                    
                    if state.has_been_sent('user', final_text):
                        return
                    
                    previous_history_count = len(state.conversation_history)
                    state.add_message('user', final_text)
                    
                    if len(state.conversation_history) > previous_history_count:
                        try:
                            if ctx.room and ctx.room.local_participant:
                                await ctx.room.local_participant.publish_data(
                                    json.dumps({
                                        "type": "transcript",
                                        "role": "user",
                                        "text": final_text,
                                        "timestamp": datetime.utcnow().isoformat()
                                    }).encode(),
                                    reliable=True
                                )
                                state.mark_as_sent('user', final_text)
                        except Exception as e:
                            logger.error(f"Error sending transcript: {e}")
                
                state.pending_user_task = asyncio.create_task(process_user_message_after_debounce())
                
            elif text and role == 'assistant':
                # For assistant messages, process immediately
                if state.has_been_sent('assistant', text):
                    return
                
                previous_history_count = len(state.conversation_history)
                state.add_message('assistant', text)
                
                if len(state.conversation_history) > previous_history_count:
                    try:
                        if ctx.room and ctx.room.local_participant:
                            await ctx.room.local_participant.publish_data(
                                json.dumps({
                                    "type": "transcript",
                                    "role": "assistant",
                                    "text": text,
                                    "timestamp": datetime.utcnow().isoformat()
                                }).encode(),
                                reliable=True
                            )
                            state.mark_as_sent('assistant', text)
                    except Exception as e:
                        logger.error(f"Error sending transcript: {e}")
        
        asyncio.create_task(handle_conversation_item_added())
    
    session.on("conversation_item_added", on_conversation_item_added)
    
    def on_function_tools_executed(event):
        """Track when function tools are executed and send to frontend."""
        async def handle_function_tools_executed():
            tool_name = getattr(event, 'tool_name', None)
            if not tool_name:
                logger.warning(f"Function tool executed event has no tool_name. Event: {event}")
                return
            
            parameters = getattr(event, 'parameters', {})
            result = getattr(event, 'result', {})
            
            result_dict = result if isinstance(result, dict) else {"message": str(result)}
            state.add_tool_call(tool_name, parameters, result_dict)
            
            try:
                if ctx.room and ctx.room.local_participant:
                    tool_data = {
                        "type": "tool_call",
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "status": "success",
                        "result": result_dict,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await ctx.room.local_participant.publish_data(
                        json.dumps(tool_data).encode(),
                        reliable=True
                    )
            except Exception as e:
                logger.error(f"Error sending tool call event: {e}")
        
        asyncio.create_task(handle_function_tools_executed())
    
    session.on("function_tools_executed", on_function_tools_executed)


def setup_room_listeners(room: rtc.Room, state: ConversationState):
    """Set up room event listeners."""
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        # Only end conversation if user (not avatar) disconnects
        if participant.identity != "bey-avatar-agent":
            state.should_end = True
    
    room.on("participant_disconnected", on_participant_disconnected)
