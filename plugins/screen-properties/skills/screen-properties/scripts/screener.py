"""
screener.py — Quick-screen metric engine for /screen-properties skill.

Usage:
    from screener import screen_candidate
    result = screen_candidate(candidate_data, assumptions)

    from screener import screen_batch
    run = screen_batch(candidates_list, criteria, assumptions)

Input schemas are defined in references/data-schema.md.
Output is a ScreenResult per candidate, ScreeningRun for a batch.

This engine is source-agnostic: it does not care where the candidate data
came from (web search, user URL paste, MLS paste, or manual).
"""

from datetime import datetime, timezone
from typing import Any
import uuid


# ------------------------------------------------------------------
# Mortgage math (shared with /analyze-property approach)
# ------------------------------------------------------------------

def monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortized mortgage payment (P and I only)."""
    if principal <= 0:
        return 0.0
    r = annual_rate / 12.0
    n = years * 12
    if r == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


# ------------------------------------------------------------------
# Screen a single candidate
# ------------------------------------------------------------------

def screen_candidate(
    candidate: dict[str, Any],
    assumptions: dict[str, Any],
) -> dict[str, Any]:
    """
    Applies the quick-screen metrics to one candidate property.
    Returns a ScreenResult dict.

    The candidate must already have `rent_estimate` populated. If it does
    not, return a result with verdict='SKIP' and a missing_data flag — do
    not fabricate a rent number.
    """
    price = float(candidate["price"])
    sqft = int(candidate["sqft"])
    rent = candidate.get("rent_estimate")

    # Guard: no rent means no screen
    if not rent:
        return _build_skipped_result(
            candidate, "No rent estimate available — cannot screen"
        )

    rent = float(rent)
    gross_rent_annual = rent * 12

    # Fixed costs (try to use verified data, else estimate)
    tax_annual = float(candidate.get("annual_tax") or _estimate_tax(candidate))
    insurance_annual = float(candidate.get("insurance_annual")
                             or price * assumptions["insurance_pct"])
    hoa_annual = float(candidate.get("hoa_monthly") or 0) * 12

    # Simplified variable OpEx (quick screen uses 15 percent, not 23 percent)
    variable_opex_pct = assumptions.get("opex_variable_pct", 0.15)
    variable_opex_annual = gross_rent_annual * variable_opex_pct

    total_opex_annual = (
        tax_annual + insurance_annual + hoa_annual + variable_opex_annual
    )

    # NOI
    noi_annual = gross_rent_annual - total_opex_annual

    # Debt
    down_pct = assumptions["down_payment_pct"]
    loan_amount = price * (1 - down_pct)
    mortgage_monthly = monthly_payment(
        loan_amount, assumptions["interest_rate"], assumptions["loan_term_years"]
    )

    # Cash flow (monthly)
    cash_flow_monthly = (noi_annual / 12.0) - mortgage_monthly

    # Ratios
    one_percent_ratio = rent / price if price > 0 else 0.0
    cap_rate = noi_annual / price if price > 0 else 0.0
    price_per_sqft = price / sqft if sqft > 0 else 0.0

    comps_median = candidate.get("comps_median_ppsf")
    price_vs_comps_ratio = (
        (price_per_sqft / comps_median) if (comps_median and price_per_sqft) else None
    )

    # Score each metric (0, 1, or 2)
    scores = _score_quick(
        one_percent_ratio=one_percent_ratio,
        cap_rate=cap_rate,
        cash_flow_monthly=cash_flow_monthly,
        price_vs_comps_ratio=price_vs_comps_ratio,
    )

    # Composite (weights per screen-rubric.md)
    weights = {
        "one_percent": 0.30,
        "cap_rate": 0.30,
        "cash_flow": 0.25,
        "price_vs_comps": 0.15,
    }
    weighted = sum(scores[k] * weights[k] for k in weights)
    composite_pct = (weighted / 2.0) * 100

    # Hard-override SKIP checks
    hard_override = None
    verdict = None

    if cash_flow_monthly < 0 and one_percent_ratio < 0.007:
        hard_override = "Negative cash flow AND rent-to-price below 0.7 percent"
        verdict = "SKIP"
    elif price_vs_comps_ratio is not None and price_vs_comps_ratio > 1.10:
        pct_over = (price_vs_comps_ratio - 1) * 100
        hard_override = f"Listed at {pct_over:.1f} percent above comps median"
        verdict = "SKIP"

    # Fall back to composite
    if verdict is None:
        if composite_pct >= 75:
            verdict = "PASS"
        elif composite_pct >= 50:
            verdict = "WATCH"
        else:
            verdict = "SKIP"

    return {
        "candidate": candidate,

        "gross_rent_annual": round(gross_rent_annual, 2),
        "tax_annual": round(tax_annual, 2),
        "insurance_annual": round(insurance_annual, 2),
        "hoa_annual": round(hoa_annual, 2),
        "variable_opex_annual": round(variable_opex_annual, 2),
        "total_opex_annual": round(total_opex_annual, 2),
        "noi_annual": round(noi_annual, 2),
        "mortgage_monthly": round(mortgage_monthly, 2),
        "cash_flow_monthly": round(cash_flow_monthly, 2),

        "one_percent_ratio": round(one_percent_ratio, 4),
        "cap_rate": round(cap_rate, 4),
        "price_per_sqft": round(price_per_sqft, 2),
        "price_vs_comps_ratio": (
            round(price_vs_comps_ratio, 3) if price_vs_comps_ratio else None
        ),

        "scores": scores,
        "composite_pct": round(composite_pct, 1),
        "verdict": verdict,
        "hard_override": hard_override,
    }


def _score_quick(**kw) -> dict[str, int]:
    s: dict[str, int] = {}

    op = kw["one_percent_ratio"]
    s["one_percent"] = 2 if op >= 0.01 else (1 if op >= 0.007 else 0)

    cr = kw["cap_rate"]
    s["cap_rate"] = 2 if cr >= 0.07 else (1 if cr >= 0.05 else 0)

    cf = kw["cash_flow_monthly"]
    s["cash_flow"] = 2 if cf >= 200 else (1 if cf >= 0 else 0)

    ratio = kw["price_vs_comps_ratio"]
    if ratio is None:
        s["price_vs_comps"] = 1  # neutral when comps unavailable
    else:
        s["price_vs_comps"] = 2 if ratio <= 0.97 else (1 if ratio <= 1.05 else 0)

    return s


def _estimate_tax(candidate: dict) -> float:
    """
    Fallback tax estimate: 1.1 percent national, 0.9 percent for FL.
    Only used when listing + county appraiser both failed.
    """
    state = (candidate.get("state") or "").upper()
    rate = 0.009 if state == "FL" else 0.011
    return float(candidate["price"]) * rate


def _build_skipped_result(candidate: dict, reason: str) -> dict:
    """Produce a SKIP result for candidates that cannot be screened."""
    return {
        "candidate": candidate,
        "gross_rent_annual": 0,
        "tax_annual": 0,
        "insurance_annual": 0,
        "hoa_annual": 0,
        "variable_opex_annual": 0,
        "total_opex_annual": 0,
        "noi_annual": 0,
        "mortgage_monthly": 0,
        "cash_flow_monthly": 0,
        "one_percent_ratio": 0,
        "cap_rate": 0,
        "price_per_sqft": 0,
        "price_vs_comps_ratio": None,
        "scores": {"one_percent": 0, "cap_rate": 0,
                   "cash_flow": 0, "price_vs_comps": 0},
        "composite_pct": 0,
        "verdict": "SKIP",
        "hard_override": reason,
    }


# ------------------------------------------------------------------
# Batch runner
# ------------------------------------------------------------------

def screen_batch(
    candidates: list[dict[str, Any]],
    criteria: dict[str, Any],
    assumptions: dict[str, Any],
) -> dict[str, Any]:
    """
    Runs the quick screen on a batch of candidates. Applies deferred filters
    (cash_flow_min, cap_rate_min) after scoring. Sorts and truncates to limit.
    Returns a ScreeningRun dict.
    """
    candidates_found = len(candidates)

    # Score all candidates
    results = [screen_candidate(c, assumptions) for c in candidates]
    candidates_screened = sum(
        1 for r in results if r["hard_override"] != "No rent estimate available — cannot screen"
    )

    # Apply deferred filters
    filters = criteria.get("filters", {})
    cf_min = filters.get("cash_flow_min")
    cap_min = filters.get("cap_rate_min")

    filtered = []
    for r in results:
        if cf_min is not None and r["cash_flow_monthly"] < cf_min:
            continue
        if cap_min is not None and r["cap_rate"] < (cap_min / 100.0):
            continue
        filtered.append(r)

    candidates_passed_filters = len(filtered)

    # Sort: PASS desc-composite, then WATCH desc-composite, then SKIP desc-composite
    verdict_order = {"PASS": 0, "WATCH": 1, "SKIP": 2}
    filtered.sort(key=lambda r: (verdict_order[r["verdict"]], -r["composite_pct"]))

    # Truncate to limit
    limit = criteria.get("limit", 10)
    final_results = filtered[:limit]

    # Counts
    pass_count = sum(1 for r in final_results if r["verdict"] == "PASS")
    watch_count = sum(1 for r in final_results if r["verdict"] == "WATCH")
    skip_count = sum(1 for r in final_results if r["verdict"] == "SKIP")

    # Data issues summary
    data_issues = _summarize_data_issues(results)

    return {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "criteria": criteria,
        "candidates_found": candidates_found,
        "candidates_screened": candidates_screened,
        "candidates_passed_filters": candidates_passed_filters,
        "candidates_scored": len(final_results),
        "results": final_results,
        "pass_count": pass_count,
        "watch_count": watch_count,
        "skip_count": skip_count,
        "assumptions_used": {
            "down_payment_pct": assumptions["down_payment_pct"],
            "interest_rate": assumptions["interest_rate"],
            "loan_term_years": assumptions["loan_term_years"],
            "opex_variable_pct": assumptions.get("opex_variable_pct", 0.15),
        },
        "data_issues": data_issues,
    }


def _summarize_data_issues(results: list[dict]) -> list[str]:
    """Aggregate data-quality concerns across the batch."""
    issues = []
    tax_estimated = sum(
        1 for r in results if r["candidate"].get("tax_source") == "estimated"
    )
    no_rent = sum(
        1 for r in results if r["hard_override"] == "No rent estimate available — cannot screen"
    )
    partial = sum(
        1 for r in results if r["candidate"].get("data_quality") == "partial"
    )

    if no_rent:
        issues.append(f"{no_rent} candidates dropped — no rent estimate available")
    if tax_estimated:
        issues.append(
            f"{tax_estimated} candidates have estimated (not verified) property tax"
        )
    if partial:
        issues.append(
            f"{partial} candidates have partial data (some fields estimated)"
        )

    return issues


# ------------------------------------------------------------------
# CLI entry for testing
# ------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python screener.py <input.json>")
        print("  input.json: {candidates: [...], criteria: {...}, assumptions: {...}}")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    run = screen_batch(data["candidates"], data["criteria"], data["assumptions"])
    print(json.dumps(run, indent=2, default=str))
