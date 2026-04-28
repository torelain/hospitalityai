from datetime import date, datetime

from domain.models import (
    BookingData,
    ExtractionConfidence,
    InboundEmail,
    Intent,
    ProcessingPath,
    ProcessingResult,
)
from domain.ports import BookingLedgerPort, PMSPort
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


class StubLedger(BookingLedgerPort):
    def __init__(self, seen_message_ids: set[str] | None = None):
        self.persisted: list[ProcessingResult] = []
        self._seen = seen_message_ids or set()

    def persist(self, result: ProcessingResult) -> None:
        self.persisted.append(result)

    def has_processed(self, message_id: str) -> bool:
        return message_id in self._seen


def make_use_case(classifier, extractor, pms=None, ledger=None):
    return ProcessEmail(
        classifier=classifier,
        extractor=extractor,
        pms=pms or StubPMS(),
        ledger=ledger or StubLedger(),
    )


class TestPath1Automated:
    def test_creates_booking_when_high_confidence_and_available(self):
        pms = StubPMS(available=True, reservation_id="res-456")
        ledger = StubLedger()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=pms,
            ledger=ledger,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.AUTOMATED
        assert result.mews_reservation_id == "res-456"
        assert pms.created is True
        assert ledger.persisted[0].path == ProcessingPath.AUTOMATED


class TestPath2Assisted:
    def test_routes_to_assisted_when_low_confidence(self):
        ledger = StubLedger()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.LOW)),
            ledger=ledger,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.ASSISTED
        assert ledger.persisted[0].path == ProcessingPath.ASSISTED

    def test_routes_to_assisted_when_not_available(self):
        ledger = StubLedger()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=StubPMS(available=False),
            ledger=ledger,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.ASSISTED
        assert ledger.persisted[0].path == ProcessingPath.ASSISTED


class TestIdempotency:
    def test_skips_processing_when_message_already_seen(self):
        pms = StubPMS()
        ledger = StubLedger(seen_message_ids={"msg-1"})
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=pms,
            ledger=ledger,
        )

        result = use_case.execute(make_email(message_id="msg-1"))

        assert result is None
        assert ledger.persisted == []
        assert pms.created is False


class TestPath3PassThrough:
    def test_routes_unknown_intent_to_pass_through(self):
        ledger = StubLedger()
        use_case = make_use_case(
            StubClassifier(Intent.UNKNOWN),
            StubExtractor(make_booking()),
            ledger=ledger,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.PASS_THROUGH
        assert ledger.persisted[0].path == ProcessingPath.PASS_THROUGH

    def test_routes_to_pass_through_on_exception(self):
        class BrokenPMS(PMSPort):
            def check_availability(self, booking):
                raise RuntimeError("Mews down")

            def create_booking(self, booking):
                raise RuntimeError("Mews down")

        ledger = StubLedger()
        use_case = make_use_case(
            StubClassifier(Intent.BOOKING_CONFIRMATION),
            StubExtractor(make_booking(confidence=ExtractionConfidence.HIGH)),
            pms=BrokenPMS(),
            ledger=ledger,
        )

        result = use_case.execute(make_email())

        assert result.path == ProcessingPath.PASS_THROUGH
        assert result.failure_reason == "Mews down"
        assert ledger.persisted[0].path == ProcessingPath.PASS_THROUGH
