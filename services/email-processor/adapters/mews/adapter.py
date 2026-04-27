from typing import Optional

from domain.models import BookingData
from domain.ports import PMSPort
from adapters.mews.client import MewsClient


class MewsAdapter(PMSPort):
    def __init__(self, client: MewsClient, service_id: str):
        self._client = client
        self._service_id = service_id
        self._category_cache: Optional[dict[str, str]] = None
        self._rate_cache: dict[str, str] = {}

    def check_availability(self, booking: BookingData) -> bool:
        if not booking.voucher_code:
            return False
        if self._resolve_rate_id(booking.voucher_code) is None:
            return False

        category_id = self._resolve_category_id(booking.room_category)
        if category_id is None:
            return False

        response = self._client.post(
            "services/getAvailability",
            {
                "ServiceId": self._service_id,
                "FirstTimeUnitStartUtc": f"{booking.arrival_date.isoformat()}T00:00:00Z",
                "LastTimeUnitStartUtc": f"{booking.departure_date.isoformat()}T00:00:00Z",
            },
        )
        for cat in response.get("CategoryAvailabilities", []):
            if cat["CategoryId"] == category_id:
                return all(count >= 1 for count in cat.get("Availabilities", [0]))
        return False

    def create_booking(self, booking: BookingData) -> str:
        if not booking.voucher_code:
            raise ValueError("Voucher code is required to create a booking")

        rate_id = self._resolve_rate_id(booking.voucher_code)
        if rate_id is None:
            raise ValueError(f"Unknown voucher code: {booking.voucher_code!r}")

        category_id = self._resolve_category_id(booking.room_category)
        if category_id is None:
            raise ValueError(f"Unknown room category: {booking.room_category!r}")

        customer_id = self._get_or_create_customer(booking)

        response = self._client.post(
            "reservations/add",
            {
                "ServiceId": self._service_id,
                "Reservations": [
                    {
                        "StartUtc": f"{booking.arrival_date.isoformat()}T14:00:00Z",
                        "EndUtc": f"{booking.departure_date.isoformat()}T11:00:00Z",
                        "CustomerId": customer_id,
                        "RateId": rate_id,
                        "VoucherCode": booking.voucher_code,
                        "RequestedCategoryId": category_id,
                        "PersonCounts": [{"Count": booking.num_guests}],
                        "Notes": booking.special_wishes,
                        "Number": booking.agency_reference,
                    }
                ],
            },
        )
        return response["Reservations"][0]["Id"]

    def _resolve_rate_id(self, voucher_code: str) -> Optional[str]:
        if voucher_code in self._rate_cache:
            return self._rate_cache[voucher_code]
        response = self._client.post(
            "vouchers/getAll",
            {
                "ServiceIds": [self._service_id],
                "VoucherCodeValues": [voucher_code],
                "Extent": {"VoucherAssignments": True},
            },
        )
        assignments = response.get("VoucherAssignments", [])
        if not assignments:
            return None
        rate_id = assignments[0]["RateId"]
        self._rate_cache[voucher_code] = rate_id
        return rate_id

    def _resolve_category_id(self, room_category_name: str) -> Optional[str]:
        if self._category_cache is None:
            response = self._client.post(
                "resourceCategories/getAll",
                {"ServiceIds": [self._service_id]},
            )
            self._category_cache = {
                cat["Names"].get("en-US", ""): cat["Id"]
                for cat in response.get("ResourceCategories", [])
            }
        return self._category_cache.get(room_category_name)

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
