#!/usr/bin/env python3
"""
Revenue report for Hospitable properties.

Usage:
  python3 revenue.py                       → year-to-date (current year)
  python3 revenue.py 2025                  → full year 2025
  python3 revenue.py 2026-01 2026-03       → month range (Jan–Mar 2026)
  python3 revenue.py 2026-02-01 2026-02-28 → exact date range
  python3 revenue.py --compare 2025 2026   → year-over-year comparison
  python3 revenue.py --monthly [year]      → month-by-month breakdown
  python3 revenue.py --best                → best performing months/properties

  Add --property <name> to filter to one property.
  Aliases: milano, bardo, drovetti, giacinto
"""
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from collections import defaultdict
from datetime import date
from pathlib import Path
from calendar import monthrange, month_abbr

# ── Config ───────────────────────────────────────────────────────────────────

TOKEN_PATH = Path.home() / ".openclaw/workspace/hospitable_token.txt"
BASE_URL = "https://public.api.hospitable.com/v2"

PROPERTIES = {
    "cd4bf5fb-16ef-49c8-b3db-93437e5f009f": "Milano",
    "912db8e2-ef92-44fa-b257-6f843c87e520": "Bardonecchia",
    "ec148f18-8c8a-456b-8bd9-b86e1c4086f9": "Drovetti",
    "4cb5b686-ed1e-470c-90e8-e50500b0d77a": "Giacinto Collegno",
}

PROPERTY_ALIASES = {
    "milano": "cd4bf5fb-16ef-49c8-b3db-93437e5f009f",
    "milan": "cd4bf5fb-16ef-49c8-b3db-93437e5f009f",
    "bardonecchia": "912db8e2-ef92-44fa-b257-6f843c87e520",
    "bardo": "912db8e2-ef92-44fa-b257-6f843c87e520",
    "drovetti": "ec148f18-8c8a-456b-8bd9-b86e1c4086f9",
    "torino": "ec148f18-8c8a-456b-8bd9-b86e1c4086f9",
    "turin": "ec148f18-8c8a-456b-8bd9-b86e1c4086f9",
    "giacinto": "4cb5b686-ed1e-470c-90e8-e50500b0d77a",
    "collegno": "4cb5b686-ed1e-470c-90e8-e50500b0d77a",
}

def _filter_properties(prop_filter: str = None) -> dict:
    if not prop_filter:
        return PROPERTIES
    key = prop_filter.lower().strip()
    if key in PROPERTY_ALIASES:
        pid = PROPERTY_ALIASES[key]
        return {pid: PROPERTIES[pid]}
    for pid, pname in PROPERTIES.items():
        if key in pname.lower():
            return {pid: pname}
    print(f"  Unknown property: {prop_filter}")
    sys.exit(1)

# ── HTTP ─────────────────────────────────────────────────────────────────────

def _token() -> str:
    if not TOKEN_PATH.exists():
        print(f"  Error: token file not found at {TOKEN_PATH}")
        sys.exit(1)
    return TOKEN_PATH.read_text().strip()

def _headers() -> dict:
    return {"Authorization": f"Bearer {_token()}", "Accept": "application/json"}

def api_get(path: str, params: dict = None, retries: int = 3) -> dict:
    url = f"{BASE_URL}/{path}"
    if params:
        url += f"?{urllib.parse.urlencode(params, doseq=True)}"
    req = urllib.request.Request(url, headers=_headers())
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                raise

# ── Date Parsing ─────────────────────────────────────────────────────────────

