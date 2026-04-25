from datetime import date
from unittest.mock import MagicMock

import pytest

from adapters.mews.adapter import MewsAdapter
from adapters.mews.client import MewsClient
from domain.models import BookingData, ExtractionConfidence


CATEGORIES_RESPONSE = {
    "ResourceCategories": [
        {"Id": "cat-deluxe", "Names": {"en-US": "Deluxe Double"}},
        {"Id": "cat-suite", "Names": {"en-US": "Suite"}},
    ]
}

VOUCHERS_RESPONSE = {
    "Vouchers": [{"Id": "voucher-1"}],
    "VoucherAssignments": [{"VoucherId": "voucher-1", "RateId": "rate-1"}],
    "VoucherCodes": [],
}


@pytest.fixture
def client():
    return MagicMock(spec=MewsClient)


@pytest.fixture
def adapter(client):
    return MewsAdapter(client, service_id="svc-1")


@pytest.fixture
def booking():
    return BookingData(
        guest_name="John Smith",
        arrival_date=date(2026, 6, 1),
        departure_date=date(2026, 6, 5),
        room_category="Deluxe Double",
        num_guests=2,
        voucher_code="PROMO2026",
        agency_name="Best Travel Agency",
        guest_email="john@example.com",
        special_wishes=None,
        confidence=ExtractionConfidence.HIGH,
    )


def avail_response(category_id: str, counts: list[int]) -> dict:
    return {"CategoryAvailabilities": [{"CategoryId": category_id, "Availabilities": counts}]}


class TestCheckAvailability:
    def test_returns_true_when_all_nights_available(self, client, adapter, booking):
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE, avail_response("cat-deluxe", [3, 2, 2, 1])]
        assert adapter.check_availability(booking) is True

    def test_returns_false_when_one_night_sold_out(self, client, adapter, booking):
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE, avail_response("cat-deluxe", [3, 0, 2, 1])]
        assert adapter.check_availability(booking) is False

    def test_returns_false_when_category_unknown(self, client, adapter, booking):
        booking.room_category = "Unknown Room"
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE]
        assert adapter.check_availability(booking) is False

    def test_returns_false_when_category_not_in_availability_response(self, client, adapter, booking):
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE, {"CategoryAvailabilities": []}]
        assert adapter.check_availability(booking) is False

    def test_returns_false_when_no_voucher_code(self, client, adapter, booking):
        booking.voucher_code = None
        assert adapter.check_availability(booking) is False
        client.post.assert_not_called()

    def test_returns_false_for_unknown_voucher_code(self, client, adapter, booking):
        client.post.return_value = {"Vouchers": [], "VoucherAssignments": [], "VoucherCodes": []}
        assert adapter.check_availability(booking) is False

    def test_uses_services_getAvailability_endpoint(self, client, adapter, booking):
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE, avail_response("cat-deluxe", [2])]
        adapter.check_availability(booking)
        endpoints = [call.args[0] for call in client.post.call_args_list]
        assert "services/getAvailability" in endpoints

    def test_category_cache_prevents_repeated_lookup(self, client, adapter, booking):
        avail = avail_response("cat-deluxe", [2, 2])
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE, avail, avail]
        adapter.check_availability(booking)
        adapter.check_availability(booking)
        category_calls = [c for c in client.post.call_args_list if "resourceCategories" in c.args[0]]
        assert len(category_calls) == 1


class TestCreateBooking:
    def test_passes_resolved_category_id(self, client, adapter, booking):
        client.post.side_effect = [
            VOUCHERS_RESPONSE,
            CATEGORIES_RESPONSE,
            {"Id": "customer-1"},
            {"Reservations": [{"Id": "reservation-1"}]},
        ]
        adapter.create_booking(booking)
        reservation_payload = client.post.call_args_list[3].args[1]
        assert reservation_payload["Reservations"][0]["RequestedCategoryId"] == "cat-deluxe"

    def test_returns_reservation_id(self, client, adapter, booking):
        client.post.side_effect = [
            VOUCHERS_RESPONSE,
            CATEGORIES_RESPONSE,
            {"Id": "customer-1"},
            {"Reservations": [{"Id": "reservation-42"}]},
        ]
        assert adapter.create_booking(booking) == "reservation-42"

    def test_reservation_includes_voucher_code_and_rate_id(self, client, adapter, booking):
        client.post.side_effect = [
            VOUCHERS_RESPONSE,
            CATEGORIES_RESPONSE,
            {"Id": "customer-1"},
            {"Reservations": [{"Id": "reservation-1"}]},
        ]
        adapter.create_booking(booking)
        reservation = client.post.call_args_list[3].args[1]["Reservations"][0]
        assert reservation["VoucherCode"] == "PROMO2026"
        assert reservation["RateId"] == "rate-1"

    def test_raises_on_unknown_category(self, client, adapter, booking):
        booking.room_category = "Unknown Room"
        client.post.side_effect = [VOUCHERS_RESPONSE, CATEGORIES_RESPONSE]
        with pytest.raises(ValueError, match="Unknown room category"):
            adapter.create_booking(booking)

    def test_raises_on_unknown_voucher_code(self, client, adapter, booking):
        client.post.return_value = {"Vouchers": [], "VoucherAssignments": [], "VoucherCodes": []}
        with pytest.raises(ValueError, match="Unknown voucher code"):
            adapter.create_booking(booking)

    def test_splits_guest_name_into_first_and_last(self, client, adapter, booking):
        client.post.side_effect = [
            VOUCHERS_RESPONSE,
            CATEGORIES_RESPONSE,
            {"Id": "customer-1"},
            {"Reservations": [{"Id": "reservation-1"}]},
        ]
        adapter.create_booking(booking)
        customer_payload = client.post.call_args_list[2].args[1]
        assert customer_payload["FirstName"] == "John"
        assert customer_payload["LastName"] == "Smith"
