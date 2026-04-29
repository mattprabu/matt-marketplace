# Notion Schema — /screen-properties

The skill uses **two separate databases** under the same parent page that
`/analyze-property` uses. Both are created on first run if missing.

---

## Parent page setup

Reuse the parent page from `/analyze-property`. If the session config
(`/home/claude/.property-analyzer-config.json`) has one, use it. Otherwise
ask the user once:

> Paste the URL of the Notion parent page where I should save screening
> results and history. I will create two databases inside it:
> Screening Results and Screening History.

Store in the session config only.

---

## Database 1: Screening Results

One row per **candidate property** from any screening run. Rows accumulate
over time — each run adds its candidates. Use the `Run ID` column to filter
by individual run.

### Columns

| Name | Type | Notes |
|---|---|---|
| Property | Title | Full address |
| Verdict | Select | Options: Pass, Watch, Skip (color-tagged) |
| Price | Number (dollar) | Asking price |
| Beds | Number | |
| Sqft | Number | |
| Est Cash Flow | Number (dollar) | Estimated monthly cash flow |
| Cap Rate | Number (percent) | Rough cap rate |
| 1% Rule | Number (percent) | Rent-to-price ratio |
| Data Quality | Select | Options: Verified, Partial, Insurance estimated |
| Screen Date | Date | ISO date |
| Listing URL | URL | Link to the listing site |
| Run ID | Text | Ties row to a Screening History row |

### Useful views (suggest to user manually)

- **By Verdict** (board, grouped on Verdict)
- **Latest PASSes** (table, filter Verdict = Pass, sort Screen Date desc, limit 20)
- **By Run** (table, filter Run ID, sort Cap Rate desc)

---

## Database 2: Screening History

One row per **screening run**. Captures the criteria, timestamp, and summary
counts. Lets the user answer "what did I screen last week?"

### Columns

| Name | Type | Notes |
|---|---|---|
| Run | Title | Format: `[Area] — [Date]` e.g., `Tampa FL — 2026-04-21` |
| Areas | Text | Comma-separated area spec |
| Price Range | Text | e.g., `$200k-$400k` or `any` |
| Other Filters | Text | compact summary, e.g., `beds 3+, sfh, DOM<60` |
| Candidates Found | Number | Total URLs fetched before filters |
| Pass Count | Number | |
| Watch Count | Number | |
| Skip Count | Number | |
| Timestamp | Date with time | |
| Run ID | Text | Unique id (UUID) |

### Useful views

- **Recent runs** (table, sort Timestamp desc, limit 10)
- **By area** (board, grouped on Areas — messy if many combos, but useful
  for Matt's recurring markets like Tampa / Land O Lakes)

---

## Check-before-create pattern

On first Notion export in a session:

1. `notion-fetch` the parent page to list its children
2. If "Screening Results" database exists, use it
3. If missing, create it with the schema above
4. Same for "Screening History"
5. Write the history row first (get the Run ID)
6. Write each result row with that Run ID

Do not create duplicate databases. If a database with the same name
already exists but has different columns (e.g., user modified it), do
not overwrite — use what is there and log any column mismatches to the
user as a warning.

---

## Cross-skill reuse

Rows in **Portfolio Scorecard** (owned by `/analyze-property`) and rows in
**Screening Results** (owned by this skill) are NOT automatically linked.
When the user runs a deep-dive from a screener row:

1. `/analyze-property` creates its own page under the parent
2. The new Portfolio Scorecard entry is NOT the same record as the
   Screening Results row — they are separate tables with different schemas

This is intentional — the screener captures the "wide" view and the
analyzer captures the "deep" view. Linking them is the user's job in Notion
(via relation properties added manually) if they want that.