def parse_date_args(args: list[str]) -> tuple[str, str, str]:
    """Parse CLI args into (start_date, end_date, label).

    Supported formats:
      []                     → YTD (Jan 1 current year to today)
      [2025]                 → full year
      [2026-01, 2026-03]    → month range
      [2026-02-01, 2026-02-28] → exact range
    """
    today = date.today()

    if not args:
        start = f"{today.year}-01-01"
        end = today.isoformat()
        label = f"{today.year} YTD (to {end})"
        return start, end, label

    if len(args) == 1:
        arg = args[0]
        if len(arg) == 4 and arg.isdigit():
            year = int(arg)
            start = f"{year}-01-01"
            end = f"{year}-12-31"
            label = f"Full Year {year}"
            return start, end, label
        # Assume single date — treat as single month or exact date
        start = arg
        end = arg
        label = arg
        return start, end, label

    # Two args
    a, b = args[0], args[1]
    if len(a) == 7 and len(b) == 7:
        # Month range: 2026-01 2026-03
        start = f"{a}-01"
        year, month = int(b[:4]), int(b[5:7])
        last_day = monthrange(year, month)[1]
        end = f"{b}-{last_day:02d}"
        label = f"{a} to {b}"
        return start, end, label

    # Exact date range
    return a, b, f"{a} to {b}"

# ── Report Generation ────────────────────────────────────────────────────────

def generate_report(start: str, end: str, props: dict = None) -> dict[str, dict]:
    """Fetch all reservations and compute per-property stats."""
    if props is None:
        props = PROPERTIES
    revenue = defaultdict(lambda: {"nights": 0, "bookings": 0, "accommodation": 0, "total": 0})

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    total_days = (end_date - start_date).days + 1

    for pid, pname in props.items():
        page = 1
        while True:
            data = api_get("reservations", {
                "properties[]": pid,
                "start_date": start,
                "end_date": end,
                "include": "financials",
                "page": page,
            })
            for r in data["data"]:
                if r["reservation_status"]["current"]["category"] != "accepted":
                    continue
                f = r.get("financials", {})
                if f:
                    g = f.get("guest", {})
                    revenue[pname]["bookings"] += 1
                    revenue[pname]["nights"] += r.get("nights", 0)
                    revenue[pname]["accommodation"] += g.get("accommodation", {}).get("amount", 0)
                    revenue[pname]["total"] += g.get("total_price", {}).get("amount", 0)
            if page >= data["meta"]["last_page"]:
                break
            page += 1
            time.sleep(0.5)
        time.sleep(0.5)

    # Add occupancy stats
    for pname in revenue:
        r = revenue[pname]
        r["total_days"] = total_days
        r["occupancy_pct"] = (r["nights"] / total_days * 100) if total_days > 0 else 0
        r["avg_nightly"] = (r["total"] / 100 / r["nights"]) if r["nights"] > 0 else 0

    return dict(revenue)

def print_report(revenue: dict, label: str):
    """Print a formatted revenue + occupancy report."""
    print(f"\n{'=' * 55}")
    print(f"  📊 REVENUE REPORT — {label}")
    print(f"{'=' * 55}")

    total_all = 0
    total_nights = 0
    total_bookings = 0

    for prop in sorted(revenue.keys()):
        r = revenue[prop]
        tot = r["total"] / 100
        acc = r["accommodation"] / 100
        occ = r["occupancy_pct"]
        avg = r["avg_nightly"]
        print(f"\n  🏡 {prop}")
        print(f"     {r['bookings']} bookings · {r['nights']} nights · {occ:.0f}% occupancy")
        print(f"     €{acc:.2f} accommodation · €{tot:.2f} total · €{avg:.0f}/night")
        total_all += tot
        total_nights += r["nights"]
        total_bookings += r["bookings"]

    total_days = next(iter(revenue.values()), {}).get("total_days", 1)
    avg_occ = (total_nights / (total_days * len(PROPERTIES)) * 100) if total_days > 0 and PROPERTIES else 0
    avg_rate = (total_all / total_nights) if total_nights > 0 else 0

    print(f"\n{'─' * 55}")
    print(f"  TOTAL: €{total_all:.2f}")
    print(f"  {total_bookings} bookings · {total_nights} nights · {avg_occ:.0f}% avg occupancy · €{avg_rate:.0f}/night")
    print()

