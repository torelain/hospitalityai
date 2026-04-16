from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class Intent(Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    UNKNOWN = "unknown"


class ExtractionConfidence(Enum):
    HIGH = "high"
    LOW = "low"


class ProcessingPath(Enum):
    AUTOMATED = "automated"       # Path 1 — booked automatically
    ASSISTED = "assisted"         # Path 2 — low confidence, sent to front desk
    PASS_THROUGH = "pass_through" # Path 3 — unknown intent or system failure


@dataclass
class InboundEmail:
    message_id: str
    from_email: str
    from_name: str
    to_email: str
    subject: str
    text_body: str
    received_at: datetime


@dataclass
class BookingData:
    guest_name: str
    arrival_date: date
    departure_date: date
    room_category: str
    num_guests: int
    agency_name: Optional[str] = None
    guest_email: Optional[str] = None
    special_wishes: Optional[str] = None
    confidence: ExtractionConfidence = ExtractionConfidence.LOW


@dataclass
class ProcessingResult:
    path: ProcessingPath
    email: InboundEmail
    booking_data: Optional[BookingData] = None
    mews_reservation_id: Optional[str] = None
    failure_reason: Optional[str] = None
