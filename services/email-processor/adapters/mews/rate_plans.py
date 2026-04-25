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
}


# Maps sender email domains to agency names.
SENDER_DOMAIN_TO_AGENCY: dict[str, str] = {
    "reisenaktuell.com": "Reisen Aktuell",
    "sante-royale.com":  "Reisen Aktuell",  # hotel staff forwarding RA requests
    "dertouristik.com":  "Clevertours",
    "akon.de":           "AKON",
    "oir.de":            "AKON",
    "pepxpress.com":     "pepXpress",
    "kurz-mal-weg.de":   "GetAway",
    # Booking platforms — use DIR channel in Mews
    "kurzurlaub.de":     "DIR",
    "check24.de":        "DIR",
}

# Maps (agency, nights) → voucher code, derived from training data.
# Ambiguous cases (multiple possible codes) are resolved by body keywords below.
AGENCY_NIGHTS_TO_CODE: dict[tuple[str, int], str] = {
    ("AKON",  3): "RR-VERA-KURZ-VP",   # reisewell 3-night wellness stays
    ("AKON",  4): "RR-AKON-KURZ-VP",
    ("AKON",  7): "RR-AKON-LANG-VP",
    ("Reisen Aktuell", 10): "RR-SO-1225-VERA-10-VP-WS",  # Weihnachten/Silvester
}

# Body keywords that disambiguate when agency+nights alone isn't enough.
# Checked in order; first match wins.
BODY_KEYWORD_TO_CODE_SUFFIX: list[tuple[str, str]] = [
    ("sorgenfrei",  "-AI"),    # Sorgenfrei Spezial → all-inclusive codes
    ("preisspecial", "-AIL"),  # Preisspecial Upgrade to AI
    ("reisewell",   "RR-VERA-{DURATION}-VP"),  # reisewell always VERA-VP
    ("kennenlernwoche", "RR-VERA-07-VP-KW"),   # pepXpress Kuren product
]

# Maps guest-facing or agency-internal package names to canonical RATE_PLANS group keywords.
# Used when the email contains a product/package name that differs from the Mews rate plan name.
PACKAGE_NAME_ALIASES: dict[str, str] = {
    # DERTOUR / clevertours.com guest-facing package names
    "präventionspaket": "Kurzreisen",
    "praeventionspaket": "Kurzreisen",
    "wellness-kurzreise": "Kurzreisen",
    "wellness kurzreise": "Kurzreisen",
    "meer erleben": "Kurzreisen",
    # GetAway Travel GmbH
    "8 tage-wellness": "Kurzreisen",
    # pepXpress internal product name
    "kennenlernwoche": "Kuren",
    # Reisen Aktuell system code for Santé Royale Rügen
    "saru": "Kurzreisen",
    # Wörlitz Buspendel — agency name leaks into rate plan field
    "wörlitz": "Wörlitz Buspendel",
    "woerlitz": "Wörlitz Buspendel",
}


def _normalize_rate_plan(keyword: str) -> str:
    """Replace known package name aliases with their canonical RATE_PLANS group keyword."""
    lower = keyword.lower()
    for alias, canonical in PACKAGE_NAME_ALIASES.items():
        if alias in lower:
            return canonical
    return keyword


def resolve_voucher_code(rate_plan_keyword: str, nights: int) -> str | None:
    """
    Find the best matching voucher code for a rate plan keyword and night count.

    Applies package name aliases first, then matches rate plans whose name contains
    the keyword (case-insensitive), then picks the code matching the duration
    (KURZ/MITTEL/LANG or numeric 07/14/21). Prefers VERA channel, then ONL, then DIR.
    Falls back to duration-free codes (e.g. fixed packages like Wörlitz Buspendel).
    """
    keyword = _normalize_rate_plan(rate_plan_keyword)
    keyword_lower = keyword.lower()

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


def resolve_by_context(sender_email: str, nights: int, body: str, rate_plan_keyword: str = "") -> str | None:
    """
    Resolve a voucher code using sender domain, night count, and body keywords.

    This uses rules derived from matched training data and takes precedence over
    the keyword-only resolve_voucher_code when a sender domain is known.

    Falls back to resolve_voucher_code if no context-based rule matches.
    """
    import re
    body_lower = body.lower()

    # Identify agency from sender domain
    domain_match = re.search(r'@([\w.\-]+)', sender_email)
    domain = domain_match.group(1).lower() if domain_match else ""
    agency = next((a for d, a in SENDER_DOMAIN_TO_AGENCY.items() if domain.endswith(d)), None)

    # 1. Deterministic agency + nights rule
    if agency:
        direct = AGENCY_NIGHTS_TO_CODE.get((agency, nights))
        if direct:
            return direct

    # 2. Body keyword resolves ambiguity (agency known, multiple possible codes)
    if agency == "AKON" and "reisewell" in body_lower:
        duration = NIGHTS_TO_DURATION.get(nights, "KURZ")
        return f"RR-VERA-{duration}-VP"

    if agency in ("Reisen Aktuell", "Clevertours", "pepXpress") and nights in NIGHTS_TO_DURATION:
        duration = NIGHTS_TO_DURATION[nights]
        if "kennenlernwoche" in body_lower:
            return "RR-VERA-07-VP-KW"
        if "sorgenfrei" in body_lower:
            return f"RR-SO-0326-VERA-{duration}-AI"
        if "preisspecial" in body_lower or "ail" in body_lower:
            return f"RR-SO-0226-REAK-{duration}-AIL"
        if agency == "Reisen Aktuell":
            return f"RR-REAK-{duration}-VP"
        if agency in ("Clevertours", "pepXpress"):
            return f"RR-VERA-{duration}-VP"

    # 3. Fall back to keyword-based resolver
    if rate_plan_keyword:
        return resolve_voucher_code(rate_plan_keyword, nights)

    return None
