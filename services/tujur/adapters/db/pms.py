import uuid

from domain.models import BookingData
from domain.ports import PMSPort


class FakePMS(PMSPort):
    """PoC-stand-in for Mews. Always reports availability and emits a fake reservation id.

    Real availability + booking creation is deferred until the pilot hotel grants Mews
    Connector API access; until then we only validate the email → BookingData mapping.
    """

    def check_availability(self, booking: BookingData) -> bool:
        return True

    def create_booking(self, booking: BookingData) -> str:
        return f"poc-{uuid.uuid4()}"
