"""
render_table_html.py — Dark-themed HTML table for screening results.

Usage:
    from render_table_html import render
    html = render(screening_run)
"""

from html import escape


# CSS kept as plain string so braces don't collide with f-strings
_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'DM Sans', -apple-system, sans-serif;
  background: #0a0a0a;
  color: #e8e8e8;
  line-height: 1.5;
  padding: 40px 20px;
}
.container { max-width: 1400px; margin: 0 auto; }

h1 { font-size: 1.9rem; font-weight: 700; margin-bottom: 6px; letter-spacing: -0.02em; }
.sub { color: #888; font-size: 0.9rem; margin-bottom: 8px; }
.criteria-line {
  color: #aaa; font-size: 0.85rem;
  font-family: 'DM Mono', monospace;
  padding: 10px 14px;
  background: #141414;
  border: 1px solid #222;
  border-radius: 6px;
  margin-bottom: 20px;
  display: inline-block;
}

.summary-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.pill {
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-family: 'DM Mono', monospace;
  border: 1px solid;
}
.pill-pass { background: rgba(29,185,84,0.12); color: #1db954; border-color: rgba(29,185,84,0.3); }
.pill-watch { background: rgba(245,166,35,0.12); color: #f5a623; border-color: rgba(245,166,35,0.3); }
.pill-skip { background: rgba(229,9,20,0.12); color: #E50914; border-color: rgba(229,9,20,0.3); }
.pill-total { background: #141414; color: #ccc; border-color: #333; }

.data-issues {
  background: #1a1410;
  border: 1px solid #3a2418;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
  color: #e8b896;
  font-size: 0.88rem;
}
.data-issues .label {
  color: #f5a623;
  font-weight: 700;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 6px;
  display: block;
}
.data-issues ul { list-style: none; padding-left: 14px; }
.data-issues li:before { content: "• "; color: #f5a623; }

table {
  width: 100%;
  border-collapse: collapse;
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  overflow: hidden;
}
thead th {
  background: #1a1a1a;
  color: #888;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 12px 10px;
  text-align: left;
  border-bottom: 1px solid #2a2a2a;
  white-space: nowrap;
}
tbody td {
  padding: 12px 10px;
  border-bottom: 1px solid #1e1e1e;
  font-size: 0.87rem;
  vertical-align: middle;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: #1a1a1a; }

.num { text-align: right; font-family: 'DM Mono', monospace; }
.num-pos { color: #1db954; }
.num-neg { color: #E50914; }

.rank {
  font-family: 'DM Mono', monospace;
  color: #666;
  font-size: 0.8rem;
  width: 40px;
}
.verdict-cell {
  font-family: 'DM Mono', monospace;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.v-pass { color: #1db954; }
.v-watch { color: #f5a623; }
.v-skip { color: #E50914; }

.address-cell { max-width: 250px; }
.address-cell .addr { color: #fff; font-size: 0.9rem; margin-bottom: 2px; }
.address-cell .addr a { color: #fff; text-decoration: none; }
.address-cell .addr a:hover { color: #E50914; text-decoration: underline; }
.address-cell .specs {
  color: #888;
  font-size: 0.75rem;
  font-family: 'DM Mono', monospace;
}

.dq-cell {
  font-size: 0.72rem;
  padding: 3px 8px;
  border-radius: 3px;
  font-weight: 600;
  letter-spacing: 0.05em;
  display: inline-block;
}
.dq-verified { background: rgba(29,185,84,0.12); color: #1db954; }
.dq-partial { background: rgba(245,166,35,0.12); color: #f5a623; }
.dq-ins-est { background: rgba(150,150,150,0.1); color: #999; }

.deepdive-cell {
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  color: #666;
  background: #1a1a1a;
  padding: 4px 8px;
  border-radius: 3px;
  user-select: all;
  cursor: text;
}

.footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #222;
  color: #666;
  font-size: 0.78rem;
}
.footer .assumptions {
  font-family: 'DM Mono', monospace;
  color: #777;
  margin-bottom: 10px;
}
.footer .disclaimer {
  font-style: italic;
  max-width: 900px;
  line-height: 1.5;
}
"""


def render(run: dict) -> str:
    """Produce the full HTML document from a ScreeningRun dict."""
    criteria = run["criteria"]
    results = run["results"]
    assumptions = run["assumptions_used"]

    areas_str = ", ".join(criteria["areas"])
    filter_summary = _format_filter_summary(criteria["filters"])

    # Summary bar pills
    pills = [
        f'<span class="pill pill-total">{run["candidates_scored"]} shown '
        f'(of {run["candidates_found"]} found)</span>',
        f'<span class="pill pill-pass">{run["pass_count"]} PASS</span>',
        f'<span class="pill pill-watch">{run["watch_count"]} WATCH</span>',
        f'<span class="pill pill-skip">{run["skip_count"]} SKIP</span>',
    ]
    summary_bar = '<div class="summary-bar">' + "".join(pills) + "</div>"

    # Data issues callout
    data_issues_html = ""
    if run.get("data_issues"):
        items = "".join("<li>" + escape(x) + "</li>" for x in run["data_issues"])
        data_issues_html = (
            '<div class="data-issues">'
            '<span class="label">Data quality notes</span>'
            f"<ul>{items}</ul>"
            "</div>"
        )

    # Table rows
    rows_html = "".join(_row(r, i + 1) for i, r in enumerate(results))

    # Empty state
    if not results:
        rows_html = (
            '<tr><td colspan="11" style="text-align:center;padding:40px;color:#666">'
            "No candidates matched the criteria."
            "</td></tr>"
        )

    # Footer assumptions line
    assumptions_line = (
        f"Quick screen uses: {assumptions['down_payment_pct'] * 100:.0f} percent down, "
        f"{assumptions['interest_rate'] * 100:.2f} percent rate, "
        f"{assumptions['loan_term_years']}-year loan, "
        f"{assumptions['opex_variable_pct'] * 100:.0f} percent variable OpEx allowance."
    )

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>Property Screening — {escape(areas_str)}</title>",
        '<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">',
        "<style>", _CSS, "</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        f"<h1>Property Screening — {escape(areas_str)}</h1>",
        f'<div class="sub">{escape(run["timestamp"][:10])} · '
        f'Run ID {escape(run["run_id"][:8])}</div>',
        f'<div class="criteria-line">{escape(filter_summary)}</div>',
        summary_bar,
        data_issues_html,
        "<table>",
        "<thead><tr>",
        "<th>#</th>",
        "<th>Verdict</th>",
        "<th>Address</th>",
        '<th class="num">Price</th>',
        '<th class="num">Sqft</th>',
        '<th class="num">$/Sqft</th>',
        '<th class="num">Est. Cash Flow</th>',
        '<th class="num">Cap Rate</th>',
        '<th class="num">1% Rule</th>',
        "<th>Data</th>",
        "<th>Deep-dive Command</th>",
        "</tr></thead>",
        f"<tbody>{rows_html}</tbody>",
        "</table>",
        '<div class="footer">',
        f'<div class="assumptions">{escape(assumptions_line)}</div>',
        '<div class="disclaimer">',
        "Quick-screen triage tool, not financial advice. Figures are "
        "estimates based on listing data, market averages, and simplified "
        "assumptions. Run /analyze-property on PASS rows for deeper "
        "verification before any investment decision.",
        "</div>",
        "</div>",
        "</div>",
        "</body>",
        "</html>",
    ]

    return "\n".join(html_parts)


def _row(r: dict, rank: int) -> str:
    c = r["candidate"]
    verdict = r["verdict"]
    v_class = {"PASS": "v-pass", "WATCH": "v-watch", "SKIP": "v-skip"}[verdict]
    v_emoji = {"PASS": "🟢", "WATCH": "🟡", "SKIP": "🔴"}[verdict]

    cf = r["cash_flow_monthly"]
    cf_class = "num-pos" if cf >= 0 else "num-neg"
    cf_str = f"${cf:,.0f}" if cf >= 0 else f"-${abs(cf):,.0f}"

    dq = c.get("data_quality", "partial")
    dq_label = {
        "verified": "Verified",
        "partial": "Partial",
        "insurance_estimated": "Ins. est.",
    }.get(dq, "Partial")
    dq_class = f"dq-{dq.replace('_', '-')}"

    url = c.get("listing_url") or "#"
    address_link = (
        f'<a href="{escape(url)}" target="_blank" rel="noopener">'
        f'{escape(c["address"])}</a>'
        if url != "#" else escape(c["address"])
    )

    deep_dive_cmd = f"/analyze-property {c.get('listing_url', c['address'])}"

    return (
        "<tr>"
        f'<td class="rank">#{rank}</td>'
        f'<td class="verdict-cell {v_class}">{v_emoji} {verdict}</td>'
        '<td class="address-cell">'
        f'<div class="addr">{address_link}</div>'
        f'<div class="specs">{c["beds"]}bd / {c["baths"]}ba · '
        f'built {c.get("year_built", "?")}</div>'
        "</td>"
        f'<td class="num">${c["price"]:,}</td>'
        f'<td class="num">{c["sqft"]:,}</td>'
        f'<td class="num">${r["price_per_sqft"]:.0f}</td>'
        f'<td class="num {cf_class}">{cf_str}</td>'
        f'<td class="num">{r["cap_rate"] * 100:.2f}%</td>'
        f'<td class="num">{r["one_percent_ratio"] * 100:.2f}%</td>'
        f'<td><span class="dq-cell {dq_class}">{dq_label}</span></td>'
        f'<td><span class="deepdive-cell">{escape(deep_dive_cmd)}</span></td>'
        "</tr>"
    )


def _format_filter_summary(filters: dict) -> str:
    """Compact one-line summary of applied filters."""
    parts = []
    if filters.get("price_min") or filters.get("price_max"):
        lo = f"${filters['price_min']:,}" if filters.get("price_min") else "any"
        hi = f"${filters['price_max']:,}" if filters.get("price_max") else "any"
        parts.append(f"price {lo}–{hi}")
    if filters.get("beds_min"):
        parts.append(f"beds ≥ {filters['beds_min']}")
    if filters.get("baths_min"):
        parts.append(f"baths ≥ {filters['baths_min']}")
    if filters.get("property_type"):
        parts.append(f"type: {filters['property_type']}")
    if filters.get("year_built_min"):
        parts.append(f"built ≥ {filters['year_built_min']}")
    if filters.get("max_dom"):
        parts.append(f"DOM ≤ {filters['max_dom']}")
    if filters.get("cash_flow_min"):
        parts.append(f"CF ≥ ${filters['cash_flow_min']}/mo")
    if filters.get("cap_rate_min"):
        parts.append(f"cap ≥ {filters['cap_rate_min']}%")
    return " · ".join(parts) if parts else "no filters"
