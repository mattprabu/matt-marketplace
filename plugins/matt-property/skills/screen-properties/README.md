# /screen-properties — Bulk Area Investment Screener

Screens many properties in an area quickly against Buy and Hold rental
investment criteria. Produces a ranked PASS / WATCH / SKIP table as the
triage step before running a full `/analyze-property` on the winners.

**Dependencies**: `web_fetch`, `web_search`, and Notion MCP (optional).
No paid APIs.

**Companion skill**: `/analyze-property` — the full deep-dive analyzer.
Install both; this one narrows the field, that one verifies the winners.

## Install

Drop the `screen-properties/` folder into your Claude skills directory
(or upload the zip). Activates on the `/screen-properties` trigger.

## Usage

### Basic

```
/screen-properties Tampa, FL
/screen-properties 33625, 33626, 33629
/screen-properties Pasco County, FL
/screen-properties Tampa; Land O Lakes; Wesley Chapel
```

### With filters

```
/screen-properties Tampa FL --price 200k-400k --beds 3 --type sfh
/screen-properties 33625 --cash-flow 200 --cap-rate 6 --max-dom 60
/screen-properties Land O Lakes --year-built 1990 --limit 15
```

### With discovery overrides (bulk from URLs or MLS)

```
/screen-properties Tampa FL [paste list of listing URLs]
/screen-properties Tampa FL [attach MLS CSV or pasted text block]
```

### With output flags

```
--html        (default, dark theme)
--pdf         (landscape, print-ready)
--notion      (Screening Results + History databases)
--markdown    (GitHub-flavored table)
--all         (all four)
```

## How it works

The pipeline has 6 stages:

1. **Parse criteria** — area(s), filters, output flags from the trigger
2. **Discover candidates** — web search, URL paste, or MLS paste
3. **Pull real per-property data** — taxes (county appraiser), rent
   (market search), insurance (state-based estimate). Anything unavailable
   is flagged, not fabricated.
4. **Apply filters** — price, beds, baths, type, year built, DOM
5. **Quick-screen metrics + verdict** — 1% rule, rough cap rate,
   estimated cash flow, price vs comps → PASS / WATCH / SKIP
6. **Render** — HTML / PDF / markdown / Notion per output flag(s)

### Verdict logic

Each candidate scored on 4 metrics (0, 1, or 2 each, weighted):

| Metric | Strong (2) | OK (1) | Weak (0) |
|---|---|---|---|
| 1% Rule | ≥ 1.0% | 0.7-1.0% | < 0.7% |
| Rough Cap Rate | ≥ 7% | 5-7% | < 5% |
| Est. Cash Flow | ≥ $200/mo | $0-200 | negative |
| Price vs Comps | ≤ 97% median | 97-105% | > 105% |

- **PASS (🟢)** — composite ≥ 75% (worth a full analysis)
- **WATCH (🟡)** — composite 50-75% (marginal)
- **SKIP (🔴)** — composite < 50% (don't deep-dive)

**Hard-override SKIP** if: negative cash flow AND 1% rule below 0.7%, OR
priced above 110% of comps median.

## Typical workflow

```
Step 1: /screen-properties Tampa FL --price 300k-500k --limit 10
        → table of 10 candidates with PASS / WATCH / SKIP

Step 2: Review the table, pick PASS rows you want to dig into

Step 3: Say "run full analysis on rows 1 and 3"
        → each becomes a full /analyze-property deep-dive
        → full 8-metric analysis, Notion Portfolio Scorecard entry
```

## Notion integration

On `--notion`, the skill writes to two databases under the same parent page
used by `/analyze-property`:

- **Screening Results** — one row per candidate per run (Property, Verdict,
  Price, Beds, Sqft, Est Cash Flow, Cap Rate, 1% Rule, Data Quality,
  Screen Date, Listing URL, Run ID)
- **Screening History** — one row per screening run (Run, Areas, Price
  Range, Other Filters, counts, Timestamp, Run ID)

Databases are created automatically on first use. Rows in Screening Results
link back to their history row via the Run ID column.

## Data honesty

This skill **never fabricates** data. If a rent estimate or tax can't be
found from any source, the property is either:

- **Dropped** from results (if critical data like rent is missing)
- **Flagged** with a data-quality badge (Verified / Partial / Insurance
  estimated)

Each run surfaces a "Data quality notes" section summarizing what was
unavailable across the batch. Insurance is always estimated — other fields
should be verified before investing.

## File map

```
screen-properties/
├── SKILL.md                     # Full pipeline spec
├── README.md                    # This file
├── scripts/
│   ├── screener.py              # Quick-screen metric engine
│   ├── filters.py               # Trigger parsing + pre-scoring filters
│   ├── render_table_html.py     # Dark HTML table
│   ├── render_table_pdf.py      # Landscape PDF
│   ├── render_table_md.py       # Markdown table
│   └── notion_export.py         # Notion DB row + schema builders
├── references/
│   ├── screen-rubric.md         # Verdict thresholds + weights
│   ├── data-schema.md           # All data dict shapes
│   └── notion-schema.md         # Screening Results + History schemas
└── examples/
    ├── sample-table.html        # Sample HTML
    ├── sample-table.pdf         # Sample PDF
    └── sample-table.md          # Sample markdown
```

## Not financial advice

The skill is a triage tool. Every report includes a disclaimer footer.
Verify all numbers yourself and consult a licensed agent before any
investment decision.
