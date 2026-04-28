"""
Mews Connector API mock server.

Response shapes are seeded from real api.mews-demo.com responses (April 2026).
IDs match the "Stay in Europe" demo property so tests remain comparable to the live demo.
"""
import uuid
from dataclasses import dataclass, field

from fastapi import FastAPI, Request

# Real IDs from the Mews demo — "Stay in Europe" property
SERVICE_ID = "35b42568-b7f3-4fb4-bca8-b06e007fa9d8"
STANDARD_CATEGORY_ID = "2c0d850f-0b3a-4cfe-b601-b06e0080f9a7"
LUXURY_CATEGORY_ID = "c8aba8fb-37dd-442c-b19e-b06e00813c2b"
_RATE_NS = uuid.UUID("a0000000-0000-0000-0000-000000000000")


def _rate(code: str) -> str:
    """Derive a stable, unique rate ID from a voucher code."""
    return str(uuid.uuid5(_RATE_NS, code))


# Each voucher code unlocks its own rate — IDs are deterministic per code.
VOUCHERS: dict[str, str] = {code: _rate(code) for code in [
    # VIP
    "RR-SO-DIR-VIP",
    "RR-SO-ONL-VIP",
    # Preisspecial Upgrade to AI (Reisen Aktuell)
    "RR-SO-0226-REAK-KURZ-AIL",
    "RR-SO-0226-REAK-MITTEL-AIL",
    "RR-SO-0226-REAK-LANG-AIL",
    # Gratis Nacht (DIR)
    "RR-SO-0226-DIR-KURZ-VP",
    "RR-SO-0226-ONL-KURZ-VP",
    "RR-SO-0226-OTA-KURZ-VP",
    "RR-SO-0226-DIR-MITTEL-VP",
    "RR-SO-0226-ONL-MITTEL-VP",
    "RR-SO-0226-OTA-MITTEL-VP",
    # Sorgenfrei Spezial (VERA)
    "RR-SO-0326-VERA-03-AI",
    "RR-SO-0326-VERA-KURZ-AI",
    "RR-SO-0326-VERA-05-AI",
    "RR-SO-0326-VERA-MITTEL-AI",
    "RR-SO-0326-VERA-07-AI",
    "RR-SO-0326-VERA-LANG-AI",
    # Sorgenfrei Spezial (DIR)
    "RR-SO-0326-DIR-03-AI",
    "RR-SO-0326-ONL-03-AI",
    "RR-SO-0326-DIR-KURZ-AI",
    "RR-SO-0326-ONL-KURZ-AI",
    "RR-SO-0326-DIR-05-AI",
    "RR-SO-0326-ONL-05-AI",
    "RR-SO-0326-DIR-MITTEL-AI",
    "RR-SO-0326-ONL-MITTEL-AI",
    "RR-SO-0326-DIR-07-AI",
    "RR-SO-0326-ONL-07-AI",
    "RR-SO-0326-DIR-LANG-AI",
    "RR-SO-0326-ONL-LANG-AI",
    # Verlängerungsnacht AKON
    "RR-ST-0024-VERLÄNGERUNG-01-VP",
    "RR-ONL-KURZ-VP",
    "RR-ONL-MITTEL-VP",
    "RR-ONL-LANG-VP",
    # Verlängerungsnacht Reisewell
    "RR-ST-0025-AKON-01-VER-VP",
    # Kuren (VERA)
    "RR-VERA-07-VP-WP",
    "RR-VERA-07-VP-KW",
    "RR-VERA-07-VP-RK",
    "RR-VERA-14-VP-KW",
    "RR-VERA-21-VP-KW",
    "RR-VERA-14-VP-RK",
    "RR-VERA-21-VP-RK",
    "RR-VERA-14-VP-WP",
    "RR-VERA-21-VP-WP",
    # Kuren (DIR)
    "RR-DIR-07-VP-WP",
    "RR-DIR-07-VP-KW",
    "RR-DIR-07-VP-RK",
    "RR-DIR-14-VP-KW",
    "RR-DIR-21-VP-KW",
    "RR-DIR-14-VP-RK",
    "RR-DIR-21-VP-RK",
    "RR-DIR-14-VP-WP",
    "RR-DIR-21-VP-WP",
    # Wörlitz Buspendel (VERA)
    "RR-WÖR-VP",
    # Interne Raten
    "RR-ST-0024-MITARBEITER-01-VP",
    "RR-ST-0024-COMPLIMENTARY-01-VP",
    # AKON (mit Begleitperson)
    "RR-AKON-KURZ-VP-BP",
    "RR-AKON-LANG-VP-BP",
    # Weihnachten/Silvester (VERA)
    "RR-SO-1225-VERA-05-VP-WE",
    "RR-SO-1225-VERA-05-VP-SI",
    "RR-SO-1225-VERA-10-VP-WS",
    # Weihnachten/Silvester (DIR)
    "RR-SO-1225-DIR-05-VP-WE",
    "RR-SO-1225-DIR-05-VP-SI",
    "RR-SO-1225-DIR-10-VP-WS",
    "RR-SO-1225-ONL-05-VP-SI",
    "RR-SO-1225-ONL-05-VP-WE",
    # Kurzreisen (VERA)
    "RR-VERA-KURZ-VP",
    "RR-VERA-MITTEL-VP",
    "RR-VERA-LANG-VP",
    # Kurzreisen (DIR)
    "RR-DIR-KURZ-VP",
    "RR-DIR-MITTEL-VP",
    "RR-DIR-LANG-VP",
    # Kurzreisen (Reisen Aktuell)
    "RR-REAK-KURZ-VP",
    "RR-REAK-MITTEL-VP",
    "RR-REAK-LANG-VP",
    # AKON
    "RR-AKON-KURZ-VP",
    "RR-AKON-LANG-VP",
]}
VOUCHER_CODE = "RR-SO-0226-REAK-KURZ-AIL"  # default used in fixtures