def print_comparison(rev1: dict, label1: str, rev2: dict, label2: str):
    """Print year-over-year comparison."""
    print(f"\n{'=' * 60}")
    print(f"  📊 COMPARISON — {label1} vs {label2}")
    print(f"{'=' * 60}")

    all_props = sorted(set(list(rev1.keys()) + list(rev2.keys())))
    empty = {"bookings": 0, "nights": 0, "total": 0, "occupancy_pct": 0, "avg_nightly": 0}

    total1 = 0
    total2 = 0

    for prop in all_props:
        r1 = rev1.get(prop, empty)
        r2 = rev2.get(prop, empty)
        t1 = r1["total"] / 100
        t2 = r2["total"] / 100
        delta = ((t2 - t1) / t1 * 100) if t1 > 0 else 0
        delta_sign = "+" if delta >= 0 else ""
        occ1 = r1["occupancy_pct"]
        occ2 = r2["occupancy_pct"]

        print(f"\n  🏡 {prop}")
        print(f"     {label1}: €{t1:.2f} · {r1['nights']}n · {occ1:.0f}%")
        print(f"     {label2}: €{t2:.2f} · {r2['nights']}n · {occ2:.0f}%")
        print(f"     Δ revenue: {delta_sign}{delta:.0f}%")

        total1 += t1
        total2 += t2

    overall_delta = ((total2 - total1) / total1 * 100) if total1 > 0 else 0
    sign = "+" if overall_delta >= 0 else ""
    print(f"\n{'─' * 60}")
    print(f"  {label1}: €{total1:.2f}")
    print(f"  {label2}: €{total2:.2f}")
    print(f"  Δ overall: {sign}{overall_delta:.0f}%")
    print()

def print_monthly(year: int = None, props: dict = None):
    """Month-by-month revenue breakdown."""
    if props is None:
        props = PROPERTIES
    today = date.today()
    if year is None:
        year = today.year

    last_month = 12 if year < today.year else today.month
    print(f"\n{'=' * 70}")
    print(f"  📊 MONTHLY BREAKDOWN — {year}")
    print(f"{'=' * 70}")

    # Header
    prop_names = sorted(props.values())
    header = f"  {'Month':<8}"
    for p in prop_names:
        short = p.split(" ")[0][:8]
        header += f" {short:>10}"
    header += f" {'TOTAL':>10}"
    print(header)
    print("  " + "─" * (len(header) - 2))

    yearly_totals = defaultdict(float)
    grand_total = 0

    for mon in range(1, last_month + 1):
        days_in = monthrange(year, mon)[1]
        s = f"{year}-{mon:02d}-01"
        if year == today.year and mon == today.month:
            e = today.isoformat()
        else:
            e = f"{year}-{mon:02d}-{days_in:02d}"

        rev = generate_report(s, e, props)
        row = f"  {month_abbr[mon]:<8}"
        month_total = 0
        for pname in prop_names:
            amt = rev.get(pname, {}).get("total", 0) / 100
            yearly_totals[pname] += amt
            month_total += amt
            row += f" €{amt:>8,.0f}"
        grand_total += month_total
        row += f" €{month_total:>8,.0f}"
        print(row)

    # Totals row
    print("  " + "─" * (len(header) - 2))
    total_row = f"  {'TOTAL':<8}"
    for pname in prop_names:
        total_row += f" €{yearly_totals[pname]:>8,.0f}"
    total_row += f" €{grand_total:>8,.0f}"
    print(total_row)

    # Best month
    if grand_total > 0:
        print(f"\n  Total {year}: €{grand_total:,.0f}")
    print()


