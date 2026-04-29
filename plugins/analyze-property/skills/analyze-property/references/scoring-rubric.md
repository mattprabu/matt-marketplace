# Scoring Rubric — Buy and Hold Rental Analysis

Industry-standard thresholds (2026 US). Each metric scores 0, 1, or 2. The
weighted composite maps to GREEN, YELLOW, or RED.

---

## Metric thresholds

### 1. Cap Rate (weight: 15 percent)

| Score | Condition |
|---|---|
| 2 (strong) | 7 percent or higher, or at or above market median for the zip |
| 1 (marginal) | 5 to 7 percent |
| 0 (fail) | Below 5 percent |

Coastal and appreciating markets often run 4 to 6 percent and rely on
appreciation. Use market median from comps as the primary benchmark when
available.

### 2. Cash-on-Cash Return (weight: 20 percent)

| Score | Condition |
|---|---|
| 2 (strong) | 10 percent or higher |
| 1 (marginal) | 6 to 10 percent |
| 0 (fail) | Below 6 percent, or negative |

### 3. DSCR — Debt Service Coverage Ratio (weight: 15 percent)

| Score | Condition |
|---|---|
| 2 (strong) | 1.25 or higher |
| 1 (marginal) | 1.0 to 1.25 |
| 0 (fail) | Below 1.0 |

DSCR below 1.0 means the property does not cover its own debt — disqualifier
for most investor lenders.

### 4. Monthly Cash Flow (weight: 15 percent)

Industry rule of thumb: 100 to 200 dollars per door minimum for Buy and Hold.

| Score | Condition |
|---|---|
| 2 (strong) | 300 dollars per month or higher |
| 1 (marginal) | 100 to 300 dollars per month |
| 0 (fail) | Below 100 dollars per month (includes negative) |

### 5. 1 Percent Rule (weight: 10 percent)

Classic screening rule: monthly rent at least 1 percent of purchase price.

| Score | Condition |
|---|---|
| 2 (pass) | Rent / Price at or above 1.0 percent |
| 1 (close) | 0.7 to 1.0 percent |
| 0 (fail) | Below 0.7 percent |

Hard to hit in high-cost markets (California, New York, coastal Florida).
Use as a screen, not a disqualifier — a 0.7 percent property in a strong
appreciation market can still work.

### 6. 50 Percent Rule (weight: 10 percent)

Operating expenses (excluding debt service) should be at or below 50 percent
of gross rent.

| Score | Condition |
|---|---|
| 2 (pass) | OpEx at or below 45 percent of gross rent |
| 1 (marginal) | 45 to 55 percent |
| 0 (fail) | Above 55 percent |

### 7. 5-Year IRR (weight: 10 percent)

Levered IRR including appreciation and sale at year 5 (6 percent sale cost).

| Score | Condition |
|---|---|
| 2 (strong) | 12 percent or higher |
| 1 (marginal) | 8 to 12 percent |
| 0 (fail) | Below 8 percent |

### 8. Price vs Comps (weight: 5 percent)

Compares listing dollars per sqft to average of 3 to 5 recent comps in the
same zip.

| Score | Condition |
|---|---|
| 2 (good deal) | At or below 97 percent of comp avg (priced below comps) |
| 1 (fair) | 97 to 105 percent |
| 0 (overpriced) | Above 105 percent |

---

## Composite score calculation

```
max_score       = sum(weights * 2) = 2.00
actual_score    = sum(weights * metric_score)
composite_pct   = actual_score / max_score * 100
```

### Verdict mapping

| Composite | Verdict | Color |
|---|---|---|
| 80 percent or higher | GREEN | Strong candidate — proceed with due diligence |
| 55 to 79 percent | YELLOW | Marginal — negotiate or pass unless other factors compel |
| Below 55 percent | RED | Pass at asking price |

---

## Hard-override rules

These trump the composite score.

### Force RED (any one triggers):

1. Monthly cash flow below zero AND DSCR below 1.0
2. Listing price above 110 percent of comps average dollars per sqft
3. Critical data missing after Stage 2 (rent OR taxes OR price)
4. 5-year IRR below 5 percent (worse than Treasury bonds)

### Force GREEN (all must be true):

1. 1 percent rule passes (rent at or above 1 percent of price)
2. Cap rate at or above market median for the zip
3. CoC at or above 8 percent
4. DSCR at or above 1.25
5. Monthly cash flow at or above 200 dollars
6. Price at or below comps average dollars per sqft

These are intentionally strict — a forced GREEN is a "buy this today" signal.
Most deals will score into GREEN via composite without hitting the
hard-override bar.

---

## Pros and Cons generation

Every report includes a pros and cons list. Generate them from the scoring data:

**Pros** — include every metric that scored 2:

- "Strong cap rate of 7.8 percent (national avg 6.2 percent)"
- "Priced 4 percent below recent comps"
- "DSCR of 1.42 — comfortable debt coverage"

**Cons** — include every metric that scored 0:

- "Negative cash flow of -85 dollars per month at asking price"
- "Fails 1 percent rule (rent / price equals 0.62 percent)"
- "High property tax eating 18 percent of gross rent"

**Watch items** — every metric that scored 1, with a one-line action:

- "CoC at 7.2 percent — acceptable but improves to 9.4 percent if you
  negotiate price to 335k"

---

## Risk factors (surface in the report)

Even with a GREEN verdict, flag these if present:

- Insurance cost above 3 percent of gross rent (Florida coastal risk)
- HOA above 20 percent of gross rent (eats cash flow; appreciation capped by
  association health)
- Year built before 1980 (likely capex-heavy; plumbing, electrical, roof risk)
- Days on market above 90 (something is wrong or priced too high)
- Taxes not verifiable from county appraiser
- Rent estimate variance above 15 percent between sources

List these under a "Risk Factors" section in the report — do not bury them.
