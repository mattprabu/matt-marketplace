"""
compare.py — Side-by-side comparison of multiple MetricsResult dicts.

Usage:
    from compare import build_comparison, render_comparison_html
    comparison = build_comparison([result1, result2, result3])
    html = render_comparison_html(comparison)
"""

from html import escape


# Plain CSS string so CSS braces don't collide with Python f-strings
_COMP_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'DM Sans', -apple-system, sans-serif;
  background: #0a0a0a; color: #e8e8e8; line-height: 1.6;
  padding: 40px 20px;
}
.container { max-width: 1200px; margin: 0 auto; }
h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
.subtitle { color: #888; margin-bottom: 30px; }

.rec-block {
  background: #141414;
  border: 1px solid #222;
  border-left: 4px solid;
  border-radius: 8px;
  padding: 24px 28px;
  margin-bottom: 30px;
}
.rec-label {
  font-size: 0.75rem; letter-spacing: 0.15em;
  color: #888; font-weight: 700;
}
.rec-addr {
  font-size: 1.4rem; color: #fff; font-weight: 700;
  margin: 6px 0;
}
.rec-reason { color: #bbb; font-size: 0.95rem; }

table {
  width: 100%;
  border-collapse: collapse;
  background: #141414;
  border: 1px solid #222;
  border-radius: 8px;
  overflow: hidden;
}
th, td {
  padding: 14px 18px;
  text-align: center;
  border-bottom: 1px solid #222;
}
th.prop-header {
  background: #1a1a1a;
  font-family: 'DM Sans';
  font-size: 0.9rem;
  padding: 16px 18px;
  position: relative;
  min-width: 180px;
}
.prop-addr { color: #fff; font-weight: 500; font-size: 0.9rem; line-height: 1.3; }
.prop-sub { color: #888; font-size: 0.75rem; font-family: 'DM Mono'; margin-top: 4px; }
.rec-badge {
  display: inline-block;
  background: rgba(29,185,84,0.15); color: #1db954;
  font-size: 0.65rem; padding: 3px 8px;
  border-radius: 3px; margin-bottom: 6px;
  letter-spacing: 0.1em; font-weight: 700;
}
td.metric-label {
  text-align: left;
  color: #888;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}
td {
  font-family: 'DM Mono', monospace;
  font-size: 0.95rem;
  color: #e8e8e8;
}
tr.key-metric td { font-size: 1.05rem; color: #fff; }
td.winner {
  background: rgba(29,185,84,0.12);
  color: #1db954;
  font-weight: 500;
  position: relative;
}
td.winner:before {
  content: "*";
  position: absolute;
  left: 10px;
  color: #1db954;
  font-size: 1rem;
  font-weight: 700;
}
tr.verdict-row td { font-size: 1rem; padding: 18px; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #1a1a1a; }
tr:hover td.winner { background: rgba(29,185,84,0.18); }

.footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #222;
  color: #666;
  font-size: 0.8rem;
  text-align: center;
}
"""


def build_comparison(results: list[dict]) -> dict:
    """Compute the comparison structure from 2 or more MetricsResult dicts."""
    if len(results) < 2:
        raise ValueError("Need at least 2 properties to compare")

    properties = [r["property"] for r in results]
    rows = _build_metric_rows(results)
    winners = _identify_winners(results)
    recommendation = _recommend(results)

    return {
        "property_count": len(results),
        "properties": properties,
        "rows": rows,
        "winners": winners,
        "recommendation": recommendation,
        "results": results,
    }


def _build_metric_rows(results: list[dict]) -> list[dict]:
    def fmt_money(v, show_sign=False):
        if v < 0:
            return f"-${abs(v):,.0f}"
        sign = "+" if show_sign and v > 0 else ""
        return f"{sign}${v:,.0f}"

    def fmt_pct(v):
        return f"{v * 100:.2f}%"

    rows = [
        {
            "label": "Price",
            "values": [fmt_money(r["property"]["price"]) for r in results],
            "lower_better": True,
            "raw": [r["property"]["price"] for r in results],
        },
        {
            "label": "Monthly Cash Flow",
            "values": [fmt_money(r["cash_flow_monthly"], show_sign=True) for r in results],
            "higher_better": True,
            "raw": [r["cash_flow_monthly"] for r in results],
            "key": True,
        },
        {
            "label": "Cap Rate",
            "values": [fmt_pct(r["cap_rate"]) for r in results],
            "higher_better": True,
            "raw": [r["cap_rate"] for r in results],
            "key": True,
        },
        {
            "label": "Cash-on-Cash",
            "values": [fmt_pct(r["coc_return"]) for r in results],
            "higher_better": True,
            "raw": [r["coc_return"] for r in results],
            "key": True,
        },
        {
            "label": "DSCR",
            "values": [f"{r['dscr']:.2f}" if r.get("dscr") is not None else "n/a"
                       for r in results],
            "higher_better": True,
            "raw": [r.get("dscr") or 999 for r in results],
            "key": True,
        },
        {
            "label": "1% Rule",
            "values": [fmt_pct(r["one_percent_ratio"]) for r in results],
            "higher_better": True,
            "raw": [r["one_percent_ratio"] for r in results],
        },
        {
            "label": "5-Year IRR",
            "values": [fmt_pct(r["irr_5yr"]) for r in results],
            "higher_better": True,
            "raw": [r["irr_5yr"] for r in results],
            "key": True,
        },
        {
            "label": "Cash to Close",
            "values": [fmt_money(r["cash_to_close"]) for r in results],
            "lower_better": True,
            "raw": [r["cash_to_close"] for r in results],
        },
        {
            "label": "Composite Score",
            "values": [f"{r['composite_score_pct']:.0f}%" for r in results],
            "higher_better": True,
            "raw": [r["composite_score_pct"] for r in results],
            "key": True,
        },
        {
            "label": "Verdict",
            "values": [
                {"GREEN": "🟢 GREEN", "YELLOW": "🟡 YELLOW", "RED": "🔴 RED"}[r["verdict"]]
                for r in results
            ],
            "raw": [r["verdict"] for r in results],
            "verdict_row": True,
        },
    ]

    # Mark winner index for each row
    for row in rows:
        if row.get("verdict_row"):
            order = {"GREEN": 2, "YELLOW": 1, "RED": 0}
            max_rank = max(order[v] for v in row["raw"])
            row["winner_indices"] = [
                i for i, v in enumerate(row["raw"]) if order[v] == max_rank
            ]
        elif "raw" in row:
            if row.get("higher_better"):
                best = max(row["raw"])
            else:
                best = min(row["raw"])
            row["winner_indices"] = [
                i for i, v in enumerate(row["raw"]) if v == best
            ]

    return rows


def _identify_winners(results: list[dict]) -> dict:
    def best(results, key, higher_is_better=True):
        vals = [(i, r[key]) for i, r in enumerate(results)
                if r.get(key) is not None]
        if not vals:
            return None
        if higher_is_better:
            idx, _ = max(vals, key=lambda x: x[1])
        else:
            idx, _ = min(vals, key=lambda x: x[1])
        return idx

    return {
        "best_cash_flow": best(results, "cash_flow_monthly"),
        "best_cap_rate": best(results, "cap_rate"),
        "best_coc": best(results, "coc_return"),
        "best_dscr": best(results, "dscr"),
        "best_irr": best(results, "irr_5yr"),
        "best_composite": best(results, "composite_score_pct"),
        "lowest_cash_needed": best(results, "cash_to_close", higher_is_better=False),
    }


def _recommend(results: list[dict]) -> dict:
    verdicts = [r["verdict"] for r in results]
    greens = [i for i, v in enumerate(verdicts) if v == "GREEN"]
    yellows = [i for i, v in enumerate(verdicts) if v == "YELLOW"]

    if greens:
        best_i = max(greens, key=lambda i: results[i]["composite_score_pct"])
        return {
            "recommended_index": best_i,
            "address": results[best_i]["property"]["address"],
            "confidence": "high",
            "reason": (
                f"Strongest GREEN verdict with composite "
                f"{results[best_i]['composite_score_pct']:.0f} percent"
            ),
        }
    if yellows:
        best_i = max(yellows, key=lambda i: (
            results[i]["cash_flow_monthly"],
            results[i].get("dscr") or 0,
        ))
        cf = results[best_i]["cash_flow_monthly"]
        return {
            "recommended_index": best_i,
            "address": results[best_i]["property"]["address"],
            "confidence": "medium",
            "reason": (
                f"Best of the marginal options — but consider negotiating price "
                f"down or looking at more properties. Cash flow ${cf:,.0f}/mo."
            ),
        }
    return {
        "recommended_index": None,
        "address": None,
        "confidence": "none",
        "reason": (
            "None of these meet investment criteria at asking price. "
            "Keep looking or negotiate significantly below list on the "
            "strongest-composite property."
        ),
    }


# ------------------------------------------------------------------
# HTML rendering for comparison report
# ------------------------------------------------------------------

def render_comparison_html(comp: dict) -> str:
    """Produce a dark-themed comparison report HTML."""
    n = comp["property_count"]
    rec = comp["recommendation"]

    # Header row with property addresses
    header_cells = []
    for i, p in enumerate(comp["properties"]):
        badge = ""
        if rec.get("recommended_index") == i:
            badge = '<div class="rec-badge">RECOMMENDED</div>'
        header_cells.append(
            '<th class="prop-header">'
            + badge
            + f'<div class="prop-addr">{escape(p["address"])}</div>'
            + f'<div class="prop-sub">${p["price"]:,} · '
            + f'{p["beds"]}/{p["baths"]} · {p["sqft"]:,} sqft</div>'
            + "</th>"
        )
    prop_headers = "".join(header_cells)

    # Metric rows
    metric_rows = []
    for row in comp["rows"]:
        winners = set(row.get("winner_indices", []))
        cells = []
        for i, val in enumerate(row["values"]):
            is_winner = i in winners and len(winners) < n
            cls = "winner" if is_winner else ""
            cells.append(f'<td class="{cls}">{escape(val)}</td>')

        row_cls_parts = []
        if row.get("key"):
            row_cls_parts.append("key-metric")
        if row.get("verdict_row"):
            row_cls_parts.append("verdict-row")
        row_cls = " ".join(row_cls_parts)

        metric_rows.append(
            f'<tr class="{row_cls}">'
            f'<td class="metric-label">{escape(row["label"])}</td>'
            + "".join(cells) +
            "</tr>"
        )

    # Recommendation block
    rec_color = {"high": "#1db954", "medium": "#f5a623", "none": "#E50914"}[
        rec.get("confidence", "none")
    ]
    rec_addr = escape(rec.get("address") or "None of these properties")
    rec_reason = escape(rec.get("reason", ""))
    rec_block = (
        f'<div class="rec-block" style="border-left-color:{rec_color}">'
        '<div class="rec-label">RECOMMENDATION</div>'
        f'<div class="rec-addr">{rec_addr}</div>'
        f'<div class="rec-reason">{rec_reason}</div>'
        "</div>"
    )

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>Property Comparison — {n} properties</title>",
        '<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">',
        "<style>",
        _COMP_CSS,
        "</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        "<h1>Side-by-Side Comparison</h1>",
        f'<div class="subtitle">Comparing {n} properties · '
        "* marks the winner for each metric</div>",
        rec_block,
        "<table>",
        "<thead><tr>",
        '<th class="metric-label" style="text-align:left">Metric</th>',
        prop_headers,
        "</tr></thead>",
        "<tbody>",
        "".join(metric_rows),
        "</tbody></table>",
        '<div class="footer">',
        "Decision-support analysis, not financial advice. "
        "Verify all numbers before making any investment decision.",
        "</div>",
        "</div>",
        "</body>",
        "</html>",
    ]

    return "\n".join(html_parts)
