"""
filters.py — Parse filter flags from a /screen-properties trigger message
and apply filters to a candidate list.

Usage:
    from filters import parse_criteria, apply_pre_scoring_filters

    criteria = parse_criteria(trigger_message)
    filtered = apply_pre_scoring_filters(candidates, criteria["filters"])
"""

import re


# ------------------------------------------------------------------
# Trigger message parsing
# ------------------------------------------------------------------

PROPERTY_TYPE_ALIASES = {
    "sfh": "single_family",
    "single-family": "single_family",
    "single_family": "single_family",
    "single family": "single_family",
    "house": "single_family",
    "condo": "condo",
    "townhouse": "townhouse",
    "townhome": "townhouse",
    "multi": "multi_family",
    "multi-family": "multi_family",
    "multi_family": "multi_family",
    "multifamily": "multi_family",
}

OUTPUT_ALIASES = {
    "--html": "html",
    "--pdf": "pdf",
    "--notion": "notion",
    "--markdown": "markdown",
    "--md": "markdown",
    "--all": "all",
}


def parse_criteria(trigger_message: str) -> dict:
    """
    Parse the full /screen-properties trigger message into a ScreenCriteria dict.

    Handles:
    - Area spec (everything before the first --flag, minus the trigger token)
    - --price MIN-MAX (supports 200k, 400000, 1.5m notation)
    - --beds N
    - --baths N
    - --type TYPE
    - --year-built YYYY
    - --max-dom N
    - --cash-flow N
    - --cap-rate N
    - --limit N
    - Output flags: --html, --pdf, --notion, --markdown, --all

    Returns a ScreenCriteria dict per references/data-schema.md.
    """
    # Strip the trigger token
    msg = trigger_message.strip()
    if msg.lower().startswith("/screen-properties"):
        msg = msg[len("/screen-properties"):].strip()

    # Split area from flags at the first `--`
    area_part, flag_part = _split_at_first_flag(msg)

    areas = _parse_areas(area_part)

    filters = {
        "price_min": None, "price_max": None,
        "beds_min": None, "baths_min": None,
        "property_type": None,
        "year_built_min": None,
        "max_dom": None,
        "cash_flow_min": None, "cap_rate_min": None,
    }

    limit = 10
    output_formats = []

    # Iterate through flags
    flags = _tokenize_flags(flag_part)

    for flag, value in flags:
        fl = flag.lower()
        if fl == "--price":
            lo, hi = _parse_price_range(value)
            filters["price_min"] = lo
            filters["price_max"] = hi
        elif fl == "--beds":
            filters["beds_min"] = int(value)
        elif fl == "--baths":
            filters["baths_min"] = float(value)
        elif fl == "--type":
            t = value.lower().strip()
            filters["property_type"] = PROPERTY_TYPE_ALIASES.get(t, t)
        elif fl == "--year-built":
            filters["year_built_min"] = int(value)
        elif fl == "--max-dom":
            filters["max_dom"] = int(value)
        elif fl == "--cash-flow":
            filters["cash_flow_min"] = float(value)
        elif fl == "--cap-rate":
            filters["cap_rate_min"] = float(value)
        elif fl == "--limit":
            limit = int(value)
        elif fl in OUTPUT_ALIASES:
            # Output flags take no value - fold them back
            output_formats.append(OUTPUT_ALIASES[fl])
            # If the "value" was parsed, it wasn't actually a value — it's the next area/flag
            # We don't re-add it here because _tokenize_flags handles valueless flags.

    # Default output
    if not output_formats:
        output_formats = ["html"]

    # Expand --all
    if "all" in output_formats:
        output_formats = ["html", "pdf", "notion", "markdown"]

    return {
        "areas": areas,
        "filters": filters,
        "limit": limit,
        "output_formats": output_formats,
        "discovery_method": "web_search",  # default; caller overrides if URLs/MLS pasted
        "raw_trigger": trigger_message,
    }


def _split_at_first_flag(msg: str) -> tuple[str, str]:
    """Return (area_part, flag_part) by splitting at the first `--flag`."""
    m = re.search(r"\s--[a-z][a-z0-9-]*", msg)
    if m:
        return msg[: m.start()].strip(), msg[m.start():].strip()
    return msg.strip(), ""


