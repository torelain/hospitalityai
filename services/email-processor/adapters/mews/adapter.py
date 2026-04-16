from datetime import timezone

from ...domain.models import BookingData
from ...domain.ports import PMSPort
from .client import MewsClient


class MewsAdapter(PMSPort):
    def __init__(self, client: MewsClient, service_id: str, rate_id: str):
        self._client = client
        self._service_id = service_id
        self._rate_id = rate_id

    def check_availability(self, booking: BookingData) -> bool:
        response = self._client.post(
            "availabilityBlocks/getAll",
            {
                "ServiceIds": [self._service_id],
                "FirstTimeUnitStartUtc": booking.arrival_date.isoformat(),
                "LastTimeUnitStartUtc": booking.departure_date.isoformat(),
            },
        )
        # A non-empty availability blocks list means the room type is available
        return len(response.get("AvailabilityBlocks", [])) > 0

    def create_booking(self, booking: BookingData) -> str:
        customer_id = self._get_or_create_customer(booking)

        response = self._client.post(
            "reservations/add",
            {
                "ServiceId": self._service_id,
                "Reservations": [
                    {
                        "StartUtc": f"{booking.arrival_date.isoformat()}T14:00:00Z",
                        "EndUtc": f"{booking.departure_date.isoformat()}T11:00:00Z",
                        "AccountId": customer_id,
                        "RateId": self._rate_id,
                        "RequestedCategoryId": None,  # resolved from room_category name
                        "PersonCounts": [{"AgeCategoryId": None, "Count": booking.num_guests}],
                        "Notes": booking.special_wishes,
                    }
                ],
            },
        )
        return response["Reservations"][0]["Id"]

    def _get_or_create_customer(self, booking: BookingData) -> str:
        first_name, *rest = booking.guest_name.split(" ", 1)
        last_name = rest[0] if rest else ""

        response = self._client.post(
            "customers/add",
            {
                "FirstName": first_name,
                "LastName": last_name,
                "Email": booking.guest_email,
                "OverwriteExisting": False,
            },
        )
        return response["Id"]
