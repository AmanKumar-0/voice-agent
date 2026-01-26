"""Conversation state management."""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime


class ConversationState:
    """Manages conversation state throughout the session."""
    
    def __init__(self):
        self.user_identified: bool = False
        self.contact_number: Optional[str] = None
        self.user_name: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.should_end: bool = False
        self.start_time: datetime = datetime.utcnow()
        self.transcript: List[str] = []
        # Track sent messages to prevent duplicates
        self.sent_messages: set = set()
        # Debounce mechanism for user messages
        self.pending_user_message: Optional[str] = None
        self.pending_user_task: Optional[asyncio.Task] = None
        self.user_message_debounce_delay: float = 0.0
        self.last_user_message_time: Optional[datetime] = None
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history. Prevents duplicates from incremental transcriptions."""
        normalized_content = self._normalize_text(content)
        
        # Check if this is a duplicate of the last message (incremental transcription)
        if self.conversation_history:
            last_message = self.conversation_history[-1]
            if last_message.get("role") == role:
                last_normalized = self._normalize_text(last_message.get("content", ""))
                
                # If new message is same or a prefix of last message, skip it
                if normalized_content == last_normalized or last_normalized.startswith(normalized_content):
                    return
                
                # If new message contains the last message (final transcription), replace it
                if normalized_content.startswith(last_normalized) and len(normalized_content) > len(last_normalized):
                    self.conversation_history.pop()
                    if role == "user" and self.transcript and self.transcript[-1].startswith("User:"):
                        self.transcript.pop()
                    elif role == "assistant" and self.transcript and self.transcript[-1].startswith("Agent:"):
                        self.transcript.pop()
        
        # Add the message
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        if role == "user":
            self.transcript.append(f"User: {content}")
        elif role == "assistant":
            self.transcript.append(f"Agent: {content}")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for deduplication."""
        return text.strip().lower()
    
    def has_been_sent(self, role: str, text: str) -> bool:
        """Check if a message has already been sent to frontend."""
        normalized = self._normalize_text(text)
        message_key = f"{role}:{normalized}"
        return message_key in self.sent_messages
    
    def mark_as_sent(self, role: str, text: str):
        """Mark a message as sent to prevent duplicates."""
        normalized = self._normalize_text(text)
        message_key = f"{role}:{normalized}"
        self.sent_messages.add(message_key)
    
    def add_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """Add a tool call to history."""
        self.tool_calls.append({
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
