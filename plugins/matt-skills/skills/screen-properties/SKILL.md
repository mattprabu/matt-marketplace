---
name: screen-properties
description: Bulk screens multiple US residential properties for investment potential. Use when the user provides a list of addresses or properties to evaluate and rank quickly.
argument-hint: "[list of addresses or property details]"
---

Screen the list of properties in $ARGUMENTS and rank them by investment potential.

## Steps

### 1. Parse the list
Extract each property from the input. Accept addresses, MLS-style specs (beds/baths/price/sqft), or mixed formats.

### 2. Score each property (1–10) across five dimensions

| Dimension | What to assess |
|---|---|
| **Location** | Neighborhood quality, school ratings, job market proximity |
| **Value** | Price vs. estimated market value — is it under/over priced? |
| **Rental potential** | Estimated rent-to-price ratio, rental demand in the area |
| **Appreciation** | Historical price growth trend for the zip code |
| **Risk** | Flood/fire risk, crime index, vacancy rate |

### 3. Produce a ranked comparison table

| Rank | Address | Score | Highlight | Watch-out |
|---|---|---|---|---|
| 1 | 123 Main St | 8.2 | Strong rental yield | High property tax |
| 2 | … | … | … | … |

### 4. Top pick recommendation
State the single best property from the list with a 2–3 sentence rationale covering why it scores highest and what risk to monitor.

### 5. Pass / Screen out
Flag any properties that are clearly not worth pursuing (score < 4) with a one-line reason.

## Notes
- Scores are estimates — recommend professional due diligence before purchase
- If fewer than 2 properties are provided, suggest using `analyze-property` for a deeper single-property report
- Acknowledge when data for a specific metric is unavailable rather than guessing
