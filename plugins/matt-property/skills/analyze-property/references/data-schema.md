# Data Schemas

Four dicts flow through the pipeline. Keep these canonical — the analyzer
script and render templates all depend on these exact field names.

---

## PropertyData (Stage 1 output)

```python
{
    "address": str,              # "4521 Oak Ridge Dr, Tampa, FL 33625"
    "city": str,
    "state": str,                # 2-letter code
    "zip": str,                  # 5-digit
    "price": int,                # asking price in USD
    "beds": int,
    "baths": float,              # 2.5 allowed
    "sqft": int,
    "lot_sqft": int | None,
    "year_built": int | None,
    "property_type": str,        # "single_family" | "condo" | "townhouse" | "multi_family"
    "hoa_monthly": float | None, # listed HOA fee
    "annual_tax": float | None,  # listed annual tax
    "rent_from_listing": int | None,  # any rent estimate shown on listing page
    "days_on_market": int | None,
    "listing_url": str | None,
    "listing_description": str | None,
    "source": str,               # "url" | "mls_paste" | "pdf" | "manual"
}
```

Note: the field is `rent_from_listing` (generic), not anything listing-site
specific. This keeps the skill portable across any listing source.

---

## EnrichmentData (Stage 2 output)

```python
{
    "rent_estimate": {
        "primary": int,              # the number used in calcs
        "listing": int | None,       # from listing page if present
        "rentometer": int | None,    # from web_search rentometer result
        "market_search": int | None, # from general web_search result
        "user_override": int | None,
        "confidence": str,           # "high" | "medium" | "low"
        "source_used": str,          # which source was chosen
    },
    "tax_annual": {
        "value": float,
        "source": str,               # "listing" | "county_appraiser" | "estimated"
        "estimated": bool,           # true if the percentage-of-price fallback was used
    },
    "insurance_annual": {
        "value": float | None,
        "source": str,               # "listing" | "estimated"
    },
    "comps": [
        {
            "address": str,
            "sold_price": int,
            "sold_date": str,        # "2026-02-15"
            "sqft": int,
            "price_per_sqft": float,
            "beds": int,
            "baths": float,
        }
        # 3 to 5 comps
    ],
    "comps_avg_price_per_sqft": float | None,
    "neighborhood": {
        "crime_rating": str | None,
        "schools_rating": float | None,
        "walk_score": int | None,
    },
    "missing_data": [str],           # list of fields that could not be fetched
    "sources": {                     # URLs used for citation
        "rent": [str],
        "tax": [str],
        "comps": [str],
        "neighborhood": [str],
    }
}
```

---

## Assumptions (Stage 3 output)

```python
{
    "down_payment_pct": float,       # 0.25 default
    "interest_rate": float,          # 0.0725 default, fetched live
    "loan_term_years": int,          # 30
    "closing_costs_pct": float,      # 0.03
    "vacancy_pct": float,            # 0.08
    "management_pct": float,         # 0.10
    "maintenance_pct": float,        # 0.05
    "capex_pct": float,              # 0.05
    "insurance_pct": float,          # 0.005 national, 0.012 FL coastal, 0.008 FL inland
    "rent_growth_annual": float,     # 0.03
    "expense_growth_annual": float,  # 0.03
    "appreciation_annual": float,    # 0.035
    "hold_years": int,               # 5 (for IRR calc)
    "sale_cost_pct": float,          # 0.06 (realtor + closing at exit)
    "overrides_applied": [str],      # which fields the user overrode
}
```

---

## MetricsResult (Stage 4 output)

```python
{
    # Income
    "gross_rent_monthly": float,
    "gross_rent_annual": float,

    # Expenses (annual)
    "tax_annual": float,
    "insurance_annual": float,
    "hoa_annual": float,
    "vacancy_annual": float,
    "management_annual": float,
    "maintenance_annual": float,
    "capex_annual": float,
    "total_opex_annual": float,

    # NOI
    "noi_annual": float,
    "noi_monthly": float,

    # Debt
    "loan_amount": float,
    "down_payment": float,
    "closing_costs": float,
    "cash_to_close": float,
    "debt_service_monthly": float,
    "debt_service_annual": float,

    # Cash flow
    "cash_flow_monthly": float,
    "cash_flow_annual": float,

    # Returns (all as decimals, e.g. 0.072 for 7.2 percent)
    "cap_rate": float,
    "coc_return": float,
    "dscr": float | None,
    "one_percent_ratio": float,
    "fifty_percent_opex_ratio": float,
    "irr_5yr": float,
    "break_even_ratio": float,

    # Rule checks
    "one_percent_pass": bool,
    "fifty_percent_pass": bool,

    # Scoring (Stage 5 fills these)
    "metric_scores": {
        "cap_rate": int,             # 0, 1, or 2
        "coc": int,
        "dscr": int,
        "cash_flow": int,
        "one_percent": int,
        "fifty_percent": int,
        "irr": int,
        "price_vs_comps": int,
    },
    "composite_score_pct": float,
    "verdict": str,                  # "GREEN" | "YELLOW" | "RED"
    "verdict_reason": str,
    "hard_override_triggered": str | None,

    # Narrative
    "pros": [str],
    "cons": [str],
    "watch_items": [str],
    "risk_factors": [str],

    # Metadata
    "analyzed_at": str,              # ISO timestamp
    "property": PropertyData,
    "enrichment": EnrichmentData,
    "assumptions": Assumptions,
}
```

---

## Field naming conventions

- All dollar amounts are `float` (not strings, not cents).
- All percentages are stored as decimals (0.25, not 25).
- All rates are annualized unless suffixed `_monthly`.
- Dates are ISO strings.
- Optional fields default to `None`, not empty string.
