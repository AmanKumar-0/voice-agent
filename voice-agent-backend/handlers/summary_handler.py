"""Conversation summary generation."""
import json
import logging
from typing import Dict, Any
from datetime import datetime

from openai import OpenAI

from models.conversation_state import ConversationState
from database import Database
from utils import format_appointment_summary
from config import Config

logger = logging.getLogger(__name__)
db = Database()


async def generate_conversation_summary(state: ConversationState, ctx) -> Dict[str, Any]:
    """Generate a summary of the conversation."""
    try:
        full_transcript = "\n".join(state.transcript)
        appointments = []
        if state.contact_number:
            appointments = db.get_appointments(state.contact_number, include_cancelled=False)
        
        duration_minutes = (datetime.utcnow() - state.start_time).total_seconds() / 60
        
        # Calculate costs
        estimated_tokens = len(full_transcript.split()) * 1.3
        llm_cost = 0.0
        llm_rate = 0.0
        
        if Config.LLM_PROVIDER == "ollama":
            llm_cost = 0.0
            llm_rate = 0.0
        elif Config.LLM_PROVIDER in ["openrouter", "together"]:
            llm_rate = 0.0001
            llm_cost = (estimated_tokens / 1000) * llm_rate
        else:
            llm_rate = Config.OPENAI_RATE_PER_1K_TOKENS
            llm_cost = (estimated_tokens / 1000) * llm_rate
        
        cost_breakdown = {
            "deepgram_stt": {
                "minutes": duration_minutes,
                "rate_per_minute": Config.DEEPGRAM_RATE_PER_MINUTE,
                "cost": duration_minutes * Config.DEEPGRAM_RATE_PER_MINUTE
            },
            "llm": {
                "estimated_tokens": estimated_tokens,
                "rate_per_1k_tokens": llm_rate,
                "cost": llm_cost,
                "provider": Config.LLM_PROVIDER
            },
            "cartesia_tts": {
                "estimated_characters": len(full_transcript) * 0.5,
                "rate_per_char": Config.CARTESIA_RATE_PER_CHAR,
                "cost": len(full_transcript) * 0.5 * Config.CARTESIA_RATE_PER_CHAR
            },
            "avatar": {
                "minutes": duration_minutes,
                "rate_per_minute": Config.AVATAR_RATE_PER_MINUTE,
                "cost": duration_minutes * Config.AVATAR_RATE_PER_MINUTE
            },
            "total": 0.0
        }
        
        cost_breakdown["total"] = sum(item["cost"] for item in cost_breakdown.values() if isinstance(item, dict) and "cost" in item)
        
        # Generate summary using LLM
        summary_prompt = f"""Summarize this appointment booking conversation:

Transcript:
{full_transcript}

Tool Calls Made:
{json.dumps(state.tool_calls, indent=2)}

Appointments:
{json.dumps([format_appointment_summary(apt) for apt in appointments], indent=2)}

Create a structured summary including:
1. User information (name, phone if available)
2. Actions taken (bookings, cancellations, modifications)
3. Appointment details
4. Any preferences or special requests mentioned
5. Conversation duration: {duration_minutes:.1f} minutes

Format as a clean, readable summary."""

        try:
            if Config.LLM_PROVIDER == "openai":
                kwargs = {"api_key": Config.OPENAI_API_KEY}
                if Config.OPENAI_BASE_URL:
                    kwargs["base_url"] = Config.OPENAI_BASE_URL
                client = OpenAI(**kwargs)
            elif Config.LLM_PROVIDER == "openrouter":
                client = OpenAI(
                    api_key=Config.OPENROUTER_API_KEY,
                    base_url=Config.OPENROUTER_BASE_URL,
                    default_headers={
                        "HTTP-Referer": "https://github.com/your-repo",
                        "X-Title": "Voice Agent",
                    }
                )
            elif Config.LLM_PROVIDER == "together":
                client = OpenAI(api_key=Config.TOGETHER_API_KEY, base_url=Config.TOGETHER_BASE_URL)
            elif Config.LLM_PROVIDER == "ollama":
                client = OpenAI(api_key="ollama", base_url=Config.OLLAMA_BASE_URL)
            else:
                raise ValueError(f"Unsupported provider: {Config.LLM_PROVIDER}")
            
            summary_model = "gpt-4o-mini" if Config.LLM_PROVIDER == "openai" else Config.get_default_model()
            response = client.chat.completions.create(
                model=summary_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3
            )
            
            summary_text = response.choices[0].message.content
            if not summary_text or summary_text.strip() == "":
                raise ValueError("LLM returned empty summary")
        except Exception as e:
            logger.error(f"Error generating summary with LLM: {e}")
            # Fallback summary with actual data
            summary_text = f"""Conversation Summary

Duration: {duration_minutes:.1f} minutes

Tool Calls Made: {len(state.tool_calls)}
{chr(10).join([f"- {tc.get('tool_name', 'unknown')}: {tc.get('result', {}).get('message', 'completed')}" for tc in state.tool_calls[:5]])}

Appointments: {len(appointments)}
{chr(10).join([f"- {format_appointment_summary(apt)}" for apt in appointments[:3]])}

Transcript: {len(state.transcript)} messages exchanged"""
        
        # Ensure summary is not empty
        if not summary_text or summary_text.strip() == "":
            summary_text = "Conversation completed successfully."
        
        # Send summary via data channel
        if ctx.room and ctx.room.local_participant:
            event = {
                "type": "conversation_summary",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": summary_text,
                "appointments": appointments,
                "tool_calls": state.tool_calls,
                "cost_breakdown": cost_breakdown,
                "duration_minutes": duration_minutes,
                "transcript": state.transcript
            }
            await ctx.room.local_participant.publish_data(
                json.dumps(event).encode(),
                reliable=True
            )
        else:
            logger.warning("Cannot send summary - room or local_participant not available")
        
        return {
            "summary": summary_text,
            "appointments": appointments,
            "tool_calls": state.tool_calls,
            "cost_breakdown": cost_breakdown,
            "duration_minutes": duration_minutes,
            "transcript": state.transcript
        }
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {"summary": "Error generating summary", "error": str(e)}
