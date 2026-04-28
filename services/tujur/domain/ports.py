from abc import ABC, abstractmethod

from .models import BookingData, ProcessingResult


class PMSPort(ABC):
    @abstractmethod
    def check_availability(self, booking: BookingData) -> bool:
        """Returns True if the requested room/dates are available."""

    # Q: I think we can add additional methods to this port in iteration 2. One to get all the available room categories
    # :  and one to fetch the available voucher codes and rates.
    @abstractmethod
    def create_booking(self, booking: BookingData) -> str:
        """Creates a booking and returns the reservation ID."""


class BookingLedgerPort(ABC):
    # TODO: Lets add another port here and extract the existing bookings for the last week.
    # : and write them to the local storage of the server we are running on in /tmp/matchings.json
    @abstractmethod
    def persist(self, result: ProcessingResult) -> None:
        """Persists the full ProcessingResult — email, extraction, path, outcome — for audit and review."""

    @abstractmethod
    def has_processed(self, message_id: str) -> bool:
        """Returns True if a message with this id has already been processed for this hotel.
        Used to short-circuit duplicate Graph notifications (at-least-once delivery)."""
