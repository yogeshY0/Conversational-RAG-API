from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    booking_detected: bool = False


class IngestResponse(BaseModel):
    message: str
    chunks_stored: int


class BookingInfo(BaseModel):
    name: str
    email: EmailStr
    date: date
    time: time


class BookingResponse(BaseModel):
    session_id: str
    booking: BookingInfo


class AllBookingsResponse(BaseModel):
    bookings: list[BookingResponse]