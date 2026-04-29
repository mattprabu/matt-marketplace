"""
render_pdf.py — PDF investment report via ReportLab.

Usage:
    from render_pdf import render_pdf
    render_pdf(metrics_result, "/mnt/user-data/outputs/report.pdf")

Print-friendly palette: white background, ink body, red accent on verdict
and warnings. Single page when possible.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)


# Palette — print friendly with brand accents
BRAND_RED = colors.HexColor("#E50914")
INK = colors.HexColor("#1a1a1a")
GRAY = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
BORDER = colors.HexColor("#e0e0e0")
GREEN = colors.HexColor("#0a8f3e")
AMBER = colors.HexColor("#d48b00")
MUTED_RED = colors.HexColor("#c0392b")


def render_pdf(m: dict, output_path: str) -> str:
    """Generate a PDF report. Returns the output path."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,
        title="Investment Analysis — " + m["property"]["address"],
        author="analyze-property skill",
    )

    styles = _build_styles()
    story = []

    p = m["property"]
    verdict = m["verdict"]

    # Header
    story.append(Paragraph(p["address"], styles["Address"]))
    story.append(Paragraph(f"${p['price']:,}", styles["Price"]))
    spec_line = f"{p['beds']} bed · {p['baths']} bath · {p['sqft']:,} sqft"
    if p.get("year_built"):
        spec_line += f" · Built {p['year_built']}"
    story.append(Paragraph(spec_line, styles["Spec"]))
    story.append(Spacer(1, 16))

    # Verdict banner
    story.append(_verdict_banner(m, verdict))
    story.append(Spacer(1, 16))

    # Metrics
    story.append(Paragraph("Key Metrics", styles["H2"]))
    story.append(_metrics_table(m))
    story.append(Spacer(1, 16))

    # Summary (pros/cons/watch)
    story.append(Paragraph("Summary", styles["H2"]))
    story.append(_pros_cons_table(m))
    story.append(Spacer(1, 16))

    # Breakdown
    story.append(Paragraph("Income and Expense Breakdown", styles["H2"]))
    story.append(_breakdown_table(m))
    story.append(Spacer(1, 16))

    # Risks
    if m.get("risk_factors"):
        story.append(Paragraph("Risk Factors", styles["H2"]))
        for r in m["risk_factors"]:
            story.append(Paragraph("! " + r, styles["Risk"]))
        story.append(Spacer(1, 12))

    # Comps
    if m["enrichment"].get("comps"):
        story.append(Paragraph("Recent Comparable Sales", styles["H2"]))
        story.append(_comps_table(m))
        story.append(Spacer(1, 16))

    # Assumptions
    story.append(Paragraph("Financial Assumptions", styles["H2"]))
    story.append(_assumptions_table(m))
    story.append(Spacer(1, 18))

    # Disclaimer
    story.append(Paragraph(_disclaimer(), styles["Disclaimer"]))

    doc.build(story)
    return output_path


def _build_styles():
    styles = getSampleStyleSheet()
    return {
        "Address": ParagraphStyle(
            "Address", parent=styles["Normal"], fontName="Helvetica",
            fontSize=11, textColor=GRAY, spaceAfter=4,
        ),
        "Price": ParagraphStyle(
            "Price", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=22, textColor=INK, spaceAfter=2,
        ),
        "Spec": ParagraphStyle(
            "Spec", parent=styles["Normal"], fontName="Courier",
            fontSize=9, textColor=GRAY, spaceAfter=0,
        ),
        "H2": ParagraphStyle(
            "H2", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=13, textColor=INK, spaceAfter=8, spaceBefore=4,
        ),
        "Body": ParagraphStyle(
            "Body", parent=styles["Normal"], fontName="Helvetica",
            fontSize=9.5, textColor=INK, leading=13,
        ),
        "Risk": ParagraphStyle(
            "Risk", parent=styles["Normal"], fontName="Helvetica",
            fontSize=9, textColor=MUTED_RED, leading=13, spaceAfter=4,
        ),
        "Disclaimer": ParagraphStyle(
            "Disclaimer", parent=styles["Normal"], fontName="Helvetica-Oblique",
            fontSize=8, textColor=GRAY, leading=11, alignment=1,
        ),
    }


def _verdict_banner(m: dict, verdict: str):
    color_map = {"GREEN": GREEN, "YELLOW": AMBER, "RED": MUTED_RED}
    label_map = {
        "GREEN": "Strong Candidate",
        "YELLOW": "Marginal",
        "RED": "Pass at This Price",
    }
    c = color_map[verdict]

    v_label_style = ParagraphStyle(
        "V1", fontName="Helvetica-Bold", fontSize=9, textColor=c
    )
    v_head_style = ParagraphStyle(
        "V2", fontName="Helvetica-Bold", fontSize=15, textColor=INK
    )
    v_reason_style = ParagraphStyle(
        "V3", fontName="Helvetica", fontSize=9, textColor=INK, leading=12
    )
    v_score_style = ParagraphStyle(
        "V4", fontName="Helvetica", fontSize=8, textColor=c
    )

    cell_content = [
        [Paragraph(f"<b>VERDICT: {verdict}</b>", v_label_style)],
        [Paragraph("<b>" + label_map[verdict] + "</b>", v_head_style)],
        [Paragraph(m["verdict_reason"], v_reason_style)],
        [Paragraph(
            f'Composite score: <font name="Courier">{m["composite_score_pct"]:.0f} percent</font>',
            v_score_style
        )],
    ]

    t = Table(cell_content, colWidths=[7.1 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, c),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
    ]))
    return t


