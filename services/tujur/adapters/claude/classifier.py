import anthropic

from domain.models import InboundEmail, Intent
from domain.use_cases.process_email import IntentClassifier

SYSTEM_PROMPT = """You are an email intent classifier for a hotel.
Classify the email intent as one of:
- booking_confirmation: a booking agency is confirming a reservation on behalf of a guest
- unknown: anything else (cancellations, modifications, inquiries, spam, etc.)

Respond with only the intent label, nothing else."""


class ClaudeIntentClassifier(IntentClassifier):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def classify(self, email: InboundEmail) -> Intent:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=10,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Subject: {email.subject}\n\n{email.text_body}",
                }
            ],
        )
        label = message.content[0].text.strip().lower()
        try:
            return Intent(label)
        except ValueError:
            return Intent.UNKNOWN
