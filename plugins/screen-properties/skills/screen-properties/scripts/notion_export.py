"""
notion_export.py — Notion integration helpers for /screen-properties.

The skill uses two databases under the same parent page that
/analyze-property uses:
  - Screening Results: one row per candidate property per run
  - Screening History: one row per run with criteria and summary counts

This script builds the row properties and database schemas. Claude invokes
the actual Notion MCP tools using these structures.

Pattern:
    1. build_history_row(run, url)      — the run summary row
    2. build_result_row(screen_result, run_id, url)  — one per property
    3. screening_results_db_schema()    — for DB creation
    4. screening_history_db_schema()    — for DB creation
"""


# ------------------------------------------------------------------
# Row builders
# ------------------------------------------------------------------

def build_history_row(run: dict, results_page_url: str | None = None) -> dict:
    """Row properties for the Screening History database."""
    c = run["criteria"]
    f = c["filters"]
    areas = ", ".join(c["areas"]) if c["areas"] else "(none)"
    date_str = run["timestamp"][:10]

    price_range = "any"
    if f.get("price_min") or f.get("price_max"):
        lo = f"${f['price_min']:,}" if f.get("price_min") else "any"
        hi = f"${f['price_max']:,}" if f.get("price_max") else "any"
        price_range = f"{lo}-{hi}"

    other_parts = []
    if f.get("beds_min"):
        other_parts.append(f"beds>={f['beds_min']}")
    if f.get("baths_min"):
        other_parts.append(f"baths>={f['baths_min']}")
    if f.get("property_type"):
        other_parts.append(f"type={f['property_type']}")
    if f.get("year_built_min"):
        other_parts.append(f"built>={f['year_built_min']}")
    if f.get("max_dom"):
        other_parts.append(f"DOM<={f['max_dom']}")
    if f.get("cash_flow_min"):
        other_parts.append(f"CF>=${f['cash_flow_min']}")
    if f.get("cap_rate_min"):
        other_parts.append(f"cap>={f['cap_rate_min']}%")

    return {
        "Run": f"{areas} — {date_str}",
        "Areas": areas,
        "Price Range": price_range,
        "Other Filters": ", ".join(other_parts) if other_parts else "(none)",
        "Candidates Found": run["candidates_found"],
        "Pass Count": run["pass_count"],
        "Watch Count": run["watch_count"],
        "Skip Count": run["skip_count"],
        "Timestamp": run["timestamp"],
        "Run ID": run["run_id"],
    }


def build_result_row(
    result: dict,
    run_id: str,
    screen_date: str,
) -> dict:
    """Row properties for the Screening Results database."""
    c = result["candidate"]

    dq_map = {
        "verified": "Verified",
        "partial": "Partial",
        "insurance_estimated": "Insurance estimated",
    }
    dq_label = dq_map.get(c.get("data_quality", "partial"), "Partial")

    return {
        "Property": c["address"],
        "Verdict": result["verdict"].capitalize(),  # Pass / Watch / Skip
        "Price": c["price"],
        "Beds": c["beds"],
        "Sqft": c["sqft"],
        "Est Cash Flow": round(result["cash_flow_monthly"], 2),
        "Cap Rate": round(result["cap_rate"] * 100, 2),
        "1% Rule": round(result["one_percent_ratio"] * 100, 2),
        "Data Quality": dq_label,
        "Screen Date": screen_date[:10],
        "Listing URL": c.get("listing_url"),
        "Run ID": run_id,
    }


# ------------------------------------------------------------------
# Database schemas
# ------------------------------------------------------------------

def screening_results_db_schema() -> dict:
    """Schema for the Screening Results database."""
    return {
        "name": "Screening Results",
        "columns": [
            {"name": "Property", "type": "title"},
            {
                "name": "Verdict", "type": "select",
                "options": [
                    {"name": "Pass", "color": "green"},
                    {"name": "Watch", "color": "yellow"},
                    {"name": "Skip", "color": "red"},
                ],
            },
            {"name": "Price", "type": "number", "number_format": "dollar"},
            {"name": "Beds", "type": "number"},
            {"name": "Sqft", "type": "number"},
            {"name": "Est Cash Flow", "type": "number", "number_format": "dollar"},
            {"name": "Cap Rate", "type": "number", "number_format": "percent"},
            {"name": "1% Rule", "type": "number", "number_format": "percent"},
            {
                "name": "Data Quality", "type": "select",
                "options": [
                    {"name": "Verified", "color": "green"},
                    {"name": "Partial", "color": "yellow"},
                    {"name": "Insurance estimated", "color": "gray"},
                ],
            },
            {"name": "Screen Date", "type": "date"},
            {"name": "Listing URL", "type": "url"},
            {"name": "Run ID", "type": "rich_text"},
        ],
    }


def screening_history_db_schema() -> dict:
    """Schema for the Screening History database."""
    return {
        "name": "Screening History",
        "columns": [
            {"name": "Run", "type": "title"},
            {"name": "Areas", "type": "rich_text"},
            {"name": "Price Range", "type": "rich_text"},
            {"name": "Other Filters", "type": "rich_text"},
            {"name": "Candidates Found", "type": "number"},
            {"name": "Pass Count", "type": "number"},
            {"name": "Watch Count", "type": "number"},
            {"name": "Skip Count", "type": "number"},
            {"name": "Timestamp", "type": "date"},
            {"name": "Run ID", "type": "rich_text"},
        ],
    }