def _metrics_table(m: dict) -> Table:
    score_color = {2: GREEN, 1: AMBER, 0: MUTED_RED}
    score_label = {2: "STRONG", 1: "OK", 0: "WEAK"}
    s = m["metric_scores"]

    def make_cell(label, value, sub, key):
        sc = s.get(key, 1)
        color = score_color[sc]
        label_style = ParagraphStyle("L", fontName="Helvetica-Bold", fontSize=7)
        val_style = ParagraphStyle("V", fontName="Courier-Bold", fontSize=14)
        sub_style = ParagraphStyle("S", fontName="Helvetica", fontSize=7.5)

        label_p = Paragraph(
            f'<font size="7" color="{GRAY.hexval()}">{label.upper()}</font>   '
            f'<font size="6.5" color="{color.hexval()}"><b>[{score_label[sc]}]</b></font>',
            label_style
        )
        val_p = Paragraph(
            f'<font name="Courier" size="14" color="{INK.hexval()}"><b>{value}</b></font>',
            val_style
        )
        sub_p = Paragraph(
            f'<font size="7.5" color="{GRAY.hexval()}">{sub}</font>',
            sub_style
        )
        return [label_p, val_p, sub_p]

    dscr_val = f"{m['dscr']:.2f}" if m.get("dscr") is not None else "n/a"
    cf = m["cash_flow_monthly"]
    cf_str = f"${cf:,.0f}" if cf >= 0 else f"-${abs(cf):,.0f}"

    cells = [
        make_cell("Monthly Cash Flow", cf_str, "after all expenses and debt", "cash_flow"),
        make_cell("Cap Rate", f"{m['cap_rate']*100:.2f}%",
                  f"NOI ${m['noi_annual']:,.0f}/yr", "cap_rate"),
        make_cell("Cash-on-Cash", f"{m['coc_return']*100:.2f}%",
                  f"on ${m['cash_to_close']:,.0f} down", "coc"),
        make_cell("DSCR", dscr_val, "debt coverage ratio", "dscr"),
        make_cell("1% Rule", f"{m['one_percent_ratio']*100:.2f}%",
                  "target: 1.00 percent or higher", "one_percent"),
        make_cell("OpEx Ratio", f"{m['fifty_percent_opex_ratio']*100:.1f}%",
                  "target: 50 percent or lower", "fifty_percent"),
        make_cell("5-Year IRR", f"{m['irr_5yr']*100:.1f}%",
                  "levered, with appreciation", "irr"),
        make_cell("Break-Even", f"{m['break_even_ratio']*100:.1f}%",
                  "percent of rent to cover costs", "fifty_percent"),
    ]

    # Build 2 rows of 4 boxes each
    box_rows = []
    current_row = []
    for c in cells:
        inner = Table([[c[0]], [c[1]], [c[2]]], colWidths=[1.65 * inch])
        inner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
            ("BOX", (0, 0), (-1, -1), 0.3, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (0, 0), 8),
            ("TOPPADDING", (0, 1), (-1, 1), 4),
            ("TOPPADDING", (0, 2), (-1, 2), 4),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ]))
        current_row.append(inner)
        if len(current_row) == 4:
            box_rows.append(current_row)
            current_row = []
    if current_row:
        while len(current_row) < 4:
            current_row.append("")
        box_rows.append(current_row)

    outer = Table(box_rows, colWidths=[1.78 * inch] * 4)
    outer.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return outer


def _pros_cons_table(m: dict) -> Table:
    pros = m.get("pros") or ["— no strong positives —"]
    cons = m.get("cons") or ["— no red flags —"]
    watch = m.get("watch_items") or ["— nothing to watch —"]

    def col(title, items, color):
        title_style = ParagraphStyle("CT", fontName="Helvetica-Bold", fontSize=9.5)
        item_style = ParagraphStyle(
            "CI", fontName="Helvetica", fontSize=8.5,
            leading=12, leftIndent=0, spaceAfter=3
        )
        paras = [
            Paragraph(
                f'<font size="9.5" color="{color.hexval()}"><b>{title}</b></font>',
                title_style
            )
        ]
        for x in items:
            paras.append(
                Paragraph(
                    f'<font color="{color.hexval()}">*</font> ' + x,
                    item_style
                )
            )
        return paras

    pros_col = col("PROS", pros, GREEN)
    cons_col = col("CONS", cons, MUTED_RED)
    watch_col = col("WATCH", watch, AMBER)

    max_len = max(len(pros_col), len(cons_col), len(watch_col))
    for c in (pros_col, cons_col, watch_col):
        while len(c) < max_len:
            c.append("")

    data = [list(row) for row in zip(pros_col, cons_col, watch_col)]
    t = Table(data, colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.3, BORDER),
        ("LINEAFTER", (0, 0), (0, -1), 0.3, BORDER),
        ("LINEAFTER", (1, 0), (1, -1), 0.3, BORDER),
    ]))
    return t


