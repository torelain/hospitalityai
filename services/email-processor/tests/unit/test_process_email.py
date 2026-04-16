from datetime import date, datetime

import pytest

from domain.models import (
    BookingData,
    ExtractionConfidence,
    InboundEmail,
    Intent,
    ProcessingPath,
)
from domain.ports import EmailSenderPort, PMSPort
from domain.use_cases.process_email import (
    BookingExtractor,
    IntentClassifier,
    ProcessEmail,
)


def make_email(**kwargs) -> InboundEmail:
    defaults = dict(
        message_id="msg-1",
        from_email="agency@example.com",
        from_name="Best Travel Agency",
        to_email="hotel@example.com",
        subject="Booking Confirmation",
        text_body="We confirm a booking for John Smith...",
        received_at=datetime(2026, 4, 16, 10, 0, 0),
    )
    return InboundEmail(**{**defaults, **kwargs})


def make_booking(**kwargs) -> BookingData:
    defaults = dict(
        guest_name="John Smith",
        arrival_date=date(2026, 6, 1),
        departure_date=date(2026, 6, 5),
        room_category="Deluxe Double",
        num_guests=2,
        confidence=ExtractionConfidence.HIGH,
    )
    return BookingData(**{**defaults, **kwargs})


class StubClassifier(IntentClassifier):
    def __init__(self, intent: Intent):
        self._intent = intent

    def classify(self, email: InboundEmail) -> Intent:
        return self._intent


class StubExtractor(BookingExtractor):
    def __init__(self, booking: BookingData):
        self._booking = booking

    def extract(self, email: InboundEmail) -> BookingData:
        return self._booking


class StubPMS(PMSPort):
    def __init__(self, available: bool = True, reservation_id: str = "res-123"):
        self.available = available
        self.reservation_id = reservation_id
        self.created = False

    def check_availability(self, booking: BookingData) -> bool:
        return self.available

    def create_booking(self, booking: BookingData) -> str:
        self.created = True
        return self.reservation_id


class StubEmailSender(EmailSenderPort):
    def __init__(self):
        self.notifications = []

    def send_auto_booking_notification(self, result):
        self.notifications.append(("auto", result))

    def send_assisted_handoff(self, result):
        self.notifications.append(("assisted", result))

    def send_pass_through(self, result):
        self.notifications.append(("pass_through", result))


def make_use_case(classifier, extractor, pms=None, sender=None):
    return ProcessEmail(
        classifier=classifier,
        extractor=extractor,
        pms=pms or StubPMS(),
        email_sender=sender or StubEmailSender(),
    )


class TestPath1Automated:
    def test_creates_booking_when_high_confidence_and_available(self):
        pms = StubPMS(available=True, reservation_id="res-456")
        sender = StubEmailSender()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=pms,
            sender=sender,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.AUTOMATED
        assert result.mews_reservation_id == "res-456"
        assert pms.created is True
        assert sender.notifications[0][0] == "auto"


class TestPath2Assisted:
    def test_routes_to_assisted_when_low_confidence(self):
        sender = StubEmailSender()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.LOW)),
            sender=sender,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.ASSISTED
        assert sender.notifications[0][0] == "assisted"

    def test_routes_to_assisted_when_not_available(self):
        sender = StubEmailSender()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=StubPMS(available=False),
            sender=sender,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.ASSISTED
        assert sender.notifications[0][0] == "assisted"


class TestPath3PassThrough:
    def test_routes_unknown_intent_to_pass_through(self):
        sender = StubEmailSender()
        use_case = make_use_case(
            StubClassifier(Intent.UNKNOWN),
            StubExtractor(make_booking()),
            sender=sender,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.PASS_THROUGH
        assert sender.notifications[0][0] == "pass_through"

    def test_routes_to_pass_through_on_exception(self):
        class BrokenPMS(PMSPort):
            def check_availability(self, booking):
                raise RuntimeError("Mews down")

            def create_booking(self, booking):
                raise RuntimeError("Mews down")

        sender = StubEmailSender()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=BrokenPMS(),
            sender=sender,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.PASS_THROUGH
        assert result.failure_reason == "Mews down"
        assert sender.notifications[0][0] == "pass_through"
