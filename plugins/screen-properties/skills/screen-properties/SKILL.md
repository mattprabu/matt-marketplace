---
name: screen-properties
description: >
  Bulk screens multiple US residential properties in an area against Buy and
  Hold investment criteria, producing a ranked PASS WATCH SKIP table. Triggers
  on /screen-properties followed by an area (city, ZIP, county, or
  multi-area) plus optional filters (price, beds, baths, type, year built,
  DOM, min cash flow, min cap rate, limit) and output flags (html, pdf,
  notion, markdown, all). Runs a 6-stage pipeline: parse trigger, discover
  candidates (web search or user-pasted URLs or MLS), fetch per-property
  real data (taxes, HOA, insurance), apply filters, score each candidate
  using 4 quick-screen metrics (1 percent rule, rough cap rate, estimated
  cash flow, price vs comps), render output. Hands off PASS rows to full
  /analyze-property analyses on user request. Writes to separate Notion
  Screening Results and Screening History databases. Uses only web_fetch
  and web_search, no paid APIs. Never use without the /screen-properties
  trigger.
trigger: /screen-properties
version: 1.0.0
companion_skill: analyze-property
---

# Screen Properties — Bulk Area Investment Screener

## Purpose

Screens many properties in an area quickly against Buy and Hold rental
investment criteria, producing a ranked PASS / WATCH / SKIP table. This is
the **triage step** before running a full `/analyze-property` analysis on
the winners.

**Design principle: wide and shallow, not deep.** Where `/analyze-property`
is deep-and-precise for a single property, this skill is broad-and-fast for
many. The user runs this to find candidates, then feeds the top 2 to 5 into
`/analyze-property` for the full deep-dive.

This is **not financial advice** — it is a decision-support triage tool.

---

## When to trigger

Trigger **only** when the user message starts with `/screen-properties`.

### Supported invocation patterns

```
/screen-properties Tampa, FL                                    (city)
/screen-properties 33625                                        (single ZIP)
/screen-properties 33625, 33626, 33629                          (multiple ZIPs)
/screen-properties Pasco County, FL                             (county)
/screen-properties Tampa, Land O Lakes, Wesley Chapel           (multi-area)
/screen-properties                                              (asks for area)
```

### With filters (appended to area spec)

```
/screen-properties Tampa FL --price 200k-400k --beds 3 --type sfh
/screen-properties 33625 --cash-flow 200 --cap-rate 6 --max-dom 60
/screen-properties Land O Lakes --year-built 1990 --limit 15
```

### With discovery overrides

```
/screen-properties Tampa FL [paste list of URLs]
/screen-properties Tampa FL [attach MLS CSV or text block]
```

### With output flags

```
/screen-properties Tampa FL --html                   (dark HTML table, default)
/screen-properties Tampa FL --pdf                    (print-ready PDF)
/screen-properties Tampa FL --notion                 (Notion DB + History log)
/screen-properties Tampa FL --markdown               (markdown table for paste)
/screen-properties Tampa FL --all                    (all four outputs)
```

---

## The 6-stage pipeline

Execute stages in order. Do not skip stages.

### Stage 1 — Parse criteria

Extract from the trigger message:

- **Area spec**: one or more of: city, ZIP, county, multi-area list
- **Filters** (all optional, parse from `--flag value` syntax):
  - `--price` range (e.g., `200k-400k`, `250000-500000`)
  - `--beds` minimum (e.g., `3`)
  - `--baths` minimum (e.g., `2`)
  - `--type` (e.g., `sfh` / `single_family`, `condo`, `townhouse`, `multi_family`)
  - `--year-built` minimum (e.g., `1990`)
  - `--cash-flow` minimum per month (e.g., `200`)
  - `--cap-rate` minimum percent (e.g., `6`)
  - `--max-dom` max days on market (e.g., `90`)
  - `--limit` max results (default 10)
- **Output flag**: `--html` (default), `--pdf`, `--notion`, `--markdown`, `--all`

If the area is not provided, ask: "Which area do you want to screen? (City,
ZIP codes, or county)"

### Stage 2 — Discover candidate listings

The skill is **listing-site agnostic** — works with any site that returns
listing data via `web_fetch`.

Three discovery methods, used in this priority:

1. **User-provided URL list** (if the user pasted URLs after the trigger):
   use those directly, skip web search.

2. **MLS paste** (if the user pasted a text block with multiple listings or
   attached an MLS CSV): parse for address / price / beds / sqft / DOM per
   listing.

