"""
analyzer.py — Core metric computation and scoring for /analyze-property skill.

Usage:
    from analyzer import analyze
    result = analyze(property_data, enrichment_data, assumptions)

Input schemas are defined in references/data-schema.md.
Output is a MetricsResult dict — pass it to the render layer.

This module is source-agnostic: it does not care whether the property data
came from a listing URL, an MLS paste, a PDF, or manual entry. It only cares
about the shape of the input dicts.
"""

from datetime import datetime, timezone
from typing import Any


# ------------------------------------------------------------------
# Metric computations
# ------------------------------------------------------------------

def monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortized mortgage payment (P&I only, no tax/insurance)."""
    if principal <= 0:
        return 0.0
    r = annual_rate / 12.0
    n = years * 12
    if r == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def compute_irr(cash_flows: list[float], guess: float = 0.1) -> float:
    """
    Newton-Raphson IRR solver for a series of cash flows.
    cash_flows[0] should be the initial outflow (negative number).
    Returns IRR as decimal (e.g., 0.12 for 12 percent).
    """
    rate = guess
    for _ in range(100):
        npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
        dnpv = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))
        if abs(dnpv) < 1e-10:
            break
        new_rate = rate - npv / dnpv
        if abs(new_rate - rate) < 1e-7:
            return new_rate
        rate = new_rate
    return rate


def compute_5yr_irr(
    cash_to_close: float,
    cash_flow_annual: float,
    price: float,
    loan_amount: float,
    interest_rate: float,
    loan_term_years: int,
    appreciation: float,
    rent_growth: float,
    expense_growth: float,
    sale_cost_pct: float,
    hold_years: int = 5,
) -> float:
    """
    Levered IRR over hold_years. Assumes cash flow grows by
    (rent_growth - expense_growth/2) as a simple approximation, and property
    is sold at year N at appreciated value. Accounts for loan payoff at sale.
    """
    flows = [-cash_to_close]
    effective_growth = rent_growth - (expense_growth * 0.5)
    for year in range(1, hold_years + 1):
        year_cf = cash_flow_annual * ((1 + effective_growth) ** (year - 1))
        if year == hold_years:
            sale_price = price * ((1 + appreciation) ** hold_years)
            sale_net = sale_price * (1 - sale_cost_pct)
            remaining_balance = _remaining_loan_balance(
                loan_amount, interest_rate, loan_term_years, hold_years
            )
            year_cf += sale_net - remaining_balance
        flows.append(year_cf)
    return compute_irr(flows)


def _remaining_loan_balance(
    principal: float, annual_rate: float, loan_term_years: int, years_elapsed: int
) -> float:
    """Balance remaining after years_elapsed years of standard amortized payments."""
    if principal <= 0:
        return 0.0
    r = annual_rate / 12.0
    n = loan_term_years * 12
    payments_made = years_elapsed * 12
    if r == 0:
        return max(0, principal - (principal / n) * payments_made)
    pmt = monthly_payment(principal, annual_rate, loan_term_years)
    balance = principal * (1 + r) ** payments_made - pmt * (((1 + r) ** payments_made - 1) / r)
    return max(0, balance)


# ------------------------------------------------------------------
# Main analyze function
# ------------------------------------------------------------------

def analyze(
    property_data: dict[str, Any],
    enrichment: dict[str, Any],
    assumptions: dict[str, Any],
) -> dict[str, Any]:
    """
    Runs the full metric + scoring pipeline.
    Returns a MetricsResult dict per references/data-schema.md.
    """
    p = property_data
    e = enrichment
    a = assumptions

    price = float(p["price"])

    # ---- Income ----
    gross_rent_monthly = float(e["rent_estimate"]["primary"])
    gross_rent_annual = gross_rent_monthly * 12

    # ---- Operating expenses (annual) ----
    tax_annual = float(e["tax_annual"]["value"])

    insurance_source = e.get("insurance_annual", {})
    if insurance_source.get("value"):
        insurance_annual = float(insurance_source["value"])
    else:
        insurance_annual = price * a["insurance_pct"]

    hoa_annual = (float(p.get("hoa_monthly") or 0)) * 12
    vacancy_annual = gross_rent_annual * a["vacancy_pct"]
    management_annual = gross_rent_annual * a["management_pct"]
    maintenance_annual = gross_rent_annual * a["maintenance_pct"]
    capex_annual = gross_rent_annual * a["capex_pct"]

    total_opex_annual = (
        tax_annual + insurance_annual + hoa_annual
        + vacancy_annual + management_annual + maintenance_annual + capex_annual
    )

    # ---- NOI ----
    noi_annual = gross_rent_annual - total_opex_annual
    noi_monthly = noi_annual / 12

    # ---- Debt ----
    down_payment = price * a["down_payment_pct"]
    closing_costs = price * a["closing_costs_pct"]
    loan_amount = price - down_payment
    cash_to_close = down_payment + closing_costs

    debt_service_monthly = monthly_payment(
        loan_amount, a["interest_rate"], a["loan_term_years"]
    )
    debt_service_annual = debt_service_monthly * 12

    # ---- Cash flow ----
    cash_flow_monthly = noi_monthly - debt_service_monthly
    cash_flow_annual = cash_flow_monthly * 12

    # ---- Return metrics ----
    cap_rate = noi_annual / price if price > 0 else 0
    coc_return = cash_flow_annual / cash_to_close if cash_to_close > 0 else 0
    dscr = noi_annual / debt_service_annual if debt_service_annual > 0 else None
    one_percent_ratio = gross_rent_monthly / price if price > 0 else 0
    fifty_percent_opex_ratio = (
        (total_opex_annual / gross_rent_annual) if gross_rent_annual > 0 else 0
    )
    break_even_ratio = (
        (debt_service_annual + total_opex_annual) / gross_rent_annual
        if gross_rent_annual > 0 else 0
    )

    irr_5yr = compute_5yr_irr(
        cash_to_close=cash_to_close,
        cash_flow_annual=cash_flow_annual,
        price=price,
        loan_amount=loan_amount,
        interest_rate=a["interest_rate"],
        loan_term_years=a["loan_term_years"],
        appreciation=a["appreciation_annual"],
        rent_growth=a["rent_growth_annual"],
        expense_growth=a["expense_growth_annual"],
        sale_cost_pct=a["sale_cost_pct"],
        hold_years=a.get("hold_years", 5),
    )

    one_percent_pass = one_percent_ratio >= 0.01
    fifty_percent_pass = fifty_percent_opex_ratio <= 0.50

    # ---- Scoring ----
    scores = _score_metrics(
        cap_rate=cap_rate,
        coc_return=coc_return,
        dscr=dscr,
        cash_flow_monthly=cash_flow_monthly,
        one_percent_ratio=one_percent_ratio,
        fifty_percent_ratio=fifty_percent_opex_ratio,
        irr=irr_5yr,
        price=price,
        sqft=p["sqft"],
        comps_avg_ppsf=e.get("comps_avg_price_per_sqft"),
    )

    weights = {
        "cap_rate": 0.15,
        "coc": 0.20,
        "dscr": 0.15,
        "cash_flow": 0.15,
        "one_percent": 0.10,
        "fifty_percent": 0.10,
        "irr": 0.10,
        "price_vs_comps": 0.05,
    }

    weighted_score = sum(scores[k] * weights[k] for k in weights)
    max_score = 2.0
    composite_pct = (weighted_score / max_score) * 100

    # ---- Hard overrides ----
    override = None
    verdict = None

    missing_critical = (
        not e["rent_estimate"].get("primary")
        or not e["tax_annual"].get("value")
        or not price
    )

    # Force RED
    if cash_flow_monthly < 0 and dscr is not None and dscr < 1.0:
        override = "Negative cash flow AND DSCR below 1.0 — property cannot service its own debt"
        verdict = "RED"
    elif e.get("comps_avg_price_per_sqft") and p.get("sqft"):
        listing_ppsf = price / p["sqft"]
        if listing_ppsf > 1.10 * e["comps_avg_price_per_sqft"]:
            pct_over = (listing_ppsf / e["comps_avg_price_per_sqft"] - 1) * 100
            override = f"Listed at {pct_over:.1f} percent above comps — overpriced"
            verdict = "RED"
    elif missing_critical:
        override = "Critical data missing (rent, taxes, or price) — verdict withheld"
        verdict = "RED"
    elif irr_5yr < 0.05:
        override = f"5-year IRR of {irr_5yr * 100:.1f} percent is below risk-free Treasury yield"
        verdict = "RED"

    # Force GREEN (only if no force-RED triggered)
    if verdict is None:
        market_cap_rate = 0.06  # fallback benchmark when comps lack rent data
        forced_green = (
            one_percent_pass
            and cap_rate >= market_cap_rate
            and coc_return >= 0.08
            and dscr is not None and dscr >= 1.25
            and cash_flow_monthly >= 200
            and (
                not e.get("comps_avg_price_per_sqft")
                or not p.get("sqft")
                or (price / p["sqft"]) <= e["comps_avg_price_per_sqft"]
            )
        )
        if forced_green:
            verdict = "GREEN"
            override = "All gold-standard thresholds met (1 percent rule, cap rate, CoC, DSCR, cash flow)"

    # Fall back to composite
    if verdict is None:
        if composite_pct >= 80:
            verdict = "GREEN"
        elif composite_pct >= 55:
            verdict = "YELLOW"
        else:
            verdict = "RED"

    verdict_reason = _build_verdict_reason(
        verdict, composite_pct, override, cash_flow_monthly, cap_rate, coc_return, dscr
    )

    # ---- Narrative ----
    pros, cons, watch_items = _build_narrative(scores, {
        "cap_rate": cap_rate,
        "coc": coc_return,
        "dscr": dscr,
        "cash_flow": cash_flow_monthly,
        "one_percent": one_percent_ratio,
        "fifty_percent": fifty_percent_opex_ratio,
        "irr": irr_5yr,
        "price_vs_comps_ratio": (
            (price / p["sqft"]) / e["comps_avg_price_per_sqft"]
            if e.get("comps_avg_price_per_sqft") and p.get("sqft") else None
        ),
    })

    risk_factors = _identify_risks(p, e, gross_rent_annual, insurance_annual, hoa_annual)

    return {
        "gross_rent_monthly": round(gross_rent_monthly, 2),
        "gross_rent_annual": round(gross_rent_annual, 2),

        "tax_annual": round(tax_annual, 2),
        "insurance_annual": round(insurance_annual, 2),
        "hoa_annual": round(hoa_annual, 2),
        "vacancy_annual": round(vacancy_annual, 2),
        "management_annual": round(management_annual, 2),
        "maintenance_annual": round(maintenance_annual, 2),
        "capex_annual": round(capex_annual, 2),
        "total_opex_annual": round(total_opex_annual, 2),

        "noi_annual": round(noi_annual, 2),
        "noi_monthly": round(noi_monthly, 2),

        "loan_amount": round(loan_amount, 2),
        "down_payment": round(down_payment, 2),
        "closing_costs": round(closing_costs, 2),
        "cash_to_close": round(cash_to_close, 2),
        "debt_service_monthly": round(debt_service_monthly, 2),
        "debt_service_annual": round(debt_service_annual, 2),

        "cash_flow_monthly": round(cash_flow_monthly, 2),
        "cash_flow_annual": round(cash_flow_annual, 2),

        "cap_rate": round(cap_rate, 4),
        "coc_return": round(coc_return, 4),
        "dscr": round(dscr, 3) if dscr is not None else None,
        "one_percent_ratio": round(one_percent_ratio, 4),
        "fifty_percent_opex_ratio": round(fifty_percent_opex_ratio, 4),
        "irr_5yr": round(irr_5yr, 4),
        "break_even_ratio": round(break_even_ratio, 4),

        "one_percent_pass": one_percent_pass,
        "fifty_percent_pass": fifty_percent_pass,

        "metric_scores": scores,
        "composite_score_pct": round(composite_pct, 1),
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "hard_override_triggered": override,

        "pros": pros,
        "cons": cons,
        "watch_items": watch_items,
        "risk_factors": risk_factors,

        "analyzed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "property": p,
        "enrichment": e,
        "assumptions": a,
    }


# ------------------------------------------------------------------
# Scoring helpers
# ------------------------------------------------------------------

def _score_metrics(**kw) -> dict[str, int]:
    s: dict[str, int] = {}

    cr = kw["cap_rate"]
    s["cap_rate"] = 2 if cr >= 0.07 else (1 if cr >= 0.05 else 0)

    coc = kw["coc_return"]
    s["coc"] = 2 if coc >= 0.10 else (1 if coc >= 0.06 else 0)

    d = kw["dscr"]
    if d is None:
        s["dscr"] = 2  # no debt means no coverage issue
    else:
        s["dscr"] = 2 if d >= 1.25 else (1 if d >= 1.0 else 0)

    cf = kw["cash_flow_monthly"]
    s["cash_flow"] = 2 if cf >= 300 else (1 if cf >= 100 else 0)

    op = kw["one_percent_ratio"]
    s["one_percent"] = 2 if op >= 0.01 else (1 if op >= 0.007 else 0)

    fp = kw["fifty_percent_ratio"]
    s["fifty_percent"] = 2 if fp <= 0.45 else (1 if fp <= 0.55 else 0)

    irr = kw["irr"]
    s["irr"] = 2 if irr >= 0.12 else (1 if irr >= 0.08 else 0)

    price = kw["price"]
    sqft = kw["sqft"]
    comps = kw["comps_avg_ppsf"]
    if comps and sqft:
        ratio = (price / sqft) / comps
        s["price_vs_comps"] = 2 if ratio <= 0.97 else (1 if ratio <= 1.05 else 0)
    else:
        s["price_vs_comps"] = 1  # neutral when comps unavailable

    return s


def _build_verdict_reason(verdict, composite, override, cf, cap, coc, dscr) -> str:
    if override:
        return override
    dscr_str = f"{dscr:.2f}" if dscr is not None else "n/a"
    if verdict == "GREEN":
        return (
            f"Composite score {composite:.0f} percent — strong across cash flow "
            f"(${cf:,.0f}/mo), cap rate ({cap * 100:.1f} percent), "
            f"CoC ({coc * 100:.1f} percent)"
        )
    if verdict == "YELLOW":
        return (
            f"Composite score {composite:.0f} percent — marginal. "
            f"Cash flow ${cf:,.0f}/mo, cap {cap * 100:.1f} percent, DSCR {dscr_str}"
        )
    return (
        f"Composite score {composite:.0f} percent — fails minimum thresholds. "
        f"Cash flow ${cf:,.0f}/mo, cap {cap * 100:.1f} percent"
    )


def _build_narrative(scores, values):
    pros, cons, watch = [], [], []

    label_map = {
        "cap_rate": ("cap rate", lambda v: f"{v * 100:.2f} percent"),
        "coc": ("cash-on-cash return", lambda v: f"{v * 100:.2f} percent"),
        "dscr": ("DSCR", lambda v: f"{v:.2f}" if v is not None else "n/a"),
        "cash_flow": ("monthly cash flow", lambda v: f"${v:,.0f}"),
        "one_percent": ("rent-to-price ratio", lambda v: f"{v * 100:.2f} percent"),
        "fifty_percent": ("operating expense ratio",
                          lambda v: f"{v * 100:.1f} percent of rent"),
        "irr": ("5-year IRR", lambda v: f"{v * 100:.1f} percent"),
    }

    for metric, score in scores.items():
        if metric == "price_vs_comps":
            if score == 2:
                pros.append("Priced below comps (good entry point)")
            elif score == 0:
                cons.append("Listed above comps — overpriced")
            continue
        label, fmt = label_map.get(metric, (metric, str))
        val = values.get(metric)
        if val is None and metric != "dscr":
            continue
        if score == 2:
            pros.append(f"Strong {label} at {fmt(val)}")
        elif score == 0:
            cons.append(f"Weak {label} at {fmt(val)}")
        else:
            watch.append(f"{label.capitalize()} at {fmt(val)} — acceptable but not strong")

    return pros, cons, watch


def _identify_risks(p, e, gross_rent_annual, insurance_annual, hoa_annual) -> list[str]:
    risks = []

    if gross_rent_annual > 0 and insurance_annual / gross_rent_annual > 0.03:
        pct = insurance_annual / gross_rent_annual * 100
        risks.append(
            f"Insurance is {pct:.1f} percent of gross rent — elevated "
            f"(FL coastal risk or old structure)"
        )

    if gross_rent_annual > 0 and hoa_annual / gross_rent_annual > 0.20:
        pct = hoa_annual / gross_rent_annual * 100
        risks.append(
            f"HOA is {pct:.1f} percent of gross rent — eats into cash flow; "
            f"also ties appreciation to association health"
        )

    yb = p.get("year_built")
    if yb and yb < 1980:
        risks.append(f"Built in {yb} — capex-heavy (plumbing, electrical, roof risk)")

    dom = p.get("days_on_market")
    if dom and dom > 90:
        risks.append(f"On market {dom} days — priced too high or has an issue")

    if e.get("tax_annual", {}).get("estimated"):
        risks.append("Property tax was estimated, not verified with county appraiser")

    re_est = e.get("rent_estimate", {})
    sources = [v for k, v in re_est.items()
               if k in ("listing", "rentometer", "market_search") and v]
    if len(sources) >= 2:
        diff = (max(sources) - min(sources)) / max(sources)
        if diff > 0.15:
            risks.append(
                f"Rent estimates disagree by {diff * 100:.0f} percent across sources "
                f"— get a local broker opinion"
            )

    for field in e.get("missing_data", []):
        risks.append(f"Missing: {field} (assumption used — verify before buying)")

    return risks


# ------------------------------------------------------------------
# CLI entry for ad-hoc testing
# ------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyzer.py <input.json>")
        print("  input.json must contain: {property, enrichment, assumptions}")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    result = analyze(data["property"], data["enrichment"], data["assumptions"])
    print(json.dumps(result, indent=2, default=str))