# Duration label → number of nights (used in KURZ/MITTEL/LANG voucher codes)
DURATION_NIGHTS: dict[str, int] = {
    "KURZ":   3,
    "MITTEL": 5,
    "LANG":   7,
}
NIGHTS_TO_DURATION: dict[int, str] = {v: k for k, v in DURATION_NIGHTS.items()}

# Rate plan name → voucher codes.
# Names are extracted from booking emails and used as lookup keys.
RATE_PLANS: dict[str, list[str]] = {
    "VIP": [
        "RR-SO-DIR-VIP",
        "RR-SO-ONL-VIP",
    ],
    "Preisspecial Upgrade to AI (Reisen Aktuell)": [
        "RR-SO-0226-REAK-KURZ-AIL",
        "RR-SO-0226-REAK-MITTEL-AIL",
        "RR-SO-0226-REAK-LANG-AIL",
    ],
    "Gratis Nacht (DIR)": [
        "RR-SO-0226-DIR-KURZ-VP",
        "RR-SO-0226-ONL-KURZ-VP",
        "RR-SO-0226-OTA-KURZ-VP",
        "RR-SO-0226-DIR-MITTEL-VP",
        "RR-SO-0226-ONL-MITTEL-VP",
        "RR-SO-0226-OTA-MITTEL-VP",
    ],
    "Sorgenfrei Spezial (VERA)": [
        "RR-SO-0326-VERA-03-AI",
        "RR-SO-0326-VERA-KURZ-AI",
        "RR-SO-0326-VERA-05-AI",
        "RR-SO-0326-VERA-MITTEL-AI",
        "RR-SO-0326-VERA-07-AI",
        "RR-SO-0326-VERA-LANG-AI",
    ],
    "Sorgenfrei Spezial (DIR)": [
        "RR-SO-0326-DIR-03-AI",
        "RR-SO-0326-ONL-03-AI",
        "RR-SO-0326-DIR-KURZ-AI",
        "RR-SO-0326-ONL-KURZ-AI",
        "RR-SO-0326-DIR-05-AI",
        "RR-SO-0326-ONL-05-AI",
        "RR-SO-0326-DIR-MITTEL-AI",
        "RR-SO-0326-ONL-MITTEL-AI",
        "RR-SO-0326-DIR-07-AI",
        "RR-SO-0326-ONL-07-AI",
        "RR-SO-0326-DIR-LANG-AI",
        "RR-SO-0326-ONL-LANG-AI",
    ],
    "Verlängerungsnacht AKON": [
        "RR-ST-0024-VERLÄNGERUNG-01-VP",
        "RR-ONL-KURZ-VP",
        "RR-ONL-MITTEL-VP",
        "RR-ONL-LANG-VP",
    ],
    "Verlängerungsnacht Reisewell": [
        "RR-ST-0025-AKON-01-VER-VP",
    ],
    "Verlängerungsnacht Gast": [
        "RR-ST-0024-VERLÄNGERUNG-01-VP",
    ],
    "Kuren (VERA)": [
        "RR-VERA-07-VP-WP",
        "RR-VERA-07-VP-KW",
        "RR-VERA-07-VP-RK",
        "RR-VERA-14-VP-KW",
        "RR-VERA-21-VP-KW",
        "RR-VERA-14-VP-RK",
        "RR-VERA-21-VP-RK",
        "RR-VERA-14-VP-WP",
        "RR-VERA-21-VP-WP",
    ],
    "Kuren (DIR)": [
        "RR-DIR-07-VP-WP",
        "RR-DIR-07-VP-KW",
        "RR-DIR-07-VP-RK",
        "RR-DIR-14-VP-KW",
        "RR-DIR-21-VP-KW",
        "RR-DIR-14-VP-RK",
        "RR-DIR-21-VP-RK",
        "RR-DIR-14-VP-WP",
        "RR-DIR-21-VP-WP",
    ],
    "Wörlitz Buspendel (VERA)": [
        "RR-WÖR-VP",
    ],
    "Interne Raten": [
        "RR-ST-0024-MITARBEITER-01-VP",
        "RR-ST-0024-COMPLIMENTARY-01-VP",
    ],
    "AKON (mit Begleitperson)": [
        "RR-AKON-KURZ-VP-BP",
        "RR-AKON-LANG-VP-BP",
    ],
    "Onlinebuchungen": [
        "RR-DIR-KURZ-VP",
        "RR-DIR-MITTEL-VP",
        "RR-ONL-KURZ-VP",
        "RR-ONL-MITTEL-VP",
        "RR-DIR-LANG-VP",
        "RR-ONL-LANG-VP",
        "RR-SO-1225-ONL-10-VP-WS",
        "RR-SO-1225-ONL-05-VP-WE",
        "RR-SO-0326-ONL-03-AI",
        "RR-SO-0326-ONL-KURZ-AI",
        "RR-SO-0326-ONL-05-AI",
        "RR-SO-0326-ONL-MITTEL-AI",
        "RR-SO-0326-ONL-07-AI",
        "RR-SO-0326-ONL-LANG-AI",
        "RR-SO-0226-ONL-KURZ-VP",
        "RR-SO-0226-ONL-MITTEL-VP",
    ],
    "Weihnachten/Silvester (DIR)": [
        "RR-SO-1225-DIR-05-VP-WE",
        "RR-SO-1225-DIR-05-VP-SI",
        "RR-SO-1225-DIR-10-VP-WS",
        "RR-SO-1225-ONL-05-VP-SI",
        "RR-SO-1225-ONL-10-VP-WS",
        "RR-SO-1225-ONL-05-VP-WE",
    ],
    "Kurzreisen (DIR)": [
        "RR-DIR-KURZ-VP",
        "RR-DIR-MITTEL-VP",
        "RR-DIR-LANG-VP",
    ],
    "Kurzreisen (Reisen Aktuell)": [
        "RR-REAK-KURZ-VP",
        "RR-REAK-MITTEL-VP",
        "RR-REAK-LANG-VP",
    ],
    "Weihnachten/Silvester (VERA)": [
        "RR-SO-1225-VERA-05-VP-WE",
        "RR-SO-1225-VERA-05-VP-SI",
        "RR-SO-1225-VERA-10-VP-WS",
    ],
    "AKON": [
        "RR-AKON-KURZ-VP",
        "RR-AKON-LANG-VP",
    ],
    "Kurzreisen (VERA)": [
        "RR-VERA-KURZ-VP",
        "RR-VERA-MITTEL-VP",
        "RR-VERA-LANG-VP",
    ],
}

