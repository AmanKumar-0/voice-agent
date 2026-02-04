"""Supabase database operations for appointment management."""
from datetime import date, time, datetime
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from config import Config
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database operations for appointments."""
    
    def __init__(self):
        """Initialize Supabase client."""
        print(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table = "appointments"
    
    def create_appointment(
        self,
        contact_number: str,
        user_name: Optional[str],
        date: date,
        time: time,
        notes: Optional[str] = None,
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Create a new appointment."""
        try:
            appointment_data = {
                "contact_number": contact_number,
                "user_name": user_name,
                "appointment_date": date.isoformat(),
                "appointment_time": time.isoformat(),
                "duration_minutes": duration_minutes,
                "status": "confirmed",
                "notes": notes,
            }
            
            result = self.client.table(self.table).insert(appointment_data).execute()
            
            if result.data:
                logger.info(f"Created appointment: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create appointment: no data returned")
                
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise
    
    def get_appointments(
        self,
        contact_number: str,
        include_cancelled: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all appointments for a contact number."""
        try:
            query = self.client.table(self.table).select("*").eq("contact_number", contact_number)
            
            if not include_cancelled:
                query = query.neq("status", "cancelled")
            
            result = query.order("appointment_date", desc=False).order("appointment_time", desc=False).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching appointments: {e}")
            return []
    
    def check_slot_available(self, date: date, time: time, duration_minutes: int = 30) -> bool:
        """Check if a time slot is available."""
        try:
            appointment_time = datetime.combine(date, time)
            end_time = appointment_time.replace(
                minute=appointment_time.minute + duration_minutes
            )
            
            # Check for overlapping appointments
            result = self.client.table(self.table).select("*").eq(
                "appointment_date", date.isoformat()
            ).neq("status", "cancelled").execute()
            
            if not result.data:
                return True
            
            for appointment in result.data:
                apt_date = datetime.fromisoformat(appointment["appointment_date"])
                apt_time = datetime.fromisoformat(appointment["appointment_time"]).time()
                apt_datetime = datetime.combine(apt_date, apt_time)
                apt_duration = appointment.get("duration_minutes", 30)
                apt_end = apt_datetime.replace(minute=apt_datetime.minute + apt_duration)
                
                # Check for overlap
                if (appointment_time < apt_end and end_time > apt_datetime):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking slot availability: {e}")
            return False
    
    def cancel_appointment(self, appointment_id: str, contact_number: str) -> bool:
        """Cancel an appointment (verify ownership first)."""
        try:
            # Verify ownership
            result = self.client.table(self.table).select("*").eq(
                "id", appointment_id
            ).eq("contact_number", contact_number).execute()
            
            if not result.data:
                logger.warning(f"Appointment {appointment_id} not found or not owned by {contact_number}")
                return False
            
            # Update status
            update_result = self.client.table(self.table).update({
                "status": "cancelled",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", appointment_id).execute()
            
            return bool(update_result.data)
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False
    
    def modify_appointment(
        self,
        appointment_id: str,
        contact_number: str,
        new_date: Optional[date] = None,
        new_time: Optional[time] = None
    ) -> Optional[Dict[str, Any]]:
        """Modify an appointment."""
        try:
            # Verify ownership
            result = self.client.table(self.table).select("*").eq(
                "id", appointment_id
            ).eq("contact_number", contact_number).execute()
            
            if not result.data:
                logger.warning(f"Appointment {appointment_id} not found or not owned by {contact_number}")
                return None
            
            current_appointment = result.data[0]
            
            # Use existing values if not provided
            final_date = new_date if new_date else date.fromisoformat(current_appointment["appointment_date"])
            final_time = new_time if new_time else datetime.fromisoformat(current_appointment["appointment_time"]).time()
            
            # Check if new slot is available
            duration = current_appointment.get("duration_minutes", 30)
            if not self.check_slot_available(final_date, final_time, duration):
                logger.warning(f"Slot {final_date} {final_time} is not available")
                return None
            
            # Update appointment
            update_data = {
                "appointment_date": final_date.isoformat(),
                "appointment_time": final_time.isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "confirmed"
            }
            
            update_result = self.client.table(self.table).update(
                update_data
            ).eq("id", appointment_id).execute()
            
            return update_result.data[0] if update_result.data else None
            
        except Exception as e:
            logger.error(f"Error modifying appointment: {e}")
            return None
    
    def get_all_booked_slots(self) -> List[Dict[str, Any]]:
        """Get all booked slots (for availability checking)."""
        try:
            result = self.client.table(self.table).select(
                "appointment_date, appointment_time, duration_minutes"
            ).neq("status", "cancelled").execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching booked slots: {e}")
            return []
