"""Helper functions for the voice agent."""
import re
from datetime import date, time, datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (10 digits)."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    return len(digits_only) == 10


def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to 10 digits."""
    digits_only = re.sub(r'\D', '', phone)
    if len(digits_only) == 10:
        return digits_only
    return phone


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string in various formats."""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    # Try relative dates
    today = date.today()
    date_lower = date_str.lower().strip()
    
    if "today" in date_lower:
        return today
    elif "tomorrow" in date_lower:
        return today + timedelta(days=1)
    elif "day after tomorrow" in date_lower:
        return today + timedelta(days=2)
    
    logger.warning(f"Could not parse date: {date_str}")
    return None


def parse_time(time_str: str) -> Optional[time]:
    """Parse time string in various formats."""
    if not time_str:
        return None
    
    # Common time formats
    formats = [
        "%H:%M",
        "%I:%M %p",
        "%I %p",
        "%H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(time_str.strip(), fmt).time()
            return parsed
        except ValueError:
            continue
    
    # Try relative times
    time_lower = time_str.lower().strip()
    
    time_mappings = {
        "morning": time(9, 0),
        "afternoon": time(14, 0),
        "evening": time(17, 0),
        "noon": time(12, 0),
        "midnight": time(0, 0),
    }
    
    for key, value in time_mappings.items():
        if key in time_lower:
            return value
    
    logger.warning(f"Could not parse time: {time_str}")
    return None


def generate_available_slots(
    start_date: date,
    days_ahead: int = 7,
    start_hour: int = 9,
    end_hour: int = 17,
    booked_slots: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """Generate available time slots."""
    slots = []
    booked_slots = booked_slots or []
    
    # Create a set of booked slots for quick lookup
    booked_set = set()
    for slot in booked_slots:
        slot_date = slot.get("appointment_date")
        slot_time = slot.get("appointment_time")
        if slot_date and slot_time:
            booked_set.add((slot_date, slot_time))
    
    current_date = start_date
    for day_offset in range(days_ahead):
        # Use timedelta to properly handle month/year rollovers
        check_date = current_date + timedelta(days=day_offset)
        
        for hour in range(start_hour, end_hour):
            slot_time = time(hour, 0)
            slot_date_str = check_date.isoformat()
            slot_time_str = slot_time.isoformat()
            
            # Check if slot is booked
            if (slot_date_str, slot_time_str) not in booked_set:
                slots.append({
                    "date": slot_date_str,
                    "time": slot_time_str,
                    "display": f"{check_date.strftime('%B %d, %Y')} at {slot_time.strftime('%I:%M %p')}"
                })
    
    return slots


def format_appointment_summary(appointment: Dict[str, Any]) -> str:
    """Format appointment for display."""
    apt_date = appointment.get("appointment_date", "")
    apt_time = appointment.get("appointment_time", "")
    user_name = appointment.get("user_name", "Guest")
    notes = appointment.get("notes", "")
    
    try:
        # Parse date
        date_obj = None
        if apt_date:
            if isinstance(apt_date, str):
                date_obj = date.fromisoformat(apt_date)
            elif hasattr(apt_date, 'isoformat'):
                date_obj = apt_date
        
        # Parse time - handle time strings (HH:MM:SS) from database
        time_obj = None
        if apt_time:
            if isinstance(apt_time, str):
                # Try parsing as time string first (HH:MM:SS or HH:MM)
                # Database stores time.isoformat() which returns "HH:MM:SS"
                try:
                    parts = apt_time.split(':')
                    if len(parts) >= 2 and len(parts) <= 3:
                        # Time string format: "HH:MM" or "HH:MM:SS"
                        hour = int(parts[0])
                        minute = int(parts[1])
                        second = int(parts[2]) if len(parts) > 2 else 0
                        time_obj = time(hour, minute, second)
                    else:
                        # Try parsing as datetime ISO format (fallback)
                        time_obj = datetime.fromisoformat(apt_time).time()
                except (ValueError, IndexError, AttributeError):
                    # If parsing as time string fails, try as datetime ISO string
                    try:
                        time_obj = datetime.fromisoformat(apt_time).time()
                    except ValueError:
                        pass
            elif isinstance(apt_time, time):
                # Already a time object
                time_obj = apt_time
            elif hasattr(apt_time, 'time'):
                # datetime object
                time_obj = apt_time.time()
        
        date_str = date_obj.strftime("%B %d, %Y") if date_obj else apt_date
        time_str = time_obj.strftime("%I:%M %p") if time_obj else apt_time
        
        summary = f"{date_str} at {time_str}"
        if user_name:
            summary = f"{user_name}: {summary}"
        if notes:
            summary += f" (Notes: {notes})"
        
        return summary
    except Exception as e:
        logger.error(f"Error formatting appointment: {e}")
        return str(appointment)
