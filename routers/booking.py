from fastapi import APIRouter
from db.redis_client import get_all_bookings
from models.schemas import AllBookingsResponse, BookingResponse, BookingInfo
from datetime import datetime

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def parse_time(time_str: str) -> str:
    """Convert time strings like '10:00 AM' to '10:00' (HH:MM)."""
    time_str = time_str.strip()
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(time_str, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return time_str


@router.get("", response_model=AllBookingsResponse)
async def list_bookings() -> AllBookingsResponse:
    """
    Retrieve all interview bookings stored in Redis.
    """
    raw_bookings = get_all_bookings()

    bookings = []
    for item in raw_bookings:
        try:
            booking_data = item["booking"]
            booking_info = BookingInfo(
                name=booking_data["name"],
                email=booking_data["email"],
                date=booking_data["date"],
                time=parse_time(booking_data["time"]),
            )
            bookings.append(
                BookingResponse(
                    session_id=item["session_id"],
                    booking=booking_info,
                )
            )
        except Exception as e:
            print(f"Skipping malformed booking: {e}")
            continue

    return AllBookingsResponse(bookings=bookings)