_CATEGORIES = [
    {
        "Id": STANDARD_CATEGORY_ID,
        "ServiceId": SERVICE_ID,
        "IsActive": True,
        "Type": "Room",
        "Classification": "StandardSingle",
        "Names": {"en-US": "Standard"},
        "ShortNames": {"en-US": "Standard"},
        "Capacity": 2,
        "ExtraCapacity": 1,
    },
    {
        "Id": LUXURY_CATEGORY_ID,
        "ServiceId": SERVICE_ID,
        "IsActive": True,
        "Type": "Room",
        "Classification": "SuperiorDouble",
        "Names": {"en-US": "Luxury"},
        "ShortNames": {"en-US": "Luxury"},
        "Capacity": 4,
        "ExtraCapacity": 2,
    },
]


@dataclass
class MewsMockState:
    """Mutable state tests configure between calls. Call reset() in teardown."""

    availability: dict[str, list[int]] = field(default_factory=lambda: {
        STANDARD_CATEGORY_ID: [5, 5, 5, 5],
        LUXURY_CATEGORY_ID: [3, 3, 3, 3],
    })
    created_customers: list[dict] = field(default_factory=list)
    created_reservations: list[dict] = field(default_factory=list)
    _counter: int = 0

    def reset(self) -> None:
        self.availability = {
            STANDARD_CATEGORY_ID: [5, 5, 5, 5],
            LUXURY_CATEGORY_ID: [3, 3, 3, 3],
        }
        self.created_customers = []
        self.created_reservations = []
        self._counter = 0

    def set_availability(self, category_id: str, counts: list[int]) -> None:
        self.availability[category_id] = counts

    def _next_number(self) -> str:
        self._counter += 1
        return str(100_000 + self._counter)