def print_best(props: dict = None):
    """Show best performing months and properties from the current year."""
    if props is None:
        props = PROPERTIES
    today = date.today()
    year = today.year

    print(f"\n{'=' * 55}")
    print(f"  🏆 BEST PERFORMERS — {year} YTD")
    print(f"{'=' * 55}")

    monthly_data = {}
    for mon in range(1, today.month + 1):
        days_in = monthrange(year, mon)[1]
        s = f"{year}-{mon:02d}-01"
        e = today.isoformat() if mon == today.month else f"{year}-{mon:02d}-{days_in:02d}"
        rev = generate_report(s, e, props)
        monthly_data[mon] = rev

    # Best month overall
    month_totals = {}
    for mon, rev in monthly_data.items():
        month_totals[mon] = sum(r.get("total", 0) for r in rev.values()) / 100
    if month_totals:
        best_month = max(month_totals, key=month_totals.get)
        print(f"\n  📅 Best month: {month_abbr[best_month]} — €{month_totals[best_month]:,.0f}")

    # Best property
    prop_totals = defaultdict(float)
    prop_nights = defaultdict(int)
    for rev in monthly_data.values():
        for pname, data in rev.items():
            prop_totals[pname] += data.get("total", 0) / 100
            prop_nights[pname] += data.get("nights", 0)
    if prop_totals:
        best_prop = max(prop_totals, key=prop_totals.get)
        print(f"  🏡 Top earner: {best_prop} — €{prop_totals[best_prop]:,.0f}")

    # Best avg nightly rate
    prop_avg = {}
    for pname in prop_totals:
        if prop_nights[pname] > 0:
            prop_avg[pname] = prop_totals[pname] / prop_nights[pname]
    if prop_avg:
        best_rate = max(prop_avg, key=prop_avg.get)
        print(f"  💰 Best nightly rate: {best_rate} — €{prop_avg[best_rate]:,.0f}/night")

    # Property ranking
    print(f"\n  ── Property Ranking ──")
    for rank, (pname, total) in enumerate(sorted(prop_totals.items(), key=lambda x: -x[1]), 1):
        nights = prop_nights[pname]
        avg = total / nights if nights > 0 else 0
        print(f"  {rank}. {pname}: €{total:,.0f} ({nights}n · €{avg:.0f}/n)")
    print()


def _parse_global_args(args: list) -> tuple:
    """Extract --property flag from args."""
    prop_filter = None
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--property" and i + 1 < len(args):
            prop_filter = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    return remaining, prop_filter


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    raw_args = sys.argv[1:]
    args, prop_filter = _parse_global_args(raw_args)
    props = _filter_properties(prop_filter)

    if args and args[0] == "--compare":
        if len(args) < 3:
            print("Usage: python3 revenue.py --compare 2025 2026")
            sys.exit(1)
        y1, y2 = args[1], args[2]
        today = date.today()

        s1 = f"{y1}-01-01"
        e1 = f"{y1}-12-31" if int(y1) < today.year else today.isoformat()
        label1 = f"{y1}" if int(y1) < today.year else f"{y1} YTD"

        s2 = f"{y2}-01-01"
        e2 = f"{y2}-12-31" if int(y2) < today.year else today.isoformat()
        label2 = f"{y2}" if int(y2) < today.year else f"{y2} YTD"

        if int(y2) == today.year:
            e1 = f"{y1}-{today.strftime('%m-%d')}"
            label1 = f"{y1} (to {today.strftime('%m-%d')})"

        print(f"Fetching {label1}...")
        rev1 = generate_report(s1, e1, props)
        print(f"Fetching {label2}...")
        rev2 = generate_report(s2, e2, props)
        print_comparison(rev1, label1, rev2, label2)
        return

    if args and args[0] == "--monthly":
        try:
            year = int(args[1]) if len(args) > 1 else None
        except ValueError:
            year = None
        print_monthly(year, props)
        return

    if args and args[0] == "--best":
        print_best(props)
        return

    if args and args[0] in ("--help", "-h"):
        print(__doc__)
        return

    # Standard report
    start, end, label = parse_date_args(args)
    print(f"Fetching data for {label}...")
    revenue = generate_report(start, end, props)
    print_report(revenue, label)

if __name__ == "__main__":
    main()
