---
name: analyze-property
description: Analyzes a single US residential property. Use when the user provides an address or property details for valuation, comparable sales, or investment analysis.
argument-hint: "[address or property details]"
---

Analyze the residential property provided in $ARGUMENTS and produce a structured property report.

## Steps

1. **Parse input** — Extract address, or if raw details are given (beds/baths/sqft/price), use those directly.

2. **Location analysis**
   - Neighborhood profile: urban/suburban/rural, walkability, school district quality
   - Proximity to amenities: transit, hospitals, shopping, employment hubs
   - Flood zone, wildfire, or other risk flags if determinable

3. **Property fundamentals**
   - Property type (SFH, condo, townhouse, multi-family)
   - Size, beds/baths, lot size, year built, notable features
   - Estimated price per sqft vs. local average

4. **Valuation estimate**
   - Estimated market value range based on known comps and market conditions
   - Price trend direction for the zip code (appreciating / stable / declining)
   - Note: This is an estimate — recommend a licensed appraisal for official valuation

5. **Investment snapshot**
   - Estimated gross rent (if applicable) and cap rate range
   - Key pros: appreciation potential, rental demand, low inventory
   - Key cons: taxes, HOA, condition risk, market saturation

6. **Summary verdict**
   - One-line verdict: Buy / Hold / Pass with a short rationale

## Output format
Return as a clean structured report with labeled sections. Keep each section to 3–5 bullet points max.

## Notes
- If specific data is unavailable, state the assumption made
- Do not fabricate specific MLS data or sale prices — use ranges and qualifiers