3. **Web search** (default if no URLs or paste provided):
   Run `web_search` with queries like:
   - `"[area] homes for sale 3 bedroom under 400k 2026"`
   - `"[zip] real estate listings active"`
   - `"homes for sale [area] investment property"`

   Pull the top results from the search. For each promising result, run
   `web_fetch` to extract the listing data. Stop when the user's `--limit`
   is reached (plus 50 percent buffer to account for filter drop-off).

**Important — anti-scraping reality:** some listing sites return empty or
blocked content via `web_fetch`. When that happens for a given URL:
- log it as "unreadable" in the missing-data tracker
- move on to the next candidate
- if more than 50 percent of candidates fail to load, inform the user and
  suggest they paste URLs or an MLS export instead

### Stage 3 — Pull per-property real data

For each candidate property that passed Stage 2 ingest, fetch:

1. **Listing-provided data** (from the fetched page):
   address, price, beds, baths, sqft, year built, property type, DOM,
   HOA if listed, annual tax if listed, any displayed rent estimate

2. **Tax** (if not in listing):
   - `web_search` for `"[county] [state] property appraiser [address]"`
   - `web_fetch` the top county appraiser result
   - If unavailable: flag as "tax unverified, estimated at 1.1 percent of price"
     (0.9 percent for FL) — and surface this in the Missing Data column

3. **Rent estimate**:
   - Listing-provided rent if shown
   - `web_search` for `"[zip] [beds] bedroom rent average 2026"` for market rate
   - `web_search` for `"rentometer [zip] [beds] bedroom"` as cross-reference
   - If no rent data found from any source, **mark the row as "NO DATA — skip"**
     rather than guess. Add to Missing Data column.

4. **HOA** (only from listing or direct county record — never estimated).

5. **Insurance**:
   - Estimate at 0.5 percent of price annually (national), 1.2 percent for
     FL coastal, 0.8 percent for FL inland — always flagged as estimated.

**Rule**: the skill **must tell the user** when data was unavailable and an
estimate was used. Do not silently guess. Every row has a "Data Quality"
indicator:
- **Verified** = all fields from listing or county records
- **Partial** = some fields estimated (insurance is normal; tax or HOA is flagged)
- **Skipped** = critical data (rent or price) missing, row dropped

### Stage 4 — Apply filters

Drop candidates that fail any user-specified filter:

- Price outside range
- Beds below minimum
- Baths below minimum
- Type mismatch
- Year built below minimum
- DOM above maximum

Note: `--cash-flow` and `--cap-rate` filters are applied **after** Stage 5
scoring, since those values don't exist until metrics are computed.

### Stage 5 — Quick-screen metrics + verdict

For each remaining candidate, use `scripts/screener.py` to compute:

- **Rent-to-price ratio** (1 percent rule check)
- **Rough cap rate**: uses simplified OpEx model:
  - Taxes (from listing or county record, or flagged-estimated)
  - Insurance (estimated from price and state)
  - HOA (if known)
  - 15 percent of rent for combined vacancy + maintenance (simpler than the
    full 23 percent used in `/analyze-property` because this is a quick screen)
- **Estimated monthly cash flow**: NOI / 12 minus mortgage P&I at 25 percent
  down, live 2026 rate
- **Price vs area median $/sqft**: compare listing $/sqft to median $/sqft
  from 3-5 recent sales in the same zip

### Verdict logic — industry-standard quick screen

Each metric scores 0, 1, or 2. Composite determines PASS / WATCH / SKIP:

| Quick Metric | Strong (2) | OK (1) | Weak (0) |
|---|---|---|---|
| 1 percent rule | ≥ 1.0% | 0.7-1.0% | < 0.7% |
| Rough cap rate | ≥ 7% | 5-7% | < 5% |
| Est. cash flow | ≥ $200/mo | $0-200 | negative |
| Price vs comps | ≤ 97% of median | 97-105% | > 105% |

**Verdict mapping** (industry standard for Buy and Hold screening in 2026):

