---
name: analyze-property
description: >
  Analyzes a single US residential property for Buy and Hold rental
  investment. Triggers on /analyze-property followed by a listing URL, MLS
  paste, PDF, or manual entry (address, price, beds, sqft). Runs a 7-stage
  pipeline: ingest, enrich (rent, tax, HOA, comps via web_search and
  web_fetch), hybrid assumption override, compute 8 metrics (cap rate,
  cash-on-cash, DSCR, cash flow, 1 percent rule, 50 percent rule, 5-year
  IRR, break-even), score against industry-standard thresholds, render
  dark HTML, PDF, or Notion page per user flags. Produces a GREEN YELLOW
  RED verdict with composite score and hard-override rules. Supports
  comparison mode for 2+ properties in one session and maintains a Notion
  Portfolio Scorecard database. Uses only web_fetch and web_search, no
  paid APIs. Never use without the /analyze-property trigger.
trigger: /analyze-property
version: 1.0.0
---

# Analyze Property — Buy and Hold Investment Analyzer

## Purpose

Given a property (URL from any listing site, MLS paste, PDF, or manual entry),
produce a **GREEN / YELLOW / RED** investment verdict for Buy and Hold rental
strategy, backed by industry-standard metrics.

This skill is **not financial advice** — it is a decision-support tool that
applies consistent math and scoring so the user can screen many properties in
the time it used to take to analyze one.

---

## When to trigger

Trigger **only** when the user message starts with `/analyze-property`.

Supported input patterns after the trigger:

1. **URL**: `/analyze-property https://www.example.com/homes/...` (any listing site)
2. **Paste**: `/analyze-property` followed by a block of MLS or listing text
3. **Manual**: `/analyze-property 123 Main St, Tampa FL, $350k, 3/2, 1800sqft`
4. **PDF upload**: `/analyze-property` with a PDF attachment (MLS sheet)
5. **Comparison**: `/analyze-property compare` (uses results from earlier in session)

If the message does not match any of the above, ask the user to clarify. **Do
not** attempt analysis without the trigger.

---

## The 7-stage pipeline

Execute stages in order. Do not skip stages. If a stage fails, report which
stage failed and why — do not silently proceed with missing data.

### Stage 1 — Ingest

Extract raw property data from the input. The skill is **listing-site agnostic**
— it works with Zillow, Redfin, Realtor.com, local MLS sites, or any other
real estate listing page.

- **URL**: Use `web_fetch` on the provided URL. Extract these fields from the
  rendered page content:
  - address, list price, beds, baths, sqft
  - year built, lot size, property type
  - HOA monthly fee if listed
  - property taxes if listed
  - any rent estimate displayed on the page
  - days on market if visible

  If `web_fetch` returns content that looks blocked or empty (common for
  aggressive anti-bot sites), tell the user the URL could not be read and
  ask them to paste the listing text instead. Do **not** guess fields.

- **Text/PDF paste**: Parse for the same fields using text patterns. For PDFs,
  read the file from `/mnt/user-data/uploads/` first.

- **Manual**: Parse comma-separated or key:value input.

Normalize into a `PropertyData` dict (see `references/data-schema.md`).

**Fail-fast rule:** if price OR beds OR sqft are missing after this stage,
stop and ask the user to provide them manually. The analysis cannot proceed
without these three.

### Stage 2 — Enrich

Fetch external data that was not in the listing. This stage is **best-effort** —
if a source fails, log it and continue, but flag the missing data in the final
report.

Fetch the following (in this priority order):

1. **Rent estimate** (critical, blocks verdict if missing):
   - If a rent estimate was already captured in Stage 1, use it as the primary.
   - Run `web_search` for `"[city] [state] [beds] bedroom rent average 2026"`
     to get a market range.
   - Run `web_search` for `"rentometer [zip] [beds] bedroom"` — if a result
     shows a median number, extract it.
   - If nothing returns, **ask the user** for their rent estimate — do not
     fabricate.

2. **Tax history** (uses listing tax if available, else):
   - `web_search` for `"[county] [state] property appraiser [address]"` and
     `web_fetch` the top county appraiser result to extract annual tax.
   - If unavailable, estimate at 1.1 percent of price for US average, 0.9
     percent for FL. Flag this as an estimated assumption in the report.

3. **HOA/Condo fees** (already in listing, or ask the user — do not guess).

