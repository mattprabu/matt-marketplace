"""
render_table_md.py — GitHub-flavored markdown table for screening results.

Usage:
    from render_table_md import render
    md = render(screening_run)
"""


def render(run: dict) -> str:
    """Produce a markdown document from a ScreeningRun dict."""
    criteria = run["criteria"]
    results = run["results"]
    a = run["assumptions_used"]

    areas_str = ", ".join(criteria["areas"]) if criteria["areas"] else "(no area)"
    filter_summary = _format_filter_summary(criteria["filters"])

    lines = []
    lines.append(f"# Property Screening — {areas_str}")
    lines.append("")
    lines.append(
        f"**Date:** {run['timestamp'][:10]}  ·  "
        f"**Run ID:** `{run['run_id'][:8]}`  ·  "
        f"**Criteria:** {filter_summary}"
    )
    lines.append("")
    lines.append(
        f"**Summary:** {run['candidates_scored']} shown (of "
        f"{run['candidates_found']} found)  ·  "
        f"🟢 {run['pass_count']} PASS  ·  "
        f"🟡 {run['watch_count']} WATCH  ·  "
        f"🔴 {run['skip_count']} SKIP"
    )
    lines.append("")

    if run.get("data_issues"):
        lines.append("## Data quality notes")
        lines.append("")
        for issue in run["data_issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    if not results:
        lines.append("_No candidates matched the criteria._")
        return "\n".join(lines)

    lines.append("## Results")
    lines.append("")
    lines.append(
        "| # | Verdict | Address | Price | Sqft | $/Sqft | "
        "Est. Cash Flow | Cap Rate | 1% Rule | Data |"
    )
    lines.append(
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|"
    )

    for i, r in enumerate(results, 1):
        c = r["candidate"]
        verdict_emoji = {"PASS": "🟢", "WATCH": "🟡", "SKIP": "🔴"}[r["verdict"]]
        verdict = f"{verdict_emoji} {r['verdict']}"

        cf = r["cash_flow_monthly"]
        cf_str = f"${cf:,.0f}" if cf >= 0 else f"-${abs(cf):,.0f}"

        addr = c["address"]
        if c.get("listing_url"):
            addr = f"[{addr}]({c['listing_url']})"

        dq_map = {
            "verified": "Verified",
            "partial": "Partial",
            "insurance_estimated": "Ins. est.",
        }
        dq = dq_map.get(c.get("data_quality", "partial"), "Partial")

        lines.append(
            f"| {i} | {verdict} | {addr} | ${c['price']:,} | "
            f"{c['sqft']:,} | ${r['price_per_sqft']:.0f} | "
            f"{cf_str} | {r['cap_rate'] * 100:.2f}% | "
            f"{r['one_percent_ratio'] * 100:.2f}% | {dq} |"
        )

    lines.append("")
    lines.append("## Deep-dive commands")
    lines.append("")
    lines.append("Copy any of these to run a full analysis on that property:")
    lines.append("")
    for i, r in enumerate(results, 1):
        c = r["candidate"]
        target = c.get("listing_url") or c["address"]
        lines.append(f"- `#{i}` — `/analyze-property {target}`")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        f"**Assumptions used:** {a['down_payment_pct'] * 100:.0f}% down, "
        f"{a['interest_rate'] * 100:.2f}% rate, {a['loan_term_years']}-yr loan, "
        f"{a['opex_variable_pct'] * 100:.0f}% variable OpEx."
    )
    lines.append("")
    lines.append(
        "_Quick-screen triage tool, not financial advice. "
        "Run /analyze-property on PASS rows for deeper verification._"
    )

    return "\n".join(lines)


def _format_filter_summary(filters: dict) -> str:
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