def _parse_areas(s: str) -> list[str]:
    """
    Parse the area portion. Supports:
      - 'Tampa, FL'
      - '33625, 33626'
      - 'Tampa FL; Land O Lakes FL'
      - 'Tampa, Land O Lakes, Wesley Chapel'
    Areas are split on semicolons first, then on commas IF the comma is
    followed by a known state abbreviation or another city word.

    Keep it simple: split on `;` first, then trust the user's comma usage.
    If the result has a single string that looks like 'City, ST', keep it.
    """
    if not s:
        return []

    # Split on semicolons (strict multi-area separator)
    if ";" in s:
        return [x.strip() for x in s.split(";") if x.strip()]

    # Heuristic: if the string looks like a single "City, ST" (two tokens,
    # the second is a 2-letter state), keep as one area. Otherwise split on commas.
    parts = [x.strip() for x in s.split(",")]
    if len(parts) == 2 and len(parts[1].strip()) == 2 and parts[1].strip().isalpha():
        return [s.strip()]

    # Also: if every part looks like a ZIP (5 digits), return each as its own area
    if all(re.fullmatch(r"\d{5}", p) for p in parts):
        return parts

    # Otherwise, join pairs like "Tampa, FL" into single entries when we see a
    # 2-letter state as the second piece. Heuristic pairing.
    combined = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if i + 1 < len(parts):
            next_p = parts[i + 1].strip()
            if len(next_p) == 2 and next_p.isalpha():
                combined.append(f"{p}, {next_p.upper()}")
                i += 2
                continue
        combined.append(p)
        i += 1

    return [c for c in combined if c]


def _tokenize_flags(s: str) -> list[tuple[str, str]]:
    """
    Parse the flag portion into (flag, value) pairs.
    Output-only flags have value=''.
    """
    tokens = re.findall(r"(--[a-z][a-z0-9-]*)\s*([^-\s][^\s]*(?:\s+[^-\s][^\s]*)*)?",
                        s, flags=re.IGNORECASE)
    cleaned = []
    for flag, value in tokens:
        fl = flag.lower()
        # Output-only flags: drop any value we mis-paired
        if fl in OUTPUT_ALIASES:
            cleaned.append((fl, ""))
        else:
            cleaned.append((fl, (value or "").strip()))
    return cleaned


def _parse_price_range(s: str) -> tuple[int | None, int | None]:
    """
    Parse '200k-400k', '250000-500000', '1.5m', '-400k', '200k-'.
    Returns (min, max). Either may be None.
    """
    s = s.strip().replace("$", "").replace(",", "")
    if "-" in s:
        lo_str, hi_str = s.split("-", 1)
    else:
        lo_str, hi_str = "", s  # single value treated as max-only

    def parse_one(x: str) -> int | None:
        x = x.strip().lower()
        if not x:
            return None
        multiplier = 1
        if x.endswith("k"):
            multiplier = 1_000
            x = x[:-1]
        elif x.endswith("m"):
            multiplier = 1_000_000
            x = x[:-1]
        try:
            return int(float(x) * multiplier)
        except ValueError:
            return None

    return parse_one(lo_str), parse_one(hi_str)


# ------------------------------------------------------------------
# Pre-scoring filters (applied after Stage 3, before Stage 5)
# ------------------------------------------------------------------

def apply_pre_scoring_filters(
    candidates: list[dict], filters: dict
) -> list[dict]:
    """
    Drop candidates that fail filters which do NOT require scoring.
    cash_flow_min and cap_rate_min are deferred (applied after scoring).
    """
    out = []
    for c in candidates:
        if filters.get("price_min") and c["price"] < filters["price_min"]:
            continue
        if filters.get("price_max") and c["price"] > filters["price_max"]:
            continue
        if filters.get("beds_min") and c["beds"] < filters["beds_min"]:
            continue
        if filters.get("baths_min") and c["baths"] < filters["baths_min"]:
            continue
        if filters.get("property_type"):
            if c.get("property_type") != filters["property_type"]:
                continue
        if filters.get("year_built_min"):
            yb = c.get("year_built")
            if not yb or yb < filters["year_built_min"]:
                continue
        if filters.get("max_dom"):
            dom = c.get("days_on_market")
            if dom is not None and dom > filters["max_dom"]:
                continue
        out.append(c)
    return out


# ------------------------------------------------------------------
# CLI entry for testing
# ------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python filters.py '/screen-properties [args]'")
        sys.exit(1)
    import json
    print(json.dumps(parse_criteria(sys.argv[1]), indent=2))