4. **Neighborhood data** (optional — only if time permits, these are flavor):
   - `web_search` for `"[zip] crime rate 2026"`
   - `web_search` for `"[zip] schools rating"`
   - `web_search` for `"[address] walk score"`

5. **Comparable sales**:
   - `web_search` for `"[zip] recently sold [beds] bedroom [baths] bath"` and
     pull 3 to 5 recent sales with price, sqft, and sold date.
   - Compute average dollars per sqft for the comps and compare to the subject.

Build an `EnrichmentData` dict. Document any sources that failed in the
`missing_data` field.

### Stage 3 — Assumptions (Hybrid)

Load smart defaults, then prompt the user with a single consolidated override
message.

**Smart defaults** (2026 US averages):

- Down payment: **25 percent** (investor standard)
- Interest rate: **live-fetched** — run `web_search` for `"current 30-year
  investment property mortgage rate 2026"` and extract the rate
- Loan term: **30 years**
- Closing costs: **3 percent** of purchase price
- Vacancy: **8 percent** of gross rent
- Property management: **10 percent** of gross rent
- Maintenance: **5 percent** of gross rent
- CapEx reserve: **5 percent** of gross rent
- Insurance: **0.5 percent** of price per year (national), **1.2 percent** for
  FL coastal, **0.8 percent** for FL inland
- Rent growth: **3 percent** annually
- Expense growth: **3 percent** annually
- Appreciation: **3.5 percent** annually (nationwide average)
- Hold period: **5 years**
- Sale costs: **6 percent** of sale price (agent + closing)

**Override prompt** — show the user a single compact summary of the defaults
applied and ask:

> "Override any of these before I run the numbers? Reply 'go' to accept, or
> list changes like 'down 20%, rate 7.25%, rent 2400'."

Wait for their response. Do not compute Stage 4 until they reply.

### Stage 4 — Compute metrics

Run `scripts/analyzer.py` (copy from skill folder to `/home/claude/`) with the
populated `PropertyData`, `EnrichmentData`, and `Assumptions` dicts.

The script computes:

- Gross rent (monthly, annual)
- Operating expenses (taxes, insurance, HOA, vacancy, management, maintenance, capex)
- NOI (Net Operating Income)
- Debt service (monthly P&I via standard amortization)
- Monthly cash flow
- Cash required to close (down payment plus closing costs)
- Cap rate (NOI divided by price)
- Cash-on-Cash return
- DSCR (Debt Service Coverage Ratio)
- 1 percent rule check
- 50 percent rule check
- 5-year levered IRR (includes appreciation and sale at year 5)
- Break-even ratio

Returns a `MetricsResult` dict.

### Stage 5 — Score and Verdict

Apply industry-standard thresholds (see `references/scoring-rubric.md` for
full details).

Each metric scores on a 0 to 2 scale:

- **0** = fail (red flag)
- **1** = marginal (yellow)
- **2** = strong (green)

Weighted composite score determines the verdict:

- **80 percent or higher** of max → GREEN (strong candidate)
- **55 to 79 percent** → YELLOW (marginal)
- **Below 55 percent** → RED (pass)

**Hard overrides** (force RED regardless of composite):

- Monthly cash flow below zero AND DSCR below 1.0
- Price above 110 percent of comps average dollars per sqft
- Missing critical data (rent, taxes, or price) after Stage 2 best-effort
- 5-year IRR below 5 percent (worse than risk-free Treasury)

**Hard overrides** (force GREEN, requires all):

- 1 percent rule passes
- Cap rate at or above market median for the zip
- CoC at or above 8 percent
- DSCR at or above 1.25
- Cash flow at or above 200 dollars per month
- Price at or below comps average dollars per sqft

### Stage 6 — Render output (dispatcher)

Ask the user which format(s) they want — or parse from the original trigger
message if they specified one (for example: `/analyze-property [URL] --html --notion`).

Supported formats:

- `--html` → dark-themed HTML report saved to `/mnt/user-data/outputs/`
- `--pdf` → PDF report via ReportLab saved to `/mnt/user-data/outputs/`
- `--notion` → new page under the parent page (see Stage 7)
- `--all` → all three

If no format flag is given, default to `--html` and ask if the user also wants
Notion.

**Rendering:**

- HTML: use `scripts/render_html.py`. Inline SVG for the metric dashboard and
  5-year projection chart. Palette: `#E50914` red accent, `#0a0a0a` background,
  DM Sans / DM Mono fonts.
