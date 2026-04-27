from abc import ABC, abstractmethod

from .models import BookingData, ProcessingResult


class PMSPort(ABC):
    @abstractmethod
    def check_availability(self, booking: BookingData) -> bool:
        """Returns True if the requested room/dates are available."""

    @abstractmethod
    def create_booking(self, booking: BookingData) -> str:
        """Creates a booking and returns the reservation ID."""


class BookingLedgerPort(ABC):
    @abstractmethod
    def persist(self, result: ProcessingResult) -> None:
        """Persists the full ProcessingResult — email, extraction, path, outcome — for audit and review."""
