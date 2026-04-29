# /analyze-property — Real Estate Investment Analyzer Skill

Buy and Hold rental property analyzer for US residential real estate. Screens
properties against industry-standard metrics and produces a GREEN / YELLOW /
RED investment verdict.

**Dependencies**: Only the built-in `web_fetch` and `web_search` tools, plus
Notion MCP (optional, for `--notion` output). No paid APIs required.

## Install

Drop the `analyze-property/` folder into your Claude skills directory, or
upload as a custom skill. The skill activates on the `/analyze-property`
trigger.

## Usage

```
/analyze-property https://www.example.com/homes/...
/analyze-property [paste MLS listing text]
/analyze-property [attach an MLS PDF]
/analyze-property 123 Main St Tampa FL, $350k, 3/2, 1800sqft
/analyze-property compare         (after analyzing 2+ in the session)
```

Optional output flags:

```
/analyze-property [input] --html       (dark-themed HTML, default)
/analyze-property [input] --pdf        (print-ready PDF)
/analyze-property [input] --notion     (Notion page + portfolio DB row)
/analyze-property [input] --all        (all three)
```

## What you get

**Per property:**

- 8 key metrics: cash flow, cap rate, CoC, DSCR, 1 percent rule, 50 percent
  rule, 5-year IRR, break-even ratio
- GREEN / YELLOW / RED verdict with composite score
- Pros / Cons / Watch items breakdown
- Risk factors (FL insurance exposure, old builds, stale listings, etc.)
- Comps comparison (dollars per sqft vs. recent sales)
- Full income and expense breakdown
- 5-year projected cash flow chart (SVG)

**Comparison mode (2 or more properties):**

- Side-by-side metric table with winner highlighting
- Final recommendation with confidence level
- Auto-updates Notion Portfolio Scorecard

## File map

```
analyze-property/
├── SKILL.md                     # Main skill spec and workflow
├── README.md                    # This file
├── scripts/
│   ├── analyzer.py              # Core metric engine
│   ├── render_html.py           # Dark-theme HTML output
│   ├── render_pdf.py            # PDF output
│   ├── notion_export.py         # Notion block and schema builder
│   └── compare.py               # Comparison mode
├── references/
│   ├── data-schema.md           # Data dict schemas
│   ├── scoring-rubric.md        # Thresholds and weights
│   └── notion-schema.md         # Notion page and DB schema
└── examples/
    ├── sample-output.html       # Sample HTML report
    ├── sample-output.pdf        # Sample PDF report
    └── sample-comparison.html   # Sample comparison report
```

## Assumptions (editable per analysis)

Smart defaults applied first, then the user can override via a single
consolidated prompt:

- Down payment: 25 percent
- Interest rate: live-fetched via web search
- Vacancy / Mgmt / Maint / CapEx: 8 / 10 / 5 / 5 percent of gross rent
- Insurance: 0.5 percent nationally, 1.2 percent FL coastal, 0.8 percent FL inland
- Rent growth: 3 percent per year
- Appreciation: 3.5 percent per year
- Hold period: 5 years

## Scoring

Each of 8 metrics scores 0, 1, or 2. Weighted composite determines verdict:

- 80 percent or higher → GREEN (strong candidate)
- 55 to 79 percent → YELLOW (marginal)
- Below 55 percent → RED (pass)

**Hard-override RED** if: negative cash flow AND DSCR below 1.0, OR priced
above 110 percent of comps, OR critical data missing, OR 5-year IRR below
5 percent.

**Hard-override GREEN** requires all: 1 percent rule passes, cap rate at or
above market, CoC at or above 8 percent, DSCR at or above 1.25, cash flow
at or above 200 dollars per month, price at or below comps.

## Not financial advice

Every report includes this disclaimer. The skill is a decision-support tool —
verify all numbers with your own due diligence and a licensed agent before
buying.