- PDF: use `scripts/render_pdf.py` (ReportLab). Same data, print-friendly layout.
- Notion: use `scripts/notion_export.py`. See Stage 7 for details.

### Stage 7 — Notion integration

If `--notion` is requested (or the user opts in when prompted):

1. **First run in a session**: ask the user for the parent page URL or page ID.
   Store it in `/home/claude/.property-analyzer-config.json` for the session.
   The config does not persist across conversations — the user will be
   re-prompted in future sessions. This is intentional to avoid leaking IDs
   across chats.

2. **Create a new child page** under the parent, titled:

   `[Address] — [Verdict Emoji] [Verdict Label]`

   Example: `4521 Oak Ridge Dr, Tampa FL — 🟢 GREEN`

3. **Page content structure**:
   - Heading with address and price
   - Verdict callout block (green, yellow, or red)
   - Metrics table (key numbers)
   - Assumptions used (collapsible toggle)
   - Pros, Cons, and Watch items as bulleted lists
   - Risk factors as amber callouts
   - Source links (listing, comps, rent data)
   - Disclaimer footer

4. **Portfolio tracking**: after creating the property page, append a row to
   a database inside the parent page called `Portfolio Scorecard`. If the
   database does not exist, create it first with this schema:
   - Property (title)
   - Verdict (select: Green/Yellow/Red)
   - Price (number, dollar format)
   - Monthly Cash Flow (number, dollar format)
   - Cap Rate (number, percent format)
   - CoC (number, percent format)
   - DSCR (number)
   - Analysis Date (date)
   - Link to Page (url)

   See `references/notion-schema.md` for full property definitions.

---

## Comparison mode

If the user triggers `/analyze-property compare`:

1. Look back in the conversation for all `MetricsResult` objects produced
   this session.
2. If fewer than 2 exist, tell the user they need to analyze at least 2
   properties first.
3. Use `scripts/compare.py` to build a side-by-side comparison table with
   all key metrics.
4. Highlight the winner for each metric (best cash flow, best cap rate, etc.).
5. Give a final recommendation: which property (if any) to pursue, with
   confidence level.
6. Render in the same format(s) the user originally used.
7. If Notion is active, also create a comparison page under the parent.

---

## Critical rules

1. **Never fabricate data.** If rent, tax, or comps cannot be found, ask the
   user or flag the field as missing in the report.
2. **Always show assumptions.** Every report must list the financial
   assumptions used so the user can verify.
3. **Math must be traceable.** Include a "financial assumptions used"
   collapsible section in every output.
4. **Current data.** When searching for mortgage rates, rent benchmarks, or
   market averages, include "2026" or "current" in the query. Today's date
   is April 2026.
5. **Privacy.** Never save Notion parent page IDs or user tokens to persistent
   storage outside the current session.
6. **Not financial advice.** Every report must include a footer disclaimer.
7. **Do not skip the Stage 3 override prompt.** Even if defaults look fine,
   the user gets a chance to override before computation. This is the hybrid
   contract.

---

## File map

```
analyze-property/
├── SKILL.md                     # This file — pipeline spec and workflow
├── README.md                    # Quick reference for humans
├── scripts/
│   ├── analyzer.py              # Metric computation engine
│   ├── render_html.py           # Dark-themed HTML report
│   ├── render_pdf.py            # PDF output via ReportLab
│   ├── notion_export.py         # Notion page and portfolio DB builder
│   └── compare.py               # Comparison mode
├── references/
│   ├── data-schema.md           # Data dict schemas
│   ├── scoring-rubric.md        # Threshold logic with weights
│   └── notion-schema.md         # Notion page and DB schema
└── examples/
    ├── sample-output.html       # Reference HTML output
    ├── sample-output.pdf        # Reference PDF output
    └── sample-comparison.html   # Reference comparison output
```

---

## Workflow reminder

When the user runs `/analyze-property [input]`:

1. Read this SKILL.md — done.
2. Read `references/scoring-rubric.md` and `references/data-schema.md`.
3. Copy all files in `scripts/` to `/home/claude/` and import them.
4. Execute pipeline stages 1 through 7.
5. Present results. Ask for format preference if not specified.
6. Save outputs to `/mnt/user-data/outputs/` and/or create Notion page.
7. Present files via the `present_files` tool.