def build_mock_app(state: MewsMockState) -> FastAPI:
    app = FastAPI()
    base = "/api/connector/v1"

    @app.post(f"{base}/vouchers/getAll")
    async def get_vouchers(request: Request):
        body = await request.json()
        requested = body.get("VoucherCodeValues", [])
        matched = {code: rate_id for code, rate_id in VOUCHERS.items() if code in requested}
        if not matched:
            return {"Vouchers": [], "VoucherAssignments": [], "VoucherCodes": []}
        voucher_list, assignment_list = [], []
        for i, (code, rate_id) in enumerate(matched.items()):
            vid = f"voucher-{i+1:04d}"
            voucher_list.append({"Id": vid, "ServiceId": SERVICE_ID, "IsActive": True})
            assignment_list.append({"VoucherId": vid, "RateId": rate_id})
        return {"Vouchers": voucher_list, "VoucherAssignments": assignment_list, "VoucherCodes": []}

    @app.post(f"{base}/resourceCategories/getAll")
    async def get_categories(_: Request):
        return {"ResourceCategories": _CATEGORIES, "Cursor": None}

    @app.post(f"{base}/services/getAvailability")
    async def get_availability(_: Request):
        return {
            "CategoryAvailabilities": [
                {
                    "CategoryId": cat_id,
                    "Availabilities": counts,
                    "Adjustments": [0] * len(counts),
                }
                for cat_id, counts in state.availability.items()
            ],
            "TimeUnitStartsUtc": [],
        }

    @app.post(f"{base}/customers/add")
    async def add_customer(request: Request):
        body = await request.json()
        customer = {
            "Id": str(uuid.uuid4()),
            "Number": state._next_number(),
            "FirstName": body.get("FirstName"),
            "LastName": body.get("LastName"),
            "Email": body.get("Email"),
            "IsActive": True,
            "ActivityState": "Active",
            "CreatedUtc": "2026-04-22T00:00:00Z",
            "UpdatedUtc": "2026-04-22T00:00:00Z",
        }
        state.created_customers.append(customer)
        return customer

    @app.post(f"{base}/reservations/add")
    async def add_reservation(request: Request):
        body = await request.json()
        reservations = []
        for res in body.get("Reservations", []):
            reservation = {
                "Id": str(uuid.uuid4()),
                "ServiceId": body.get("ServiceId"),
                "GroupId": str(uuid.uuid4()),
                "Number": f"RES-{state._next_number()}",
                "State": "Confirmed",
                "Origin": "Connector",
                "RequestedResourceCategoryId": res.get("RequestedCategoryId"),
                "RateId": res.get("RateId"),
                "VoucherCode": res.get("VoucherCode"),
                "AccountId": res.get("CustomerId"),
                "ScheduledStartUtc": res.get("StartUtc"),
                "ScheduledEndUtc": res.get("EndUtc"),
                "CreatedUtc": "2026-04-22T00:00:00Z",
                "UpdatedUtc": "2026-04-22T00:00:00Z",
            }
            state.created_reservations.append(reservation)
            reservations.append(reservation)
        return {"Reservations": reservations}

    return app
