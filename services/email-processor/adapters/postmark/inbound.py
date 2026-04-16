from datetime import datetime

from ...domain.models import InboundEmail


def parse_postmark_payload(payload: dict) -> InboundEmail:
    """Maps a Postmark inbound webhook payload to an InboundEmail domain object."""
    return InboundEmail(
        message_id=payload["MessageID"],
        from_email=payload["From"],
        from_name=payload.get("FromName", ""),
        to_email=payload["To"],
        subject=payload.get("Subject", ""),
        text_body=payload.get("TextBody", ""),
        received_at=datetime.fromisoformat(payload["Date"]),
    )
