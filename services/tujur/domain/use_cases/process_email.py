from abc import ABC, abstractmethod

from domain.models import (
    BookingData,
    ExtractionConfidence,
    InboundEmail,
    Intent,
    ProcessingPath,
    ProcessingResult,
)
from domain.ports import BookingLedgerPort, PMSPort


class IntentClassifier(ABC):
    @abstractmethod
    def classify(self, email: InboundEmail) -> Intent:
        pass


class BookingExtractor(ABC):
    @abstractmethod
    def extract(self, email: InboundEmail) -> BookingData:
        pass


class ProcessEmail:
    def __init__(
        self,
        classifier: IntentClassifier,
        extractor: BookingExtractor,
        pms: PMSPort,
        ledger: BookingLedgerPort,
    ):
        self._classifier = classifier
        self._extractor = extractor
        self._pms = pms
        self._ledger = ledger

    def execute(self, email: InboundEmail) -> ProcessingResult | None:
        if self._ledger.has_processed(email.message_id):
            return None
        try:
            result = self._process(email)
        except Exception as e:
            result = ProcessingResult(
                path=ProcessingPath.PASS_THROUGH,
                email=email,
                failure_reason=str(e),
            )
        self._ledger.persist(result)
        return result

    def _process(self, email: InboundEmail) -> ProcessingResult:
        intent = self._classifier.classify(email)

        if intent != Intent.BOOKING_CONFIRMATION:
            return ProcessingResult(path=ProcessingPath.PASS_THROUGH, email=email)

        booking = self._extractor.extract(email)

        if booking.confidence == ExtractionConfidence.LOW:
            return ProcessingResult(
                path=ProcessingPath.ASSISTED,
                email=email,
                booking_data=booking,
            )

        if not self._pms.check_availability(booking):
            return ProcessingResult(
                path=ProcessingPath.ASSISTED,
                email=email,
                booking_data=booking,
            )

        reservation_id = self._pms.create_booking(booking)
        return ProcessingResult(
            path=ProcessingPath.AUTOMATED,
            email=email,
            booking_data=booking,
            mews_reservation_id=reservation_id,
        )
