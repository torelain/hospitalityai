"""
Integration tests for MewsAdapter against the local Mews mock server.

These tests exercise the full HTTP stack — request formatting, field names,
response parsing — using real API-shaped payloads captured from api.mews-demo.com.
"""
from datetime import date

import pytest

from domain.models import BookingData, ExtractionConfidence
from tests.mews_mock.server import LUXURY_CATEGORY_ID, STANDARD_CATEGORY_ID, VOUCHER_CODE


@pytest.fixture
def booking():
    return BookingData(
        guest_name="Jane Smith",
        arrival_date=date(2026, 9, 1),
        departure_date=date(2026, 9, 4),
        room_category="Standard",
        num_guests=2,
        voucher_code=VOUCHER_CODE,
        agency_name="Best Travel",
        guest_email="jane@example.com",
        special_wishes=None,
        confidence=ExtractionConfidence.HIGH,
    )


class TestCheckAvailability:
    def test_returns_true_when_rooms_available(self, mews_adapter, booking):
        assert mews_adapter.check_availability(booking) is True

    def test_returns_false_when_sold_out(self, mews_adapter, mock_state, booking):
        mock_state.set_availability(STANDARD_CATEGORY_ID, [0, 0, 0])
        assert mews_adapter.check_availability(booking) is False

    def test_returns_false_when_one_night_sold_out(self, mews_adapter, mock_state, booking):
        mock_state.set_availability(STANDARD_CATEGORY_ID, [5, 0, 5])
        assert mews_adapter.check_availability(booking) is False

    def test_returns_false_for_unknown_category(self, mews_adapter, booking):
        booking.room_category = "Presidential Suite"
        assert mews_adapter.check_availability(booking) is False

    def test_luxury_category_available(self, mews_adapter, booking):
        booking.room_category = "Luxury"
        assert mews_adapter.check_availability(booking) is True

    def test_luxury_category_sold_out(self, mews_adapter, mock_state, booking):
        booking.room_category = "Luxury"
        mock_state.set_availability(LUXURY_CATEGORY_ID, [0, 0, 0])
        assert mews_adapter.check_availability(booking) is False

    def test_returns_false_for_unknown_voucher_code(self, mews_adapter, booking):
        booking.voucher_code = "INVALID"
        assert mews_adapter.check_availability(booking) is False

    def test_returns_false_when_no_voucher_code(self, mews_adapter, booking):
        booking.voucher_code = None
        assert mews_adapter.check_availability(booking) is False


class TestCreateBooking:
    def test_returns_reservation_id(self, mews_adapter, booking):
        reservation_id = mews_adapter.create_booking(booking)
        assert reservation_id  # non-empty string UUID

    def test_creates_customer_with_split_name(self, mews_adapter, mock_state, booking):
        mews_adapter.create_booking(booking)
        assert len(mock_state.created_customers) == 1
        customer = mock_state.created_customers[0]
        assert customer["FirstName"] == "Jane"
        assert customer["LastName"] == "Smith"

    def test_creates_customer_with_email(self, mews_adapter, mock_state, booking):
        mews_adapter.create_booking(booking)
        assert mock_state.created_customers[0]["Email"] == "jane@example.com"

    def test_reservation_uses_resolved_category_id(self, mews_adapter, mock_state, booking):
        mews_adapter.create_booking(booking)
        reservation = mock_state.created_reservations[0]
        assert reservation["RequestedResourceCategoryId"] == STANDARD_CATEGORY_ID

    def test_reservation_includes_start_and_end(self, mews_adapter, mock_state, booking):
        mews_adapter.create_booking(booking)
        reservation = mock_state.created_reservations[0]
        assert reservation["ScheduledStartUtc"] == "2026-09-01T14:00:00Z"
        assert reservation["ScheduledEndUtc"] == "2026-09-04T11:00:00Z"

    def test_raises_for_unknown_category(self, mews_adapter, booking):
        booking.room_category = "Presidential Suite"
        with pytest.raises(ValueError, match="Unknown room category"):
            mews_adapter.create_booking(booking)

    def test_reservation_includes_voucher_code(self, mews_adapter, mock_state, booking):
        mews_adapter.create_booking(booking)
        assert mock_state.created_reservations[0]["VoucherCode"] == VOUCHER_CODE

    def test_category_resolved_only_once_across_calls(self, mews_adapter, mock_state, booking):
        mews_adapter.create_booking(booking)
        mews_adapter.create_booking(booking)
        category_calls = [
            r for r in mock_state.created_reservations
        ]
        # Two reservations but categories only fetched once (adapter caches)
        assert len(category_calls) == 2
        assert len(mock_state.created_customers) == 2
