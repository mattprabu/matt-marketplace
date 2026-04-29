# Data Schemas — /screen-properties

Five dicts flow through the pipeline. These are the canonical field names
— all scripts depend on these.

---

## ScreenCriteria (Stage 1 output)

```python
{
    "areas": [str],              # ["Tampa FL", "33625", "Pasco County FL"]
    "filters": {
        "price_min": int | None,
        "price_max": int | None,
        "beds_min": int | None,
        "baths_min": float | None,
        "property_type": str | None,   # "single_family" | "condo" | "townhouse" | "multi_family"
        "year_built_min": int | None,
        "max_dom": int | None,
        "cash_flow_min": float | None, # deferred filter (applied post-scoring)
        "cap_rate_min": float | None,  # deferred filter (applied post-scoring)
    },
    "limit": int,                # default 10
    "output_formats": [str],     # ["html"] | ["html","notion"] | ["all"]
    "discovery_method": str,     # "web_search" | "url_paste" | "mls_paste"
    "raw_trigger": str,          # original user message for reference
}
```

---

## CandidateProperty (Stage 2-3 output, per property)

```python
{
    "address": str,
    "city": str,
    "state": str,
    "zip": str,
    "price": int,
    "beds": int,
    "baths": float,
    "sqft": int,
    "lot_sqft": int | None,
    "year_built": int | None,
    "property_type": str,
    "hoa_monthly": float | None,
    "annual_tax": float | None,
    "rent_from_listing": int | None,
    "days_on_market": int | None,
    "listing_url": str | None,

    # Enrichment
    "rent_estimate": int | None,
    "rent_source": str,          # "listing" | "rentometer" | "market_search" | None
    "tax_source": str,           # "listing" | "county_appraiser" | "estimated"
    "tax_estimated": bool,
    "insurance_annual": float,   # always estimated
    "comps_median_ppsf": float | None,

    # Data quality tracking
    "missing_data": [str],       # list of fields that could not be fetched
    "data_quality": str,         # "verified" | "partial" | "skipped"
}
```

---

## ScreenResult (Stage 5 output, per property)

```python
{
    "candidate": CandidateProperty,

    # Computed
    "gross_rent_annual": float,
    "tax_annual": float,
    "insurance_annual": float,
    "hoa_annual": float,
    "variable_opex_annual": float,   # 15 percent of gross rent
    "total_opex_annual": float,
    "noi_annual": float,
    "mortgage_monthly": float,
    "cash_flow_monthly": float,

    # Ratios
    "one_percent_ratio": float,  # rent/price monthly, e.g. 0.0085
    "cap_rate": float,           # NOI / price, decimal
    "price_per_sqft": float,
    "price_vs_comps_ratio": float | None,  # listing ppsf / median ppsf

    # Scoring
    "scores": {
        "one_percent": int,       # 0, 1, or 2
        "cap_rate": int,
        "cash_flow": int,
        "price_vs_comps": int,
    },
    "composite_pct": float,      # 0-100
    "verdict": str,              # "PASS" | "WATCH" | "SKIP"
    "hard_override": str | None, # reason if a force-SKIP triggered
}
```

---

## ScreeningRun (Stage 6 output, the whole run)

```python
{
    "run_id": str,                   # uuid for this run
    "timestamp": str,                # ISO datetime
    "criteria": ScreenCriteria,
    "candidates_found": int,         # before filter drops
    "candidates_screened": int,      # after Stage 3 (excludes unreadable URLs)
    "candidates_passed_filters": int,# after Stage 4
    "candidates_scored": int,        # after Stage 5
    "results": [ScreenResult],       # sorted: PASS first, then WATCH, then SKIP
    "pass_count": int,
    "watch_count": int,
    "skip_count": int,
    "assumptions_used": {
        "down_payment_pct": float,
        "interest_rate": float,
        "loan_term_years": int,
        "opex_variable_pct": float,  # 0.15 for quick screen
    },
    "data_issues": [str],            # human-readable summary of what failed
}
```

---

## NotionScreeningRow (Stage 7, per row in Screening Results DB)

```python
{
    "Property": str,                 # address (title)
    "Verdict": str,                  # "Pass" | "Watch" | "Skip"
    "Price": int,
    "Beds": int,
    "Sqft": int,
    "Est Cash Flow": float,          # monthly
    "Cap Rate": float,               # percent number
    "1% Rule": float,                # percent number
    "Data Quality": str,             # "Verified" | "Partial" | "Insurance estimated"
    "Screen Date": str,              # ISO date
    "Listing URL": str | None,
    "Run ID": str,                   # links to Screening History row
}
```

---

## NotionHistoryRow (Stage 7, per run in Screening History DB)

```python
{
    "Run": str,                      # "Tampa FL — 2026-04-21" (title)
    "Areas": str,                    # comma-separated
    "Price Range": str,              # "$200k-$400k"
    "Other Filters": str,            # compact summary
    "Candidates Found": int,
    "Pass Count": int,
    "Watch Count": int,
    "Skip Count": int,
    "Timestamp": str,                # ISO datetime
    "Run ID": str,                   # unique id used to link to result rows
}
```

---

## Field naming conventions (same as /analyze-property for continuity)

- Dollar amounts are `float`, never strings or cents
- Percentages stored as decimals (0.25, not 25)
- All rates annualized unless suffixed `_monthly`
- Dates as ISO strings
- Missing optional fields default to `None`, not empty string
