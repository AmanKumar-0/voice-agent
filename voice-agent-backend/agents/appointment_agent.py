"""Appointment booking agent implementation."""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from livekit.agents import Agent, function_tool, RunContext
from livekit import rtc

from models.conversation_state import ConversationState
from database import Database
from utils import format_appointment_summary
from config import Config

logger = logging.getLogger(__name__)
db = Database()


class AppointmentAgent(Agent):
    """Appointment booking agent with tools."""
    
    def __init__(self, state: ConversationState, ctx=None):
        super().__init__(
            instructions="""You are a friendly and professional appointment booking assistant. Your role is to help users book, modify, and manage appointments through natural conversation.

IMPORTANT - SCOPE LIMITATIONS:
You are ONLY designed to handle appointment-related tasks. You MUST politely decline and redirect any requests that are outside this scope, such as:
- General questions or conversations unrelated to appointments
- Requests for information about other services or products
- Technical support or troubleshooting
- Personal advice or recommendations
- Any task that cannot be accomplished using your available tools

When declining out-of-scope requests:
1. Politely explain that you're specifically designed for appointment management
2. Apologize that you can't help with that particular request
3. Immediately redirect the conversation back to appointment-related tasks
4. Offer to help with booking, viewing, modifying, or canceling appointments

Example response for out-of-scope requests:
"I'm sorry, but I'm specifically designed to help with appointment booking and management. I can't assist with [their request]. However, I'd be happy to help you book an appointment, check your existing appointments, or modify a booking. What would you like to do?"

Key guidelines:
1. Be conversational, warm, and helpful. Speak naturally as if you're talking to a friend.
2. Early in the conversation, ask for the user's phone number to identify them. Use the identify_user tool.
3. When booking appointments:
   - Confirm all details (date, time, name) before booking
   - Use the fetch_slots tool to show available times if needed
   - Always verify the appointment details with the user before confirming
4. Handle ambiguous requests by asking clarifying questions (e.g., "What time would work best for you?")
5. **CRITICAL - ENDING CONVERSATIONS**: When a user indicates they want to end the conversation (phrases like "I'm done", "I'm finished", "that's all", "goodbye", "end the call", "I've completed my task", "let's go off", "I think I'm done"), you MUST immediately call the end_conversation tool. Do NOT just respond with a farewell message - you MUST use the tool. This is required for proper conversation cleanup and summary generation.
6. Keep responses concise but friendly. Don't be overly verbose.
7. If a tool call fails, explain the error to the user in simple terms and suggest alternatives.
8. ALWAYS stay within your scope - only handle appointment-related tasks and redirect out-of-scope requests.

Current conversation state:
- User identified: {user_identified}
- Contact number: {contact_number}
""".format(
                user_identified=state.user_identified,
                contact_number=state.contact_number or "Not provided"
            ),
        )
        self.state = state
        self.ctx = ctx
    
    async def _send_tool_call_event(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """Helper to send tool call events to frontend."""
        try:
            if self.ctx and self.ctx.room and self.ctx.room.local_participant:
                await self.ctx.room.local_participant.publish_data(
                    json.dumps({
                        "type": "tool_call",
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "status": "success" if result.get("success") else "error",
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    }).encode(),
                    reliable=True
                )
        except Exception as e:
            logger.error(f"Error sending tool call event: {e}")
    
    @function_tool
    async def identify_user(self, context: RunContext, contact_number: str):
        """Ask user for their phone number to identify them. Use this early in the conversation.
        
        Args:
            contact_number: 10-digit phone number provided by the user (can include spaces, dashes, or parentheses)
        
        Returns:
            Confirmation message with the normalized phone number
        """
        from utils import validate_phone_number, normalize_phone_number
        
        normalized = normalize_phone_number(contact_number)
        if not validate_phone_number(normalized):
            return "Invalid phone number format. Please provide a 10-digit phone number."
        
        self.state.contact_number = normalized
        self.state.user_identified = True
        
        await self._send_tool_call_event("identify_user", {"contact_number": normalized}, {"success": True, "contact_number": normalized})
        return f"Thank you! I've identified you with phone number {normalized}."
    
    @function_tool
    async def fetch_slots(self, context: RunContext):
        """Fetch available appointment slots. Returns a list of available time slots for the next 7 days (9 AM to 5 PM, hourly slots).
        
        Returns:
            List of available appointment slots with dates, times, and display text
        """
        from utils import generate_available_slots
        from datetime import date
        
        booked_slots = db.get_all_booked_slots()
        available_slots = generate_available_slots(
            start_date=date.today(),
            days_ahead=7,
            booked_slots=booked_slots
        )
        
        result = {
            "success": True,
            "slots": available_slots,
            "count": len(available_slots)
        }
        
        await self._send_tool_call_event("fetch_slots", {}, result)
        
        if not available_slots:
            return "No available slots found for the next 7 days."
        
        slots_text = "\n".join([f"- {slot['display']}" for slot in available_slots[:10]])
        return f"Available slots:\n{slots_text}\n(Showing first 10 of {len(available_slots)} total slots)"
    
    @function_tool
    async def book_appointment(
        self,
        context: RunContext,
        contact_number: str,
        appointment_date: str,
        appointment_time: str,
        user_name: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Book a new appointment. Must check for conflicts before booking.
        
        Args:
            contact_number: 10-digit phone number of the user (required)
            appointment_date: Date in YYYY-MM-DD format or relative terms like "tomorrow", "next Monday" (required)
            appointment_time: Time in HH:MM format (24-hour) or relative terms like "2pm", "morning" (required)
            user_name: Name of the user (optional)
            notes: Additional notes or special requests (optional)
        
        Returns:
            Confirmation message with appointment details, or error message if booking fails
        """
        from utils import validate_phone_number, normalize_phone_number, parse_date, parse_time
        
        normalized = normalize_phone_number(contact_number)
        if not validate_phone_number(normalized):
            return "Invalid phone number format."
        
        apt_date = parse_date(appointment_date)
        apt_time = parse_time(appointment_time)
        
        if not apt_date or not apt_time:
            return f"Could not parse date/time. Date: {appointment_date}, Time: {appointment_time}"
        
        if not db.check_slot_available(apt_date, apt_time):
            return f"The slot on {apt_date} at {apt_time} is already booked. Please choose another time."
        
        appointment = db.create_appointment(
            contact_number=normalized,
            user_name=user_name,
            date=apt_date,
            time=apt_time,
            notes=notes
        )
        
        self.state.contact_number = normalized
        if user_name:
            self.state.user_name = user_name
        
        await self._send_tool_call_event(
            "book_appointment",
            {
                "contact_number": normalized,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            },
            {"success": True, "appointment": appointment, "summary": format_appointment_summary(appointment)}
        )
        
        return f"Appointment booked successfully! {format_appointment_summary(appointment)}"
    
    @function_tool
    async def retrieve_appointments(self, context: RunContext, contact_number: str):
        """Retrieve all appointments for a given contact number. Returns appointments sorted by date (upcoming first).
        
        Args:
            contact_number: 10-digit phone number of the user (required)
        
        Returns:
            List of user's appointments with dates, times, and details
        """
        from utils import validate_phone_number, normalize_phone_number
        
        normalized = normalize_phone_number(contact_number)
        if not validate_phone_number(normalized):
            return "Invalid phone number format."
        
        appointments = db.get_appointments(normalized, include_cancelled=False)
        
        result = {
            "success": True,
            "appointments": appointments,
            "count": len(appointments)
        }
        
        await self._send_tool_call_event("retrieve_appointments", {"contact_number": normalized}, result)
        
        if not appointments:
            return "No appointments found for this phone number."
        
        appointments_text = "\n".join([format_appointment_summary(apt) for apt in appointments])
        return f"Your appointments:\n{appointments_text}"
    
    @function_tool
    async def cancel_appointment(self, context: RunContext, appointment_id: str, contact_number: str):
        """Cancel an existing appointment. Verifies ownership before cancelling.
        
        Args:
            appointment_id: UUID of the appointment to cancel (required)
            contact_number: 10-digit phone number to verify ownership (required)
        
        Returns:
            Confirmation message if successful, or error message if cancellation fails
        """
        from utils import validate_phone_number, normalize_phone_number
        
        normalized = normalize_phone_number(contact_number)
        if not validate_phone_number(normalized):
            return "Invalid phone number format."
        
        success = db.cancel_appointment(appointment_id, normalized)
        
        result = {"success": success}
        await self._send_tool_call_event(
            "cancel_appointment",
            {"appointment_id": appointment_id, "contact_number": normalized},
            result
        )
        
        if success:
            return f"Appointment {appointment_id} has been cancelled successfully."
        else:
            return "Failed to cancel appointment. It may not exist or you may not have permission."
    
    @function_tool
    async def modify_appointment(
        self,
        context: RunContext,
        appointment_id: str,
        contact_number: str,
        new_date: Optional[str] = None,
        new_time: Optional[str] = None
    ):
        """Modify an existing appointment (change date or time). Verifies ownership and checks for conflicts.
        
        Args:
            appointment_id: UUID of the appointment to modify (required)
            contact_number: 10-digit phone number to verify ownership (required)
            new_date: New date in YYYY-MM-DD format or relative terms like "tomorrow" (optional)
            new_time: New time in HH:MM format (24-hour) or relative terms like "2pm" (optional)
        
        Returns:
            Confirmation message with updated appointment details, or error message if modification fails
        """
        from utils import validate_phone_number, normalize_phone_number, parse_date, parse_time
        
        normalized = normalize_phone_number(contact_number)
        if not validate_phone_number(normalized):
            return "Invalid phone number format."
        
        new_date_obj = parse_date(new_date) if new_date else None
        new_time_obj = parse_time(new_time) if new_time else None
        
        updated = db.modify_appointment(
            appointment_id=appointment_id,
            contact_number=normalized,
            new_date=new_date_obj,
            new_time=new_time_obj
        )
        
        result = {
            "success": updated is not None,
            "appointment": updated
        }
        await self._send_tool_call_event(
            "modify_appointment",
            {"appointment_id": appointment_id, "contact_number": normalized, "new_date": new_date, "new_time": new_time},
            result
        )
        
        if updated:
            return f"Appointment modified successfully! {format_appointment_summary(updated)}"
        else:
            return "Failed to modify appointment. The new slot may be unavailable, or you may not have permission."
    
    @function_tool
    async def end_conversation(self, context: RunContext):
        """End the conversation gracefully. ALWAYS use this tool when the user indicates they want to end the call, finish the conversation, or are done with their task.
        
        Use this tool when the user says things like:
        - "I'm done" / "I'm finished" / "I've completed my task"
        - "Let's end the conversation" / "End the call" / "Goodbye"
        - "That's all" / "Nothing else" / "I'm all set"
        - "Thank you, that's everything" / "I'm good, thanks"
        - Any indication they want to finish or wrap up
        
        This is a REQUIRED tool call - do not just say goodbye conversationally. You MUST call this tool to properly end the conversation.
        
        Args:
            No parameters required.
        
        Returns:
            Farewell message confirming the conversation is ending
        """
        self.state.should_end = True
        await self._send_tool_call_event("end_conversation", {}, {"success": True})
        return "Conversation ending. Thank you for using our appointment booking service!"
