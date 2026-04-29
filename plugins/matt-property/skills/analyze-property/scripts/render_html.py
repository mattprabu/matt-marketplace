"""
render_html.py — Generates the dark-themed HTML investment report.

Usage:
    from render_html import render
    html = render(metrics_result)

Output style: dark palette with red accent, DM Sans / DM Mono typography.
The CSS is kept in a separate _CSS string (not an f-string) so that CSS
braces do not conflict with Python formatting.
"""

from html import escape


# ------------------------------------------------------------------
# CSS — plain string (no f-string), so CSS braces are safe
# ------------------------------------------------------------------

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'DM Sans', -apple-system, sans-serif;
  background: #0a0a0a;
  color: #e8e8e8;
  line-height: 1.6;
  padding: 40px 20px;
}
.container { max-width: 1100px; margin: 0 auto; }
.mono { font-family: 'DM Mono', monospace; }
h1 { font-size: 2.2rem; margin-bottom: 8px; font-weight: 700; letter-spacing: -0.02em; }
h2 { font-size: 1.5rem; margin-bottom: 16px; font-weight: 700; color: #fff; }
h3 { font-size: 1.1rem; margin-bottom: 10px; font-weight: 500; color: #ccc; }

.header {
  border-bottom: 1px solid #222;
  padding-bottom: 30px;
  margin-bottom: 30px;
}
.address { color: #888; font-size: 1rem; margin-bottom: 4px; }
.price { font-size: 1.8rem; color: #fff; font-weight: 500; }
.specs { color: #888; font-size: 0.95rem; margin-top: 8px; }

.verdict-banner {
  border: 1px solid;
  border-left: 4px solid;
  border-radius: 8px;
  padding: 24px 28px;
  margin: 30px 0;
}
.verdict-banner .label {
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 700;
}
.verdict-banner .headline {
  font-size: 1.8rem;
  color: #fff;
  margin: 8px 0 6px;
  font-weight: 700;
}
.verdict-banner .reason { color: #bbb; font-size: 1rem; }
.verdict-banner .composite {
  display: inline-block;
  margin-top: 14px;
  padding: 4px 12px;
  border-radius: 4px;
  font-family: 'DM Mono', monospace;
  font-size: 0.85rem;
}

.section { margin: 40px 0; }

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.metric-card {
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 20px;
  position: relative;
}
.metric-card .label {
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: #888;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.metric-card .value {
  font-family: 'DM Mono', monospace;
  font-size: 1.8rem;
  color: #fff;
  font-weight: 500;
}
.metric-card .sub {
  font-size: 0.85rem;
  color: #888;
  margin-top: 6px;
}
.metric-card .score-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
}
.score-2 { background: rgba(29,185,84,0.15); color: #1db954; }
.score-1 { background: rgba(245,166,35,0.15); color: #f5a623; }
.score-0 { background: rgba(229,9,20,0.15); color: #E50914; }

.pc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}
@media (max-width: 800px) { .pc-grid { grid-template-columns: 1fr; } }
.pc-box {
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 20px;
}
.pc-box h3 { margin-bottom: 12px; }
.pc-box ul { list-style: none; }
.pc-box li {
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
  color: #ccc;
  font-size: 0.95rem;
}
.pc-box li:before {
  position: absolute;
  left: 0;
  top: 8px;
  font-size: 0.85rem;
}
.pros li:before { content: "+"; color: #1db954; font-weight: 700; }
.cons li:before { content: "x"; color: #E50914; font-weight: 700; }
.watch li:before { content: "*"; color: #f5a623; font-weight: 700; }

table {
  width: 100%;
  border-collapse: collapse;
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  overflow: hidden;
}
th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #222;
}
th {
  background: #1a1a1a;
  font-size: 0.8rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 500;
}
td { font-family: 'DM Mono', monospace; font-size: 0.9rem; }
tr:last-child td { border-bottom: none; }
.num { text-align: right; color: #fff; }
.num-neg { color: #E50914; }
.num-pos { color: #1db954; }

.risk-section {
  background: #1a1410;
  border: 1px solid #3a2418;
  border-radius: 8px;
  padding: 24px;
}
.risk-list { list-style: none; }
.risk-list li {
  padding: 10px 0 10px 28px;
  position: relative;
  color: #e8b896;
  border-bottom: 1px solid #2a1a10;
}
.risk-list li:last-child { border-bottom: none; }
.risk-list li:before {
  content: "!";
  position: absolute;
  left: 10px;
  top: 10px;
  color: #f5a623;
  font-size: 0.9rem;
  font-weight: 700;
}

.chart-container {
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 24px;
}

details {
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
}
details summary {
  cursor: pointer;
  font-weight: 500;
  color: #ccc;
  font-size: 0.95rem;
}
details[open] summary { margin-bottom: 16px; }

.footer {
  margin-top: 60px;
  padding-top: 24px;
  border-top: 1px solid #222;
  color: #666;
  font-size: 0.8rem;
  text-align: center;
}
.footer .disclaimer {
  max-width: 700px;
  margin: 0 auto 12px;
  line-height: 1.5;
}
"""


# ------------------------------------------------------------------

def render(m: dict) -> str:
    """Produce the full HTML document from a MetricsResult dict."""
    p = m["property"]
    e = m["enrichment"]
    a = m["assumptions"]

    verdict = m["verdict"]
    verdict_color = {"GREEN": "#1db954", "YELLOW": "#f5a623", "RED": "#E50914"}[verdict]
    verdict_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}[verdict]
    verdict_label = {
        "GREEN": "Strong Candidate",
        "YELLOW": "Marginal",
        "RED": "Pass at This Price",
    }[verdict]

    cards_html = _render_metric_cards(m)
    pros_cons_html = _render_pros_cons(m)
    chart_svg = _render_5yr_projection(m, a)
    breakdown_html = _render_breakdown(m)
    comps_html = _render_comps(e, p)
    assumptions_html = _render_assumptions(a, e)

    risks_html = ""
    if m.get("risk_factors"):
        items = "".join("<li>" + escape(r) + "</li>" for r in m["risk_factors"])
        risks_html = (
            '<section class="section risk-section">'
            "<h2>Risk Factors</h2>"
            '<ul class="risk-list">' + items + "</ul>"
            "</section>"
        )

    # Built-in inline style for verdict banner (keeps dynamic colors isolated)
    banner_style = (
        f"background: linear-gradient(135deg, {verdict_color}22 0%, {verdict_color}08 100%);"
        f"border-color: {verdict_color}66;"
        f"border-left-color: {verdict_color};"
    )

    year_built_txt = f"Built {p['year_built']}" if p.get("year_built") else ""
    dom_txt = f"{p['days_on_market']} days on market" if p.get("days_on_market") else ""

    # Assemble the final document
    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>Investment Analysis — {escape(p['address'])}</title>",
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">',
        "<style>",
        _CSS,
        "</style>",
        "</head>",
        "<body>",
        '<div class="container">',

        '<div class="header">',
        f'<div class="address">{escape(p["address"])}</div>',
        f'<div class="price">${p["price"]:,}</div>',
        f'<div class="specs mono">{p["beds"]} bed · {p["baths"]} bath · '
        f'{p["sqft"]:,} sqft {("· " + year_built_txt) if year_built_txt else ""}'
        f' {("· " + dom_txt) if dom_txt else ""}</div>',
        "</div>",

        f'<div class="verdict-banner" style="{banner_style}">',
        f'<div class="label" style="color:{verdict_color}">{verdict_emoji} Verdict</div>',
        f'<div class="headline">{verdict_label}</div>',
        f'<div class="reason">{escape(m["verdict_reason"])}</div>',
        f'<div class="composite" style="background:{verdict_color}33; color:{verdict_color}">'
        f'Composite score: {m["composite_score_pct"]:.0f} percent</div>',
        "</div>",

        '<section class="section">',
        "<h2>Key Metrics</h2>",
        f'<div class="metrics-grid">{cards_html}</div>',
        "</section>",

        '<section class="section">',
        "<h2>Summary</h2>",
        pros_cons_html,
        "</section>",

        risks_html,

        '<section class="section">',
        "<h2>5-Year Cash Flow Projection</h2>",
        f'<div class="chart-container">{chart_svg}</div>',
        "</section>",

        '<section class="section">',
        "<h2>Income and Expense Breakdown</h2>",
        breakdown_html,
        "</section>",

        comps_html,

        '<section class="section">',
        "<details>",
        "<summary>View financial assumptions used</summary>",
        assumptions_html,
        "</details>",
        "</section>",

        '<div class="footer">',
        '<div class="disclaimer">',
        "This analysis is a decision-support tool, not financial advice. Figures are "
        "projections based on listing data and market estimates. Verify all numbers "
        "with your own due diligence, a licensed real estate agent, and a tax or "
        "financial advisor before making any investment decision.",
        "</div>",
        f'<div class="mono">Generated by /analyze-property · {m["analyzed_at"][:10]}</div>',
        "</div>",

        "</div>",
        "</body>",
        "</html>",
    ]

    return "\n".join(html_parts)


# ------------------------------------------------------------------

def _render_metric_cards(m: dict) -> str:
    scores = m["metric_scores"]
    dscr_val = f"{m['dscr']:.2f}" if m.get("dscr") is not None else "n/a"
    cf = m["cash_flow_monthly"]

    cards = [
        _card("Monthly Cash Flow", f"${cf:,.0f}",
              "after all expenses and debt", scores["cash_flow"],
              color_override=("#E50914" if cf < 0 else None)),
        _card("Cap Rate", f"{m['cap_rate'] * 100:.2f}%",
              f"NOI ${m['noi_annual']:,.0f} / price", scores["cap_rate"]),
        _card("Cash-on-Cash", f"{m['coc_return'] * 100:.2f}%",
              f"on ${m['cash_to_close']:,.0f} invested", scores["coc"]),
        _card("DSCR", dscr_val, "debt service coverage", scores["dscr"]),
        _card("1% Rule", f"{m['one_percent_ratio'] * 100:.2f}%",
              "target: 1.00 percent or higher", scores["one_percent"]),
        _card("50% Rule (OpEx)", f"{m['fifty_percent_opex_ratio'] * 100:.1f}%",
              "target: 50 percent or lower", scores["fifty_percent"]),
        _card("5-Year IRR", f"{m['irr_5yr'] * 100:.1f}%",
              "levered, with appreciation", scores["irr"]),
        _card("Break-Even", f"{m['break_even_ratio'] * 100:.1f}%",
              "percent of rent needed to cover costs", scores["fifty_percent"]),
    ]
    return "".join(cards)


def _card(label, value, sub, score, color_override=None):
    badge_class = f"score-{score}"
    badge_text = {2: "STRONG", 1: "OK", 0: "WEAK"}[score]
    value_style = f' style="color:{color_override}"' if color_override else ""
    return (
        '<div class="metric-card">'
        f'<span class="score-badge {badge_class}">{badge_text}</span>'
        f'<div class="label">{escape(label)}</div>'
        f'<div class="value"{value_style}>{escape(value)}</div>'
        f'<div class="sub">{escape(sub)}</div>'
        "</div>"
    )


def _render_pros_cons(m: dict) -> str:
    def box(title, cls, items, empty_msg):
        if not items:
            li_html = '<li style="color:#555">— ' + escape(empty_msg) + " —</li>"
        else:
            li_html = "".join("<li>" + escape(x) + "</li>" for x in items)
        return (
            '<div class="pc-box">'
            f"<h3>{title}</h3>"
            f'<ul class="{cls}">{li_html}</ul>'
            "</div>"
        )

    pros_box = box("Pros", "pros", m.get("pros", []), "no strong positives")
    cons_box = box("Cons", "cons", m.get("cons", []), "no red flags")
    watch_box = box("Watch Items", "watch", m.get("watch_items", []), "nothing to watch")

    return '<div class="pc-grid">' + pros_box + cons_box + watch_box + "</div>"


def _render_5yr_projection(m: dict, a: dict) -> str:
    """Simple bar chart of projected annual cash flow over 5 years."""
    cf_annual = m["cash_flow_annual"]
    rent_growth = a.get("rent_growth_annual", 0.03)
    exp_growth = a.get("expense_growth_annual", 0.03)
    effective_growth = rent_growth - (exp_growth * 0.5)

    values = [cf_annual * ((1 + effective_growth) ** i) for i in range(5)]
    years = [f"Year {i + 1}" for i in range(5)]

    width, height = 760, 240
    pad_l, pad_r, pad_t, pad_b = 60, 20, 30, 50
    chart_w = width - pad_l - pad_r
    chart_h = height - pad_t - pad_b

    max_v = max(max(values), 0)
    min_v = min(min(values), 0)
    if max_v == min_v:
        max_v = max_v + 1000
    v_range = max_v - min_v if max_v != min_v else 1
    zero_y = pad_t + chart_h * (max_v / v_range)

    bar_w = chart_w / len(values) * 0.6
    gap = chart_w / len(values) * 0.4

    bars = []
    for i, v in enumerate(values):
        x = pad_l + i * (bar_w + gap) + gap / 2
        if v >= 0:
            h = chart_h * (v / v_range)
            y = zero_y - h
            color = "#1db954"
        else:
            h = chart_h * (-v / v_range)
            y = zero_y
            color = "#E50914"

        label_y = y - 6 if v >= 0 else y + h + 14

        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
            f'fill="{color}" opacity="0.85" rx="2"/>'
        )
        bars.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{label_y:.1f}" '
            f'text-anchor="middle" fill="#ccc" font-size="11" '
            f'font-family="DM Mono">${v:,.0f}</text>'
        )
        bars.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 15:.1f}" '
            f'text-anchor="middle" fill="#888" font-size="11" '
            f'font-family="DM Sans">{years[i]}</text>'
        )

    zero_line = (
        f'<line x1="{pad_l}" y1="{zero_y:.1f}" x2="{width - pad_r}" y2="{zero_y:.1f}" '
        f'stroke="#333" stroke-width="1"/>'
        f'<text x="{pad_l - 8}" y="{zero_y + 4:.1f}" text-anchor="end" '
        f'fill="#666" font-size="10" font-family="DM Mono">$0</text>'
    )

    svg = (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;max-width:{width}px">'
        + zero_line + "".join(bars) +
        "</svg>"
    )

    caption = (
        '<div style="text-align:center;color:#666;font-size:0.85rem;margin-top:12px">'
        f'Projected annual cash flow — rent grows {rent_growth * 100:.1f} percent '
        f'per year, expenses {exp_growth * 100:.1f} percent per year'
        "</div>"
    )
    return svg + caption


def _render_breakdown(m: dict) -> str:
    a = m["assumptions"]
    rows = [
        ("Gross rent (annual)", m["gross_rent_annual"], "pos"),
        ("Property taxes", -m["tax_annual"], "neg"),
        ("Insurance", -m["insurance_annual"], "neg"),
        ("HOA", -m["hoa_annual"], "neg"),
        (f"Vacancy ({a['vacancy_pct'] * 100:.0f}%)",
         -m["vacancy_annual"], "neg"),
        (f"Property management ({a['management_pct'] * 100:.0f}%)",
         -m["management_annual"], "neg"),
        (f"Maintenance ({a['maintenance_pct'] * 100:.0f}%)",
         -m["maintenance_annual"], "neg"),
        (f"CapEx reserve ({a['capex_pct'] * 100:.0f}%)",
         -m["capex_annual"], "neg"),
    ]

    row_parts = []
    for label, val, kind in rows:
        cls = "num-neg" if kind == "neg" else "num-pos"
        sign = "-" if val < 0 else ""
        row_parts.append(
            "<tr>"
            f"<td>{escape(label)}</td>"
            f'<td class="num {cls}">{sign}${abs(val):,.0f}</td>'
            "</tr>"
        )

    noi_row = (
        '<tr style="border-top:2px solid #333">'
        '<td style="font-weight:700">Net Operating Income (NOI)</td>'
        f'<td class="num" style="color:#fff;font-weight:700">${m["noi_annual"]:,.0f}</td>'
        "</tr>"
    )
    debt_row = (
        "<tr>"
        "<td>Debt service (P and I)</td>"
        f'<td class="num num-neg">-${m["debt_service_annual"]:,.0f}</td>'
        "</tr>"
    )
    cf_cls = "num-pos" if m["cash_flow_annual"] >= 0 else "num-neg"
    cf_sign = "" if m["cash_flow_annual"] >= 0 else "-"
    cf_row = (
        '<tr style="border-top:2px solid #333">'
        '<td style="font-weight:700">Annual cash flow</td>'
        f'<td class="num {cf_cls}" style="font-weight:700">'
        f'{cf_sign}${abs(m["cash_flow_annual"]):,.0f}</td>'
        "</tr>"
    )

    return (
        "<table>"
        '<thead><tr><th>Line Item</th><th class="num">Annual</th></tr></thead>'
        "<tbody>"
        + "".join(row_parts) + noi_row + debt_row + cf_row +
        "</tbody></table>"
    )


def _render_comps(e: dict, p: dict) -> str:
    comps = e.get("comps") or []
    if not comps:
        return ""

    listing_ppsf = p["price"] / p["sqft"] if p.get("sqft") else 0
    avg_ppsf = e.get("comps_avg_price_per_sqft")

    row_parts = []
    for c in comps:
        row_parts.append(
            "<tr>"
            f'<td style="font-family:\'DM Sans\'">{escape(c["address"])}</td>'
            f'<td class="num">${c["sold_price"]:,}</td>'
            f'<td class="num">{c["sqft"]:,}</td>'
            f'<td class="num">${c["price_per_sqft"]:.0f}</td>'
            f'<td style="font-family:\'DM Sans\';color:#888">{escape(c["sold_date"])}</td>'
            "</tr>"
        )

    delta = ""
    if avg_ppsf and listing_ppsf:
        diff_pct = (listing_ppsf / avg_ppsf - 1) * 100
        color = "#1db954" if diff_pct <= 0 else "#E50914"
        label = "below" if diff_pct <= 0 else "above"
        delta = (
            '<div style="margin-top:12px;padding:12px;background:#1a1a1a;'
            'border-radius:6px;color:#ccc;font-size:0.9rem">'
            f'Subject property at <span class="mono">${listing_ppsf:.0f}/sqft</span> '
            f'is <span style="color:{color};font-weight:500">'
            f'{abs(diff_pct):.1f} percent {label}</span> '
            f'comps average (<span class="mono">${avg_ppsf:.0f}/sqft</span>)'
            "</div>"
        )

    return (
        '<section class="section">'
        "<h2>Recent Comparable Sales</h2>"
        "<table>"
        "<thead><tr>"
        "<th>Address</th>"
        '<th class="num">Sold Price</th>'
        '<th class="num">Sqft</th>'
        '<th class="num">$/Sqft</th>'
        "<th>Sold</th>"
        "</tr></thead>"
        "<tbody>" + "".join(row_parts) + "</tbody>"
        "</table>"
        + delta +
        "</section>"
    )


def _render_assumptions(a: dict, e: dict) -> str:
    rent_src = e.get("rent_estimate", {}).get("source_used", "unknown")
    tax_src = e.get("tax_annual", {}).get("source", "unknown")

    rows = [
        ("Down payment", f"{a['down_payment_pct'] * 100:.0f}%"),
        ("Interest rate", f"{a['interest_rate'] * 100:.2f}%"),
        ("Loan term", f"{a['loan_term_years']} years"),
        ("Closing costs", f"{a['closing_costs_pct'] * 100:.1f}% of price"),
        ("Vacancy", f"{a['vacancy_pct'] * 100:.0f}% of rent"),
        ("Property management", f"{a['management_pct'] * 100:.0f}% of rent"),
        ("Maintenance", f"{a['maintenance_pct'] * 100:.0f}% of rent"),
        ("CapEx reserve", f"{a['capex_pct'] * 100:.0f}% of rent"),
        ("Insurance", f"{a['insurance_pct'] * 100:.2f}% of price per year"),
        ("Annual rent growth", f"{a['rent_growth_annual'] * 100:.1f}%"),
        ("Annual appreciation", f"{a['appreciation_annual'] * 100:.1f}%"),
        ("Rent source", escape(rent_src)),
        ("Tax source", escape(tax_src)),
    ]

    body = "".join(
        "<tr>"
        f'<td style="font-family:\'DM Sans\'">{escape(label)}</td>'
        f'<td class="num">{escape(val)}</td>'
        "</tr>"
        for label, val in rows
    )
    return "<table>" + body + "</table>"
