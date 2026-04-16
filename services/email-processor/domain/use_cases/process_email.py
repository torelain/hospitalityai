from abc import ABC, abstractmethod

from ..models import (
    BookingData,
    ExtractionConfidence,
    InboundEmail,
    Intent,
    ProcessingPath,
    ProcessingResult,
)
from ..ports import EmailSenderPort, PMSPort


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
        email_sender: EmailSenderPort,
    ):
        self._classifier = classifier
        self._extractor = extractor
        self._pms = pms
        self._email_sender = email_sender

    def execute(self, email: InboundEmail) -> ProcessingResult:
        try:
            return self._process(email)
        except Exception as e:
            result = ProcessingResult(
                path=ProcessingPath.PASS_THROUGH,
                email=email,
                failure_reason=str(e),
            )
            self._email_sender.send_pass_through(result)
            return result

    def _process(self, email: InboundEmail) -> ProcessingResult:
        intent = self._classifier.classify(email)

        if intent != Intent.BOOKING_CONFIRMATION:
            result = ProcessingResult(path=ProcessingPath.PASS_THROUGH, email=email)
            self._email_sender.send_pass_through(result)
            return result

        booking = self._extractor.extract(email)

        if booking.confidence == ExtractionConfidence.LOW:
            result = ProcessingResult(
                path=ProcessingPath.ASSISTED,
                email=email,
                booking_data=booking,
            )
            self._email_sender.send_assisted_handoff(result)
            return result

        if not self._pms.check_availability(booking):
            result = ProcessingResult(
                path=ProcessingPath.ASSISTED,
                email=email,
                booking_data=booking,
            )
            self._email_sender.send_assisted_handoff(result)
            return result

        reservation_id = self._pms.create_booking(booking)
        result = ProcessingResult(
            path=ProcessingPath.AUTOMATED,
            email=email,
            booking_data=booking,
            mews_reservation_id=reservation_id,
        )
        self._email_sender.send_auto_booking_notification(result)
        return result
