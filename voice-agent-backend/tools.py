"""Tool definitions for the voice agent."""
from typing import Dict, Any, List, Optional
from datetime import date, time
from database import Database
from utils import (
    validate_phone_number,
    normalize_phone_number,
    parse_date,
    parse_time,
    generate_available_slots,
    format_appointment_summary
)
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
db = Database()


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get all tool definitions in OpenAI function calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": "identify_user",
                "description": "Ask user for their phone number to identify them. Use this early in the conversation to get the user's contact information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_number": {
                            "type": "string",
                            "description": "10-digit phone number provided by the user"
                        }
                    },
                    "required": ["contact_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_slots",
                "description": "Fetch available appointment slots. Returns a list of available time slots for the next 7 days (9 AM to 5 PM, hourly slots). Excludes already booked slots.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "book_appointment",
                "description": "Book a new appointment. Must check for conflicts before booking. Returns success/failure with confirmation details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_number": {
                            "type": "string",
                            "description": "10-digit phone number of the user"
                        },
                        "user_name": {
                            "type": "string",
                            "description": "Name of the user (optional)"
                        },
                        "appointment_date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format"
                        },
                        "appointment_time": {
                            "type": "string",
                            "description": "Time in HH:MM format (24-hour)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes or special requests (optional)"
                        }
                    },
                    "required": ["contact_number", "appointment_date", "appointment_time"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "retrieve_appointments",
                "description": "Retrieve all appointments for a given contact number. Returns appointments sorted by date (upcoming first).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_number": {
                            "type": "string",
                            "description": "10-digit phone number of the user"
                        }
                    },
                    "required": ["contact_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cancel_appointment",
                "description": "Cancel an existing appointment. Verifies ownership before cancelling.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": "UUID of the appointment to cancel"
                        },
                        "contact_number": {
                            "type": "string",
                            "description": "10-digit phone number to verify ownership"
                        }
                    },
                    "required": ["appointment_id", "contact_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "modify_appointment",
                "description": "Modify an existing appointment (change date or time). Verifies ownership and checks for conflicts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": "UUID of the appointment to modify"
                        },
                        "new_date": {
                            "type": "string",
                            "description": "New date in YYYY-MM-DD format (optional)"
                        },
                        "new_time": {
                            "type": "string",
                            "description": "New time in HH:MM format (optional)"
                        },
                        "contact_number": {
                            "type": "string",
                            "description": "10-digit phone number to verify ownership"
                        }
                    },
                    "required": ["appointment_id", "contact_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "end_conversation",
                "description": "End the conversation gracefully. Use this when the user wants to finish the call or has completed their task. This will generate a summary and end the session.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]


def execute_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    conversation_state: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a tool and return the result."""
    try:
        if tool_name == "identify_user":
            contact_number = parameters.get("contact_number", "")
            normalized = normalize_phone_number(contact_number)
            
            if not validate_phone_number(normalized):
                return {
                    "success": False,
                    "error": "Invalid phone number format. Please provide a 10-digit phone number."
                }
            
            conversation_state["contact_number"] = normalized
            conversation_state["user_identified"] = True
            
            return {
                "success": True,
                "message": f"Thank you! I've identified you with phone number {normalized}.",
                "contact_number": normalized
            }
        
        elif tool_name == "fetch_slots":
            booked_slots = db.get_all_booked_slots()
            available_slots = generate_available_slots(
                start_date=date.today(),
                days_ahead=7,
                booked_slots=booked_slots
            )
            
            return {
                "success": True,
                "slots": available_slots,
                "count": len(available_slots)
            }
        
        elif tool_name == "book_appointment":
            contact_number = parameters.get("contact_number", "")
            normalized = normalize_phone_number(contact_number)
            
            if not validate_phone_number(normalized):
                return {
                    "success": False,
                    "error": "Invalid phone number format."
                }
            
            date_str = parameters.get("appointment_date", "")
            time_str = parameters.get("appointment_time", "")
            user_name = parameters.get("user_name")
            notes = parameters.get("notes")
            
            # Parse date and time
            apt_date = parse_date(date_str) if date_str else None
            apt_time = parse_time(time_str) if time_str else None
            
            if not apt_date or not apt_time:
                return {
                    "success": False,
                    "error": f"Could not parse date/time. Date: {date_str}, Time: {time_str}"
                }
            
            # Check availability
            if not db.check_slot_available(apt_date, apt_time):
                return {
                    "success": False,
                    "error": f"The slot on {apt_date} at {apt_time} is already booked. Please choose another time."
                }
            
            # Create appointment
            appointment = db.create_appointment(
                contact_number=normalized,
                user_name=user_name,
                date=apt_date,
                time=apt_time,
                notes=notes
            )
            
            conversation_state["contact_number"] = normalized
            if user_name:
                conversation_state["user_name"] = user_name
            
            return {
                "success": True,
                "message": f"Appointment booked successfully!",
                "appointment": appointment,
                "summary": format_appointment_summary(appointment)
            }
        
        elif tool_name == "retrieve_appointments":
            contact_number = parameters.get("contact_number", "")
            normalized = normalize_phone_number(contact_number)
            
            if not validate_phone_number(normalized):
                return {
                    "success": False,
                    "error": "Invalid phone number format."
                }
            
            appointments = db.get_appointments(normalized, include_cancelled=False)
            
            return {
                "success": True,
                "appointments": appointments,
                "count": len(appointments),
                "formatted": [format_appointment_summary(apt) for apt in appointments]
            }
        
        elif tool_name == "cancel_appointment":
            appointment_id = parameters.get("appointment_id", "")
            contact_number = parameters.get("contact_number", "")
            normalized = normalize_phone_number(contact_number)
            
            if not validate_phone_number(normalized):
                return {
                    "success": False,
                    "error": "Invalid phone number format."
                }
            
            success = db.cancel_appointment(appointment_id, normalized)
            
            if success:
                return {
                    "success": True,
                    "message": f"Appointment {appointment_id} has been cancelled successfully."
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to cancel appointment. It may not exist or you may not have permission."
                }
        
        elif tool_name == "modify_appointment":
            appointment_id = parameters.get("appointment_id", "")
            contact_number = parameters.get("contact_number", "")
            normalized = normalize_phone_number(contact_number)
            
            if not validate_phone_number(normalized):
                return {
                    "success": False,
                    "error": "Invalid phone number format."
                }
            
            new_date_str = parameters.get("new_date")
            new_time_str = parameters.get("new_time")
            
            new_date = parse_date(new_date_str) if new_date_str else None
            new_time = parse_time(new_time_str) if new_time_str else None
            
            updated = db.modify_appointment(
                appointment_id=appointment_id,
                contact_number=normalized,
                new_date=new_date,
                new_time=new_time
            )
            
            if updated:
                return {
                    "success": True,
                    "message": "Appointment modified successfully!",
                    "appointment": updated,
                    "summary": format_appointment_summary(updated)
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to modify appointment. The new slot may be unavailable, or you may not have permission."
                }
        
        elif tool_name == "end_conversation":
            conversation_state["should_end"] = True
            return {
                "success": True,
                "message": "Conversation ending. Generating summary..."
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }
