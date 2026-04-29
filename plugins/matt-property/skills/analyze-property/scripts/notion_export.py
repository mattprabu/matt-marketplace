"""
notion_export.py — Notion page and portfolio database helpers.

Build the structured content the skill passes to the Notion MCP tools.
The actual Notion API calls happen via the Notion MCP tools that Claude
invokes — this script just builds the block payloads and database schema.

Usage pattern (executed by Claude, not imported and called from here):
    1. Build the page title:   title = build_property_page_title(result)
    2. Build the page content: blocks = build_property_page_blocks(result)
    3. Call the Notion MCP tool to create the page under the parent.
    4. Build DB row props:     props = build_portfolio_row(result, page_url)
    5. Call the Notion MCP tool to add the row to Portfolio Scorecard.
"""


def build_property_page_title(m: dict) -> str:
    """Generate the Notion page title: '[Address] — [Emoji] [Verdict]'."""
    addr = m["property"]["address"]
    emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[m["verdict"]]
    return f"{addr} — {emoji} {m['verdict']}"


def build_property_page_blocks(m: dict) -> list[dict]:
    """Build the body content blocks for a property analysis page."""
    p = m["property"]
    e = m["enrichment"]
    blocks: list[dict] = []

    # Header line
    year_str = f" · Built {p['year_built']}" if p.get("year_built") else ""
    blocks.append(_heading(
        f"${p['price']:,} · {p['beds']} bd / {p['baths']} ba · "
        f"{p['sqft']:,} sqft{year_str}", 2
    ))

    # Verdict callout
    callout_icon = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[m["verdict"]]
    callout_color = {
        "GREEN": "green_background",
        "YELLOW": "yellow_background",
        "RED": "red_background",
    }[m["verdict"]]
    blocks.append(_callout(
        f"{m['verdict']} — {m['verdict_reason']}",
        icon=callout_icon,
        color=callout_color,
    ))
    blocks.append(_paragraph(
        f"Composite score: {m['composite_score_pct']:.0f} percent"
    ))

    # Key metrics
    blocks.append(_heading("Key Metrics", 2))
    blocks.append(_metrics_toggle(m))

    # Pros
    if m.get("pros"):
        blocks.append(_heading("Pros", 3))
        for pro in m["pros"]:
            blocks.append(_bullet(pro))

    # Cons
    if m.get("cons"):
        blocks.append(_heading("Cons", 3))
        for con in m["cons"]:
            blocks.append(_bullet(con))

    # Watch items
    if m.get("watch_items"):
        blocks.append(_heading("Watch Items", 3))
        for item in m["watch_items"]:
            blocks.append(_bullet(item))

    # Risk factors
    if m.get("risk_factors"):
        blocks.append(_heading("Risk Factors", 2))
        for risk in m["risk_factors"]:
            blocks.append(_callout(risk, icon="⚠️", color="orange_background"))

    # Cash flow summary
    blocks.append(_heading("Cash Flow Summary", 2))
    blocks.append(_paragraph(
        f"Gross rent: ${m['gross_rent_annual']:,.0f}/yr · "
        f"Operating expenses: ${m['total_opex_annual']:,.0f}/yr · "
        f"NOI: ${m['noi_annual']:,.0f}/yr"
    ))
    blocks.append(_paragraph(
        f"Debt service: ${m['debt_service_annual']:,.0f}/yr · "
        f"Annual cash flow: ${m['cash_flow_annual']:,.0f}"
    ))

    # Comps toggle
    if e.get("comps"):
        comp_lines = [
            f"{c['address']} — ${c['sold_price']:,} ({c['sqft']:,} sqft, "
            f"${c['price_per_sqft']:.0f}/sqft), sold {c['sold_date']}"
            for c in e["comps"]
        ]
        if e.get("comps_avg_price_per_sqft") and p.get("sqft"):
            listing_ppsf = p["price"] / p["sqft"]
            avg = e["comps_avg_price_per_sqft"]
            delta = (listing_ppsf / avg - 1) * 100
            comp_lines.insert(
                0,
                f"Subject at ${listing_ppsf:.0f}/sqft vs comps avg ${avg:.0f}/sqft "
                f"({delta:+.1f} percent)"
            )
        blocks.append(_toggle("Comparable sales", [_bullet(x) for x in comp_lines]))

    # Assumptions toggle
    a = m["assumptions"]
    assump_lines = [
        f"Down payment: {a['down_payment_pct']*100:.0f} percent",
        f"Interest rate: {a['interest_rate']*100:.2f} percent",
        f"Loan term: {a['loan_term_years']} years",
        f"Vacancy / Mgmt / Maint / CapEx: "
        f"{a['vacancy_pct']*100:.0f} / {a['management_pct']*100:.0f} / "
        f"{a['maintenance_pct']*100:.0f} / {a['capex_pct']*100:.0f} percent",
        f"Insurance: {a['insurance_pct']*100:.2f} percent of price per year",
        f"Rent growth: {a['rent_growth_annual']*100:.1f} percent per year",
        f"Appreciation: {a['appreciation_annual']*100:.1f} percent per year",
        f"Rent source: {e.get('rent_estimate', {}).get('source_used', 'n/a')}",
        f"Tax source: {e.get('tax_annual', {}).get('source', 'n/a')}",
    ]
    blocks.append(_toggle(
        "Financial assumptions used",
        [_bullet(x) for x in assump_lines]
    ))

    # Sources
    if p.get("listing_url"):
        blocks.append(_heading("Sources", 3))
        blocks.append(_bullet(f"Listing: {p['listing_url']}"))

    # Disclaimer
    blocks.append(_divider())
    blocks.append(_paragraph(
        "Decision-support analysis, not financial advice. Verify all numbers "
        "independently before purchasing.",
        italic=True,
    ))

    return blocks


def build_portfolio_row(m: dict, page_url: str | None = None) -> dict:
    """Build Notion database row properties for the Portfolio Scorecard."""
    p = m["property"]
    return {
        "Property": p["address"],
        "Verdict": m["verdict"].capitalize(),
        "Price": p["price"],
        "Monthly Cash Flow": round(m["cash_flow_monthly"], 2),
        "Cap Rate": round(m["cap_rate"] * 100, 2),
        "CoC": round(m["coc_return"] * 100, 2),
        "DSCR": round(m["dscr"], 2) if m.get("dscr") is not None else None,
        "Analysis Date": m["analyzed_at"][:10],
        "Link to Page": page_url,
    }


def portfolio_db_schema() -> dict:
    """Schema for creating the Portfolio Scorecard database."""
    return {
        "name": "Portfolio Scorecard",
        "columns": [
            {"name": "Property", "type": "title"},
            {
                "name": "Verdict", "type": "select",
                "options": [
                    {"name": "Green", "color": "green"},
                    {"name": "Yellow", "color": "yellow"},
                    {"name": "Red", "color": "red"},
                ],
            },
            {"name": "Price", "type": "number", "number_format": "dollar"},
            {"name": "Monthly Cash Flow", "type": "number", "number_format": "dollar"},
            {"name": "Cap Rate", "type": "number", "number_format": "percent"},
            {"name": "CoC", "type": "number", "number_format": "percent"},
            {"name": "DSCR", "type": "number"},
            {"name": "Analysis Date", "type": "date"},
            {"name": "Link to Page", "type": "url"},
        ],
    }


# ------------------------------------------------------------------
# Block builders — Notion-compatible dicts
# ------------------------------------------------------------------

def _text(content: str, italic: bool = False, bold: bool = False) -> dict:
    return {
        "type": "text",
        "text": {"content": content},
        "annotations": {"italic": italic, "bold": bold},
        "plain_text": content,
    }


def _heading(content: str, level: int) -> dict:
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": [_text(content)]},
    }


def _paragraph(content: str, italic: bool = False) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [_text(content, italic=italic)]},
    }


def _bullet(content: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [_text(content)]},
    }


def _callout(content: str, icon: str, color: str) -> dict:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [_text(content)],
            "icon": {"type": "emoji", "emoji": icon},
            "color": color,
        },
    }


def _toggle(summary: str, children: list[dict]) -> dict:
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [_text(summary, bold=True)],
            "children": children,
        },
    }


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _metrics_toggle(m: dict) -> dict:
    """Toggle containing metric bullets, keeping the page compact."""
    dscr = f"{m['dscr']:.2f}" if m.get("dscr") is not None else "n/a"
    one_pct_pass = "pass" if m["one_percent_pass"] else "fail"
    fifty_pct_pass = "pass" if m["fifty_percent_pass"] else "fail"
    lines = [
        f"Monthly cash flow: ${m['cash_flow_monthly']:,.0f}",
        f"Cap rate: {m['cap_rate']*100:.2f} percent",
        f"Cash-on-cash: {m['coc_return']*100:.2f} percent",
        f"DSCR: {dscr}",
        f"1 percent rule: {m['one_percent_ratio']*100:.2f} percent ({one_pct_pass})",
        f"50 percent rule: {m['fifty_percent_opex_ratio']*100:.1f} percent "
        f"opex ratio ({fifty_pct_pass})",
        f"5-year IRR: {m['irr_5yr']*100:.1f} percent",
        f"Cash to close: ${m['cash_to_close']:,.0f}",
    ]
    return _toggle("Metrics (click to expand)", [_bullet(x) for x in lines])
