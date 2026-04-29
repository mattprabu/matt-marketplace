# Quick Screen Rubric — Bulk Area Screener

Industry-standard quick-screen thresholds for Buy and Hold rental triage
(US, 2026). These are **simpler** than the full `/analyze-property` rubric
— this skill is about fast triage across many properties, not deep analysis
of one.

---

## Simplified OpEx model (quick screen only)

The full `/analyze-property` skill uses a 23 percent OpEx allowance
(8 vacancy + 10 mgmt + 5 maintenance) on top of fixed costs. The quick
screen simplifies this:

**Quick screen OpEx** = taxes + insurance + HOA + **15 percent of rent**
(combined vacancy + maintenance + light management)

This runs faster and is accurate enough for PASS / SKIP decisions. The full
23 percent model is used in the deep-dive.

---

## Quick-screen metrics

Four metrics, each scored 0, 1, or 2:

### 1. 1 Percent Rule (weight: 30 percent)

Monthly rent as a percentage of purchase price.

| Score | Condition |
|---|---|
| 2 (strong) | At or above 1.0 percent |
| 1 (close) | 0.7 to 1.0 percent |
| 0 (fail) | Below 0.7 percent |

### 2. Rough Cap Rate (weight: 30 percent)

Using the simplified OpEx model.

| Score | Condition |
|---|---|
| 2 (strong) | At or above 7 percent |
| 1 (marginal) | 5 to 7 percent |
| 0 (fail) | Below 5 percent |

### 3. Estimated Monthly Cash Flow (weight: 25 percent)

After simplified OpEx and mortgage P&I (25 percent down, live 30-year rate).

| Score | Condition |
|---|---|
| 2 (strong) | At or above 200 dollars per month |
| 1 (marginal) | 0 to 200 dollars per month |
| 0 (fail) | Negative |

### 4. Price vs Area Median $/sqft (weight: 15 percent)

Subject property $/sqft compared to median of recent sales in same zip.

| Score | Condition |
|---|---|
| 2 (below market) | At or below 97 percent of median |
| 1 (fair) | 97 to 105 percent |
| 0 (overpriced) | Above 105 percent |

If comps data is unavailable, score defaults to 1 (neutral).

---

## Composite and verdict

```
max_score        = sum(weights * 2) = 2.00
actual_score     = sum(weights * metric_score)
composite_pct    = actual_score / max_score * 100
```

| Composite | Verdict | Meaning |
|---|---|---|
| At or above 75 percent | PASS (🟢) | Good candidate — run full /analyze-property |
| 50 to 75 percent | WATCH (🟡) | Marginal — negotiate price down, or pass |
| Below 50 percent | SKIP (🔴) | Do not waste time on full analysis |

---

## Hard-override rules

### Force SKIP (any one triggers):

1. Negative estimated cash flow AND rent-to-price below 0.7 percent
2. Listing dollars per sqft above 110 percent of area median

### No hard-override for PASS

Unlike `/analyze-property`, the quick screen does not have a "force PASS"
rule. A PASS here just means "worth running the full analyzer on." It is
intentionally easier to qualify for PASS than for GREEN in `/analyze-property`
— the deep dive does the strict qualification.

---

## Data quality indicators

Every row includes a **Data Quality** badge:

- **Verified** (green): price, beds, sqft, rent, and taxes all came from
  listing or county records
- **Partial** (amber): price and beds are solid, but tax or rent was
  estimated from market data
- **Insurance-estimated** (neutral): normal case for most listings —
  insurance is almost always estimated from price and state

If a critical field (rent, price) cannot be found, the row is **dropped
entirely** and flagged in the Missing Data summary. It does not appear
in the table at all, because a quick screen without rent data is
meaningless.

---

## Assumption set used by the quick screen

All of these are **flagged in the report footer** so the user knows exactly
what went into the numbers:

- Down payment: 25 percent (investor standard)
- Interest rate: live-fetched via `web_search` for current 30-year investor rate
- Loan term: 30 years
- OpEx allowance: 15 percent of rent (simplified)
- Insurance: 0.5 percent of price / year (national), 1.2 percent (FL coastal),
  0.8 percent (FL inland) — always estimated
- Closing costs: ignored at screen stage (material only for deep-dive)

**Key difference from /analyze-property**: this skill does NOT compute IRR,
DSCR, break-even ratio, or 5-year projections. Those are deep-dive metrics.
The screener is strictly for triage.

---

## Why these thresholds

The rubric mirrors the verdict logic in `/analyze-property` for continuity
— a PASS here means "likely to score at least YELLOW in the full analysis,
potentially GREEN." This lets Matt trust the pipeline:

- SKIP at screen → don't bother with full analysis
- WATCH at screen → maybe full analysis if other factors compel
- PASS at screen → definitely worth the deeper look

The 75 percent PASS threshold is deliberately higher than the 55 percent
YELLOW threshold in `/analyze-property` because this skill uses simplified
(more generous) assumptions. A PASS on the quick screen with 15 percent OpEx
could easily be a YELLOW on the full 23 percent OpEx model. That's expected.
