"""
Mews rate plan → voucher code mapping.

Rate plan names are extracted from booking emails and used as lookup keys.
Each voucher code unlocks exactly one rate in Mews.
"""

DURATION_NIGHTS: dict[str, int] = {
    "KURZ":   3,
    "MITTEL": 5,
    "LANG":   7,
}
NIGHTS_TO_DURATION: dict[int, str] = {v: k for k, v in DURATION_NIGHTS.items()}

# Some rate plan groups use different night counts for the same KURZ/MITTEL/LANG labels.
# Keys must match (a substring of) the corresponding RATE_PLANS group name.
DURATION_OVERRIDES: dict[str, dict[int, str]] = {
    "AKON": {4: "KURZ", 7: "LANG"},
}


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
    "Kuren (ONL)": [
        "RR-DIR-07-VP-WP",
        "RR-ONL-07-VP-WP",
        "RR-DIR-07-VP-KW",
        "RR-ONL-07-VP-KW",
        "RR-DIR-07-VP-RK",
        "RR-ONL-07-VP-RK",
        "RR-DIR-14-VP-KW",
        "RR-ONL-14-VP-KW",
        "RR-DIR-14-VP-RK",
        "RR-ONL-14-VP-RK",
        "RR-DIR-14-VP-WP",
        "RR-ONL-14-VP-WP",
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
    "Stammgast 2024 (VERA)": [
        # Returning-guest discount, 3-night fixed package (Clevertours/DERTOUR).
        "RR-ST-A24-VERA-03-VP",
    ],
}


def resolve_voucher_code(rate_plan_keyword: str, nights: int) -> str | None:
    """
    Find the best matching voucher code for a rate plan keyword and night count.

    Matches rate plans whose name contains the keyword (case-insensitive), then picks
    the code matching the duration (KURZ/MITTEL/LANG or numeric 07/14/21).
    Prefers VERA channel, then ONL, then DIR.
    Falls back to duration-free codes (e.g. fixed packages like Wörlitz Buspendel).
    """
    keyword_lower = rate_plan_keyword.lower()

    # Sort so that the group whose name is most "covered" by the keyword comes first.
    # e.g. "AKON" should prefer the "AKON" group over "AKON (mit Begleitperson)".
    matching_groups = sorted(
        [(name, codes) for name, codes in RATE_PLANS.items() if keyword_lower in name.lower()],
        key=lambda nc: len(keyword_lower) / len(nc[0]),
        reverse=True,
    )
    if not matching_groups:
        return None

    candidates: list[str] = []
    for name, codes in matching_groups:
        # Use a group-specific duration mapping if one exists, otherwise fall back to global.
        override = next(
            (mapping for key, mapping in DURATION_OVERRIDES.items() if key.lower() in name.lower()),
            None,
        )
        duration = (override or NIGHTS_TO_DURATION).get(nights)
        for code in codes:
            if duration and f"-{duration}-" in code:
                candidates.append(code)
            elif duration and code.endswith(f"-{duration}"):
                candidates.append(code)

    # Fallback: numeric night match (e.g. Kuren: -07-, -14-, -21-)
    if not candidates:
        night_str = f"-{nights:02d}-"
        for _, codes in matching_groups:
            for code in codes:
                if night_str in code:
                    candidates.append(code)

    # Fallback: duration-free codes (fixed packages with no KURZ/MITTEL/LANG segment)
    if not candidates:
        duration_markers = {f"-{d}-" for d in DURATION_NIGHTS} | {f"-{n:02d}-" for n in DURATION_NIGHTS.values()}
        for _, codes in matching_groups:
            for code in codes:
                if not any(m in code for m in duration_markers):
                    candidates.append(code)

    if not candidates:
        return None

    for channel in ("VERA", "AKON", "ONL", "DIR"):
        for code in candidates:
            if f"-{channel}-" in code:
                return code

    return candidates[0]