def _breakdown_table(m: dict) -> Table:
    a = m["assumptions"]
    rows = [
        ["Line Item", "Annual"],
        ["Gross rent", f"${m['gross_rent_annual']:,.0f}"],
        ["Property taxes", f"-${m['tax_annual']:,.0f}"],
        ["Insurance", f"-${m['insurance_annual']:,.0f}"],
        ["HOA", f"-${m['hoa_annual']:,.0f}"],
        [f"Vacancy ({a['vacancy_pct']*100:.0f}%)", f"-${m['vacancy_annual']:,.0f}"],
        [f"Management ({a['management_pct']*100:.0f}%)", f"-${m['management_annual']:,.0f}"],
        [f"Maintenance ({a['maintenance_pct']*100:.0f}%)", f"-${m['maintenance_annual']:,.0f}"],
        [f"CapEx ({a['capex_pct']*100:.0f}%)", f"-${m['capex_annual']:,.0f}"],
        ["Net Operating Income (NOI)", f"${m['noi_annual']:,.0f}"],
        ["Debt service (P and I)", f"-${m['debt_service_annual']:,.0f}"],
    ]

    cf = m["cash_flow_annual"]
    cf_str = f"${cf:,.0f}" if cf >= 0 else f"-${abs(cf):,.0f}"
    rows.append(["Annual cash flow", cf_str])

    t = Table(rows, colWidths=[4.5 * inch, 2.6 * inch])
    cf_color = GREEN if cf >= 0 else MUTED_RED
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
        ("FONT", (0, 1), (0, -1), "Helvetica", 9),
        ("FONT", (1, 1), (1, -1), "Courier", 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (1, 1), (1, 1), GREEN),
        ("TEXTCOLOR", (1, 2), (1, 8), MUTED_RED),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
        ("LINEABOVE", (0, 9), (-1, 9), 0.8, INK),
        ("FONT", (0, 9), (-1, 9), "Helvetica-Bold", 9.5),
        ("LINEABOVE", (0, 11), (-1, 11), 0.8, INK),
        ("FONT", (0, 11), (-1, 11), "Helvetica-Bold", 9.5),
        ("TEXTCOLOR", (1, 11), (1, 11), cf_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, 8),
         [colors.white, colors.HexColor("#fafafa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    return t


def _comps_table(m: dict) -> Table:
    comps = m["enrichment"]["comps"]
    rows = [["Address", "Sold Price", "Sqft", "$/Sqft", "Sold"]]
    for c in comps:
        rows.append([
            c["address"],
            f"${c['sold_price']:,}",
            f"{c['sqft']:,}",
            f"${c['price_per_sqft']:.0f}",
            c["sold_date"],
        ])

    t = Table(rows, colWidths=[2.6 * inch, 1.2 * inch, 0.8 * inch, 0.9 * inch, 1.0 * inch])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
        ("FONT", (0, 1), (0, -1), "Helvetica", 8.5),
        ("FONT", (1, 1), (-2, -1), "Courier", 8.5),
        ("FONT", (-1, 1), (-1, -1), "Helvetica", 8),
        ("TEXTCOLOR", (-1, 1), (-1, -1), GRAY),
        ("ALIGN", (1, 0), (-2, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#fafafa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    return t


def _assumptions_table(m: dict) -> Table:
    a = m["assumptions"]
    e = m["enrichment"]
    rows = [
        ["Assumption", "Value"],
        ["Down payment", f"{a['down_payment_pct']*100:.0f}%"],
        ["Interest rate", f"{a['interest_rate']*100:.2f}%"],
        ["Loan term", f"{a['loan_term_years']} years"],
        ["Vacancy / Mgmt / Maint / CapEx",
         f"{a['vacancy_pct']*100:.0f}% / {a['management_pct']*100:.0f}% / "
         f"{a['maintenance_pct']*100:.0f}% / {a['capex_pct']*100:.0f}%"],
        ["Rent source", e.get("rent_estimate", {}).get("source_used", "unknown")],
        ["Tax source", e.get("tax_annual", {}).get("source", "unknown")],
        ["Annual rent growth", f"{a['rent_growth_annual']*100:.1f}%"],
        ["Annual appreciation", f"{a['appreciation_annual']*100:.1f}%"],
    ]
    t = Table(rows, colWidths=[3.4 * inch, 3.7 * inch])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_GRAY),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#fafafa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    return t


def _disclaimer() -> str:
    return (
        "This analysis is a decision-support tool, not financial advice. "
        "Figures are projections based on listing data and market estimates. "
        "Verify all numbers with your own due diligence, a licensed real "
        "estate agent, and a tax or financial advisor before making any "
        "investment decision."
    )
