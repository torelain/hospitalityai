from abc import ABC, abstractmethod
from typing import Optional

from .models import BookingData, InboundEmail, ProcessingResult


class PMSPort(ABC):
    @abstractmethod
    def check_availability(self, booking: BookingData) -> bool:
        """Returns True if the requested room/dates are available."""

    @abstractmethod
    def create_booking(self, booking: BookingData) -> str:
        """Creates a booking and returns the reservation ID."""


class EmailSenderPort(ABC):
    @abstractmethod
    def send_auto_booking_notification(self, result: ProcessingResult) -> None:
        """Notifies front desk that a booking was created automatically (Path 1)."""

    @abstractmethod
    def send_assisted_handoff(self, result: ProcessingResult) -> None:
        """Sends summary + original email to front desk for human decision (Path 2)."""

    @abstractmethod
    def send_pass_through(self, result: ProcessingResult) -> None:
        """Forwards original email to front desk unchanged (Path 3)."""