- **PASS (🟢)** — composite ≥ 75% (candidate for full analysis)
- **WATCH (🟡)** — composite 50-75% (marginal, negotiate or skip)
- **SKIP (🔴)** — composite < 50% (don't waste time on full analysis)

**Hard override SKIP** (any one triggers):
- Negative estimated cash flow AND rent-to-price below 0.7 percent
- Listed at more than 110 percent of comps median $/sqft

Now apply the deferred filters (`--cash-flow`, `--cap-rate`). Drop candidates
that fail.

### Stage 6 — Render output (dispatcher)

Sort the surviving candidates: PASS first (by composite desc), then WATCH,
then SKIP. Truncate to `--limit` (default 10).

Render based on user flag(s):

- **`--html`** (default) → `scripts/render_table_html.py` produces a
  dark-themed sortable HTML table. Each row shows: rank, verdict emoji,
  address (linked), price, beds/baths, sqft, rough cap rate, est. cash flow,
  1% rule, data quality, and a "Deep dive" cell with a copy-paste-ready
  `/analyze-property [URL]` command.

- **`--pdf`** → `scripts/render_table_pdf.py` produces a print-friendly PDF
  with the same table, landscape orientation.

- **`--markdown`** → `scripts/render_table_md.py` produces a GitHub-flavored
  markdown table the user can paste anywhere.

- **`--notion`** → `scripts/notion_export.py` writes each row to the
  "Screening Results" Notion database (created if missing) and logs the run
  to "Screening History". See Stage 7 for schema details.

After rendering, prompt the user:

> Want me to run full `/analyze-property` on any of the PASS rows? Reply with
> row numbers (e.g., "1, 3, 5") or 'no'.

If the user replies with numbers, for each selected row: invoke the
`/analyze-property` pipeline with that row's listing URL as input. Each becomes
its own full deep-dive report (HTML / PDF / Notion per their preference).

### Stage 7 — Notion integration

The screening skill uses **two separate Notion databases**, both under the
same parent page used by `/analyze-property` (reuse that parent — do not
ask for a new one if the config already has it).

Databases:

1. **Screening Results**: one row per candidate property, updated on each
   run. See `references/notion-schema.md` for full schema.

2. **Screening History**: one row per screening run — captures the area,
   filters, timestamp, total candidates found, and PASS count. Useful for:
   "What did I screen last week in Tampa?" queries.

If either database does not exist in the parent page, create it before
writing rows.

---

## Companion workflow with /analyze-property

These two skills are designed to work together:

```
Step 1: /screen-properties Tampa FL --price 300k-500k --limit 10
        → produces table of 10 candidates with PASS/WATCH/SKIP

Step 2: User reviews table, picks top 2-3 PASS rows

Step 3: User says "run full analysis on rows 1 and 3"
        → skill automatically invokes /analyze-property for each URL
        → each becomes a full deep-dive with all 8 metrics + Notion page
```

Matt's typical loop:
- Weekly: run `/screen-properties` on watched areas
- Deep-dive: run `/analyze-property` on top 2-3 PASS rows
- Decide: use Portfolio Scorecard in Notion to pick the one to pursue

---

## Critical rules

1. **Never fabricate data.** If rent or tax is unavailable, say so in the
   Data Quality column. Do not guess silently.
2. **Be honest about data limits.** If many URLs fail to scrape, tell the
   user — do not pretend you have a full picture.
3. **Show assumptions.** Every report includes a footer listing the quick
   screen assumption set (simplified 15 percent OpEx, 25 percent down, live rate).
4. **Current data.** When web-searching for listings, mortgage rates, or
   market averages, include "2026" or "current". Today is April 2026.
5. **Privacy.** Do not persist Notion IDs outside the session.
6. **Not financial advice.** Every report includes the footer disclaimer.
7. **Respect the `--limit`.** If the user says 10, return 10 — not 50. If
   fewer than 10 candidates survive, say so and explain why.

---

## File map

```
screen-properties/
├── SKILL.md                     # This file
├── README.md                    # Quick reference
├── scripts/
│   ├── screener.py              # Quick-screen metric engine
│   ├── filters.py               # Filter parser and applier
│   ├── render_table_html.py     # Dark HTML table renderer
│   ├── render_table_pdf.py      # PDF landscape table renderer
│   ├── render_table_md.py       # Markdown table renderer
│   └── notion_export.py         # Screening Results + History DB writer
├── references/
│   ├── screen-rubric.md         # Quick-screen thresholds (industry-standard)
│   ├── data-schema.md           # CandidateProperty / ScreenResult schemas
│   └── notion-schema.md         # Screening Results + History DB columns
└── examples/
    ├── sample-table.html        # Reference HTML output
    ├── sample-table.pdf         # Reference PDF output
    └── sample-table.md          # Reference markdown output
```

---

## Workflow reminder

When the user runs `/screen-properties [args]`:

1. Read this SKILL.md — done.
2. Read `references/screen-rubric.md` and `references/data-schema.md`.
3. Copy all files in `scripts/` to `/home/claude/` and import them.
4. Execute pipeline stages 1-6.
5. Render table. Ask which PASS rows (if any) to deep-dive.
6. Write to `/mnt/user-data/outputs/` and/or Notion.
7. Present files via `present_files`.
8. If user elected deep-dives, invoke `/analyze-property` for each row.
