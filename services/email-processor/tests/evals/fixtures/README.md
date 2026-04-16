# Eval Fixtures

Real booking agency emails used to measure LLM extraction accuracy.

Each fixture is a `.json` file with the following structure:

```json
{
  "email": {
    "subject": "Booking Confirmation — Smith, 1-5 June",
    "text_body": "Dear Hotel, we confirm the following booking..."
  },
  "expected": {
    "intent": "booking_confirmation",
    "guest_name": "John Smith",
    "arrival_date": "2026-06-01",
    "departure_date": "2026-06-05",
    "room_category": "Deluxe Double",
    "num_guests": 2,
    "agency_name": "Best Travel Agency",
    "special_wishes": null
  }
}
```

Add real booking agency emails here before the hackathon. Anonymise guest data if needed.
