"""
render_table_pdf.py — Landscape PDF table for screening results.

Usage:
    from render_table_pdf import render_pdf
    render_pdf(screening_run, "/mnt/user-data/outputs/screen.pdf")
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)


INK = colors.HexColor("#1a1a1a")
GRAY = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
BORDER = colors.HexColor("#e0e0e0")
GREEN = colors.HexColor("#0a8f3e")
AMBER = colors.HexColor("#d48b00")
MUTED_RED = colors.HexColor("#c0392b")


def render_pdf(run: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title="Property Screening",
        author="screen-properties skill",
    )

    styles = _build_styles()
    story = []

    criteria = run["criteria"]
    results = run["results"]
    areas_str = ", ".join(criteria["areas"]) if criteria["areas"] else "(no area)"

    # Header
    story.append(Paragraph(f"Property Screening — {areas_str}", styles["H1"]))
    story.append(Paragraph(
        f"{run['timestamp'][:10]}  ·  Run ID {run['run_id'][:8]}  ·  "
        f"{_format_filters(criteria['filters'])}",
        styles["Sub"]
    ))
    story.append(Spacer(1, 8))

    # Summary line
    summary = (
        f'<font color="{GRAY.hexval()}">Summary:</font> '
        f'<font color="{INK.hexval()}"><b>{run["candidates_scored"]} shown</b></font> '
        f'(of {run["candidates_found"]} found)  ·  '
        f'<font color="{GREEN.hexval()}"><b>{run["pass_count"]} PASS</b></font>  ·  '
        f'<font color="{AMBER.hexval()}"><b>{run["watch_count"]} WATCH</b></font>  ·  '
        f'<font color="{MUTED_RED.hexval()}"><b>{run["skip_count"]} SKIP</b></font>'
    )
    story.append(Paragraph(summary, styles["Summary"]))
    story.append(Spacer(1, 12))

    # Data issues
    if run.get("data_issues"):
        for issue in run["data_issues"]:
            story.append(Paragraph("! " + issue, styles["Issue"]))
        story.append(Spacer(1, 10))

    # Table
    if results:
        story.append(_build_table(results))
    else:
        story.append(Paragraph(
            "<i>No candidates matched the criteria.</i>",
            styles["Body"]
        ))

    story.append(Spacer(1, 14))

    # Footer
    a = run["assumptions_used"]
    assump = (
        f"Quick-screen assumptions: {a['down_payment_pct']*100:.0f}% down, "
        f"{a['interest_rate']*100:.2f}% rate, {a['loan_term_years']}-yr loan, "
        f"{a['opex_variable_pct']*100:.0f}% variable OpEx."
    )
    story.append(Paragraph(assump, styles["Foot"]))
    story.append(Paragraph(
        "Quick-screen triage tool, not financial advice. "
        "Run /analyze-property on PASS rows for deeper verification.",
        styles["Disclaimer"]
    ))

    doc.build(story)
    return output_path


def _build_styles():
    return {
        "H1": ParagraphStyle(
            "H1", fontName="Helvetica-Bold", fontSize=16,
            textColor=INK, spaceAfter=2,
        ),
        "Sub": ParagraphStyle(
            "Sub", fontName="Courier", fontSize=8,
            textColor=GRAY, spaceAfter=4,
        ),
        "Summary": ParagraphStyle(
            "Summary", fontName="Helvetica", fontSize=9,
            textColor=INK, spaceAfter=2,
        ),
        "Body": ParagraphStyle(
            "Body", fontName="Helvetica", fontSize=9,
            textColor=INK, leading=12,
        ),
        "Issue": ParagraphStyle(
            "Issue", fontName="Helvetica", fontSize=8.5,
            textColor=AMBER, leading=11, leftIndent=6, spaceAfter=2,
        ),
        "Foot": ParagraphStyle(
            "Foot", fontName="Courier", fontSize=7.5,
            textColor=GRAY, spaceAfter=4,
        ),
        "Disclaimer": ParagraphStyle(
            "Disclaimer", fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=GRAY, leading=10,
        ),
    }


def _build_table(results: list[dict]) -> Table:
    # Columns: #, Verdict, Address, Price, Sqft, $/Sqft, CF, Cap, 1%, Data
    header = ["#", "Verdict", "Address", "Price", "Sqft", "$/Sqft",
              "Cash Flow", "Cap Rate", "1% Rule", "Data"]
    rows = [header]

    verdict_style = {"PASS": GREEN, "WATCH": AMBER, "SKIP": MUTED_RED}

    addr_style = ParagraphStyle(
        "Addr", fontName="Helvetica", fontSize=8.5,
        textColor=INK, leading=11,
    )

    for i, r in enumerate(results, 1):
        c = r["candidate"]
        cf = r["cash_flow_monthly"]
        cf_str = f"${cf:,.0f}" if cf >= 0 else f"-${abs(cf):,.0f}"

        dq_label = {
            "verified": "Verified",
            "partial": "Partial",
            "insurance_estimated": "Ins.est.",
        }.get(c.get("data_quality", "partial"), "Partial")

        # Address with specs below
        addr_text = (
            f'<b>{c["address"]}</b><br/>'
            f'<font size="7" color="{GRAY.hexval()}">{c["beds"]}bd / '
            f'{c["baths"]}ba · built {c.get("year_built", "?")}</font>'
        )
        addr_para = Paragraph(addr_text, addr_style)

        rows.append([
            f"#{i}",
            r["verdict"],
            addr_para,
            f"${c['price']:,}",
            f"{c['sqft']:,}",
            f"${r['price_per_sqft']:.0f}",
            cf_str,
            f"{r['cap_rate']*100:.2f}%",
            f"{r['one_percent_ratio']*100:.2f}%",
            dq_label,
        ])

    # Column widths (landscape letter is 11" wide; margins 0.4*2 = 0.8; usable 10.2")
    col_widths = [
        0.35 * inch,  # rank
        0.65 * inch,  # verdict
        2.80 * inch,  # address
        0.85 * inch,  # price
        0.55 * inch,  # sqft
        0.65 * inch,  # $/sqft
        0.85 * inch,  # CF
        0.70 * inch,  # cap
        0.70 * inch,  # 1%
        0.70 * inch,  # data
    ]

    t = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
        ("ALIGN", (3, 0), (-1, 0), "RIGHT"),
        # Body
        ("FONT", (0, 1), (-1, -1), "Helvetica", 8.5),
        ("FONT", (3, 1), (-2, -1), "Courier", 8.5),
        ("ALIGN", (3, 1), (-2, -1), "RIGHT"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("VALIGN", (2, 1), (2, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#fafafa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.3, BORDER),
        ("LINEBELOW", (0, 1), (-1, -2), 0.2, BORDER),
    ]

    # Color-code verdict cells and cash flow column
    for row_idx, r in enumerate(results, 1):
        vcolor = verdict_style[r["verdict"]]
        style_cmds.append(("TEXTCOLOR", (1, row_idx), (1, row_idx), vcolor))
        style_cmds.append(("FONT", (1, row_idx), (1, row_idx),
                           "Helvetica-Bold", 8.5))

        cf = r["cash_flow_monthly"]
        cf_color = GREEN if cf >= 0 else MUTED_RED
        style_cmds.append(("TEXTCOLOR", (6, row_idx), (6, row_idx), cf_color))

    t.setStyle(TableStyle(style_cmds))
    return t


def _format_filters(filters: dict) -> str:
    parts = []
    if filters.get("price_min") or filters.get("price_max"):
        lo = f"${filters['price_min']:,}" if filters.get("price_min") else "any"
        hi = f"${filters['price_max']:,}" if filters.get("price_max") else "any"
        parts.append(f"price {lo}-{hi}")
    if filters.get("beds_min"):
        parts.append(f"beds >= {filters['beds_min']}")
    if filters.get("baths_min"):
        parts.append(f"baths >= {filters['baths_min']}")
    if filters.get("property_type"):
        parts.append(f"type: {filters['property_type']}")
    if filters.get("year_built_min"):
        parts.append(f"built >= {filters['year_built_min']}")
    if filters.get("max_dom"):
        parts.append(f"DOM <= {filters['max_dom']}")
    if filters.get("cash_flow_min"):
        parts.append(f"CF >= ${filters['cash_flow_min']}/mo")
    if filters.get("cap_rate_min"):
        parts.append(f"cap >= {filters['cap_rate_min']}%")
    return " · ".join(parts) if parts else "no filters"
