#!/usr/bin/env python3
"""
Hospitable API helper for Lorenzo.

Usage:
  python3 hospitable.py                        → today's check-ins/check-outs
  python3 hospitable.py 2026-02-19             → specific day
  python3 hospitable.py 2026-02-01 2026-03-31  → date range
  python3 hospitable.py --upcoming [N]         → next N days (default 7)
  python3 hospitable.py --occupancy [start end]→ occupancy stats (default YTD)
  python3 hospitable.py --conversations        → recent guest conversations
  python3 hospitable.py --token-check          → validate API token health
  python3 hospitable.py --reviews              → recent reviews (last page)
  python3 hospitable.py --reviews --pending   → reviews needing response
  python3 hospitable.py --reviews --low       → low-rated reviews (★1-3)
  python3 hospitable.py --reviews --stats     → detailed rating breakdown
  python3 hospitable.py --dashboard             → daily ops overview (all-in-one)
  python3 hospitable.py --calendar [YYYY-MM]   → visual calendar with pricing
  python3 hospitable.py --guest <name>         → search guest by name
  python3 hospitable.py --gaps [N]             → find unbooked nights (next N days)
  python3 hospitable.py --menu                 → interactive menu

  Add --property <name> to filter any command to one property.
  Property aliases: milano, bardo, drovetti, giacinto
"""

import sys
import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import date, timedelta
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

TOKEN_PATH = Path.home() / ".openclaw/workspace/hospitable_token.txt"

PROPERTIES = {
    "cd4bf5fb-16ef-49c8-b3db-93437e5f009f": "Milano",
    "912db8e2-ef92-44fa-b257-6f843c87e520": "Bardonecchia",
    "ec148f18-8c8a-456b-8bd9-b86e1c4086f9": "Drovetti (Turin)",
    "4cb5b686-ed1e-470c-90e8-e50500b0d77a": "Giacinto Collegno (Turin)",
}

PROPERTY_ALIASES = {
    "milano": "cd4bf5fb-16ef-49c8-b3db-93437e5f009f",
    "milan": "cd4bf5fb-16ef-49c8-b3db-93437e5f009f",
    "brianza": "cd4bf5fb-16ef-49c8-b3db-93437e5f009f",
    "bardonecchia": "912db8e2-ef92-44fa-b257-6f843c87e520",
    "bardo": "912db8e2-ef92-44fa-b257-6f843c87e520",
    "drovetti": "ec148f18-8c8a-456b-8bd9-b86e1c4086f9",
    "torino": "ec148f18-8c8a-456b-8bd9-b86e1c4086f9",
    "turin": "ec148f18-8c8a-456b-8bd9-b86e1c4086f9",
    "giacinto": "4cb5b686-ed1e-470c-90e8-e50500b0d77a",
    "collegno": "4cb5b686-ed1e-470c-90e8-e50500b0d77a",
}

BASE_URL = "https://public.api.hospitable.com/v2"

def _resolve_property(name: str) -> dict:
    """Resolve a property alias to {id: ..., name: ...}. Returns None if not found."""
    key = name.lower().strip()
    if key in PROPERTY_ALIASES:
        pid = PROPERTY_ALIASES[key]
        return {"id": pid, "name": PROPERTIES[pid]}
    # Try matching against property names
    for pid, pname in PROPERTIES.items():
        if key in pname.lower():
            return {"id": pid, "name": pname}
    return None

def _filter_properties(prop_filter: str = None) -> dict:
    """Return PROPERTIES dict filtered by alias. If None, return all."""
    if not prop_filter:
        return PROPERTIES
    resolved = _resolve_property(prop_filter)
    if resolved:
        return {resolved["id"]: resolved["name"]}
    print(f"  Unknown property: {prop_filter}")
    print(f"  Valid: {', '.join(sorted(PROPERTY_ALIASES.keys()))}")
    sys.exit(1)

# ── HTTP Helpers ──────────────────────────────────────────────────────────────

def _token() -> str:
    if not TOKEN_PATH.exists():
        print(f"  Error: token file not found at {TOKEN_PATH}")
        sys.exit(1)
    return TOKEN_PATH.read_text().strip()

def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _api_get(path: str, params: list = None, retries: int = 3) -> dict:
    url = f"{BASE_URL}/{path}"
    if params:
        url += f"?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=_headers())
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
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

def _api_post(path: str, body: dict, retries: int = 3) -> dict:
    url = f"{BASE_URL}/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(), method="POST")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
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

# ── Core ─────────────────────────────────────────────────────────────────────

def _fetch(prop_id: str, start: str, end: str, includes: list[str] = None) -> list[dict]:
    if includes is None:
        includes = ["guest"]
    params = [
        ("properties[]", prop_id),
        ("start_date", start),
        ("end_date", end),
    ]
    for inc in includes:
        params.append(("include[]", inc))
    data = _api_get("reservations", params)
    items = data.get("data", []) if isinstance(data, dict) else data
    for r in items:
        r["_property_id"] = prop_id
        r["_property_name"] = PROPERTIES[prop_id]
    return items

def _fetch_all_pages(prop_id: str, start: str, end: str, includes: list[str] = None) -> list[dict]:
    """Fetch all pages of reservations for a property."""
    if includes is None:
        includes = ["guest"]
    page = 1
    all_items = []
    while True:
        params = [
            ("properties[]", prop_id),
            ("start_date", start),
            ("end_date", end),
            ("page", str(page)),
        ]
        for inc in includes:
            params.append(("include[]", inc))
        data = _api_get("reservations", params)
        items = data.get("data", []) if isinstance(data, dict) else data
        for r in items:
            r["_property_id"] = prop_id
            r["_property_name"] = PROPERTIES[prop_id]
        all_items.extend(items)
        meta = data.get("meta", {})
        if page >= meta.get("last_page", 1):
            break
        page += 1
    return all_items

def get_reservations(start: str, end: str, includes: list[str] = None, props: dict = None) -> list[dict]:
    if props is None:
        props = PROPERTIES
    all_reservations = []
    for prop_id in props:
        all_reservations.extend(_fetch(prop_id, start, end, includes))
    return all_reservations

def get_all_reservations(start: str, end: str, includes: list[str] = None, props: dict = None) -> list[dict]:
    """Get all reservations across all properties, with pagination."""
    if props is None:
        props = PROPERTIES
    all_reservations = []
    for prop_id in props:
        all_reservations.extend(_fetch_all_pages(prop_id, start, end, includes))
    return all_reservations

def get_calendar(prop_id: str, start: str, end: str) -> list[dict]:
    """Fetch calendar data (availability + pricing) for a property."""
    try:
        data = _api_get(f"properties/{prop_id}/calendar", [
            ("start_date", start),
            ("end_date", end),
        ])
        return data.get("data", {}).get("days", []) if isinstance(data, dict) else []
    except Exception as e:
        print(f"  Error fetching calendar: {e}")
        return []

def get_guest_messages(reservation_id: str) -> list[dict]:
    """Fetch messages for a reservation."""
    try:
        data = _api_get(f"reservations/{reservation_id}/messages")
        return data.get("data", []) if isinstance(data, dict) else []
    except Exception as e:
        print(f"  Error fetching messages: {e}")
        return []

def send_guest_message(conversation_id: str, text: str) -> bool:
    """Send a message to a guest via conversation ID."""
    try:
        _api_post(f"conversations/{conversation_id}/messages", {"body": text})
        return True
    except Exception as e:
        print(f"  Error sending message: {e}")
        return False

def get_reviews(prop_filter: str = None, pages: int = 1) -> dict:
    """Fetch reviews for properties. pages=0 fetches all pages."""
    props = _filter_properties(prop_filter) if prop_filter else PROPERTIES
    results = {}
    for prop_id, name in props.items():
        try:
            all_items = []
            page = 1
            while True:
                data = _api_get(f"properties/{prop_id}/reviews", [("page", str(page))])
                items = data.get("data", []) if isinstance(data, dict) else []
                all_items.extend(items)
                meta = data.get("meta", {})
                if pages > 0 and page >= pages:
                    break
                if page >= meta.get("last_page", 1):
                    break
                page += 1
                time.sleep(0.2)
            results[name] = {"items": all_items, "total": meta.get("total", len(all_items))}
        except Exception:
            results[name] = {"items": [], "total": 0}
    return results

# ── Formatting helpers ────────────────────────────────────────────────────────

def _guest_name(r: dict) -> str:
    g = r.get("guest") or {}
    fn = g.get("first_name", "")
    ln = g.get("last_name", "")
    return f"{fn} {ln}".strip() or "Unknown guest"

def _date_part(dt_str: str) -> str:
    return dt_str[:10] if dt_str else ""

def _fmt(r: dict, kind: str) -> str:
    icon = "✈️  CHECK-IN " if kind == "in" else "🏠 CHECK-OUT"
    name = _guest_name(r)
    prop = r.get("_property_name", "?")
    nights = r.get("nights", "?")
    guests_count = (r.get("guests") or {}).get("total", "?")
    code = r.get("code", r.get("id", ""))
    platform = r.get("platform", "")
    plat_tag = f" [{platform}]" if platform and platform != "airbnb" else ""
    return (
        f"  {icon}  {name}  @{prop}\n"
        f"           {nights} night(s) · {guests_count} guest(s) · #{code}{plat_tag}"
    )

# ── Commands ──────────────────────────────────────────────────────────────────

def show_day(target_date: str):
    print(f"\n📅  Hospitable — {target_date}\n")
    reservations = get_reservations(target_date, target_date)
    check_ins = [r for r in reservations if _date_part(r.get("arrival_date", "")) == target_date]
    check_outs = [r for r in reservations if _date_part(r.get("departure_date", "")) == target_date]

    if check_ins:
        print(f"  ┌── CHECK-INS ({len(check_ins)}) " + "─" * 40)
        for r in check_ins:
            print(_fmt(r, "in"))
        print()
    else:
        print("  No check-ins.\n")

    if check_outs:
        print(f"  ┌── CHECK-OUTS ({len(check_outs)}) " + "─" * 39)
        for r in check_outs:
            print(_fmt(r, "out"))
        print()
    else:
        print("  No check-outs.\n")

def show_range(start: str, end: str):
    print(f"\n📅  Hospitable — {start} to {end}\n")
    reservations = get_reservations(start, end)
    if not reservations:
        print("  No reservations found.\n")
        return

    reservations.sort(key=lambda r: r.get("arrival_date", ""))
    by_prop: dict[str, list] = {}
    for r in reservations:
        prop = r.get("_property_name", "?")
        by_prop.setdefault(prop, []).append(r)

    for prop, items in by_prop.items():
        print(f"  🏡 {prop} ({len(items)} reservation(s))")
        print("  " + "─" * 55)
        for r in items:
            arrival = _date_part(r.get("arrival_date", ""))
            departure = _date_part(r.get("departure_date", ""))
            name = _guest_name(r)
            nights = r.get("nights", "?")
            guests_count = (r.get("guests") or {}).get("total", "?")
            code = r.get("code", "")
            platform = r.get("platform", "")
            print(f"  {arrival} → {departure}  {name}  ({nights}n · {guests_count}g · #{code} · {platform})")
        print()
    print(f"  Total: {len(reservations)} reservation(s)\n")

def show_reviews(mode: str = "recent", prop_filter: str = None):
    """Show reviews. mode: recent (default), pending (needs response), low (1-3 stars), stats."""
    pages = 1 if mode == "recent" else 0  # fetch all for filtering modes

    if mode == "stats":
        print("\n⭐  Review Statistics (fetching all reviews...)\n")
        pages = 0
    elif mode == "pending":
        print("\n⚠️  Reviews Needing Response\n")
    elif mode == "low":
        print("\n📉  Low-Rated Reviews (★1-3)\n")
    else:
        print("\n⭐  Recent Reviews\n")

    reviews = get_reviews(prop_filter=prop_filter, pages=pages)
    grand_total = 0
    grand_pending = 0

    for prop, data in reviews.items():
        items = data["items"]
        total = data["total"]
        grand_total += total

        if not items:
            print(f"  🏡 {prop} — no reviews\n")
            continue

        # Calculate stats from fetched items
        ratings = [r.get("public", {}).get("rating", 0) for r in items if r.get("public", {}).get("rating")]
        avg = sum(ratings) / len(ratings) if ratings else 0
        pending = [r for r in items if r.get("can_respond") and not r.get("responded_at")]
        low = [r for r in items if (r.get("public", {}).get("rating") or 5) <= 3]
        grand_pending += len(pending)

        # Filter based on mode
        if mode == "pending":
            display = pending
        elif mode == "low":
            display = low
        elif mode == "stats":
            display = []  # stats mode shows summary only
        else:
            display = items[:5]

        # Header
        pending_tag = f"  ⚠️ {len(pending)} need response" if pending else ""
        low_tag = f"  📉 {len(low)} low-rated" if low else ""
        print(f"  🏡 {prop} — {total} total · avg ★{avg:.1f}{pending_tag}{low_tag}")

        if mode == "stats" and items:
            # Detailed category breakdown
            cat_totals = {}
            cat_counts = {}
            for rv in items:
                for dr in (rv.get("private", {}) or {}).get("detailed_ratings", []):
                    cat = dr.get("type", "")
                    r = dr.get("rating", 0)
                    if r > 0 and cat:
                        cat_totals[cat] = cat_totals.get(cat, 0) + r
                        cat_counts[cat] = cat_counts.get(cat, 0) + 1
            if cat_totals:
                print(f"    Category breakdown (from {len(items)} reviews):")
                for cat in ["cleanliness", "communication", "checkin", "accuracy", "location", "value"]:
                    if cat in cat_totals:
                        cat_avg = cat_totals[cat] / cat_counts[cat]
                        bar = "★" * round(cat_avg) + "☆" * (5 - round(cat_avg))
                        print(f"      {cat:<15} {bar} {cat_avg:.1f}")

        if mode == "pending" and not pending:
            print(f"    ✅ All responded!\n")
            continue
        elif mode == "low" and not low:
            print(f"    ✅ No low ratings!\n")
            continue

        for rv in display:
            pub = rv.get("public", {})
            rating = pub.get("rating", "?")
            comment = (pub.get("review") or "—")[:200]
            date_str = rv.get("reviewed_at", "")[:10]
            responded = rv.get("responded_at")
            can_respond = rv.get("can_respond", False)

            stars = "★" * int(rating) + "☆" * (5 - int(rating)) if isinstance(rating, int) else f"★{rating}"
            tag = ""
            if can_respond and not responded:
                tag = " ⚠️ NEEDS RESPONSE"
            elif responded:
                tag = " ✅"

            print(f"    {stars} ({date_str}){tag}")
            if comment and comment != "—":
                print(f"      \"{comment}\"")

            # Show existing response if any
            response = pub.get("response")
            if response and mode == "pending":
                print(f"      → Response: \"{response[:100]}\"")
        print()

    # Summary
    if mode == "pending":
        print(f"  {'─' * 50}")
        print(f"  Total needing response: {grand_pending}")
    elif mode == "stats":
        print(f"  {'─' * 50}")
        print(f"  Total reviews across all properties: {grand_total}")
    print()

def show_upcoming(days: int = 7):
    """Show check-ins, check-outs, and currently staying guests for the next N days."""
    today = date.today()
    end = today + timedelta(days=days - 1)
    start_str = today.isoformat()
    end_str = end.isoformat()

    print(f"\n📅  Upcoming — next {days} day(s) ({start_str} to {end_str})\n")

    # Fetch reservations that overlap this window (use wider range to catch ongoing stays)
    wide_start = (today - timedelta(days=30)).isoformat()
    reservations = get_reservations(wide_start, end_str)

    if not reservations:
        print("  No reservations found.\n")
        return

    # Categorize
    currently_staying = []
    for day_offset in range(days):
        current_day = today + timedelta(days=day_offset)
        day_str = current_day.isoformat()
        check_ins = [r for r in reservations if _date_part(r.get("arrival_date", "")) == day_str]
        check_outs = [r for r in reservations if _date_part(r.get("departure_date", "")) == day_str]

        if check_ins or check_outs:
            day_label = "TODAY" if day_offset == 0 else current_day.strftime("%a %b %d")
            print(f"  ┌── {day_label} " + "─" * 45)
            for r in check_ins:
                print(f"    ✈️  IN   {_guest_name(r)}  @{r.get('_property_name', '?')}  ({r.get('nights', '?')}n)")
            for r in check_outs:
                print(f"    🏠 OUT  {_guest_name(r)}  @{r.get('_property_name', '?')}")
            # Flag same-day turnovers
            in_props = {r.get("_property_name") for r in check_ins}
            out_props = {r.get("_property_name") for r in check_outs}
            turnovers = in_props & out_props
            for t in turnovers:
                print(f"    ⚠️  TURNOVER at {t}")
            print()

    # Currently staying (arrived before today, departing after today)
    staying = [
        r for r in reservations
        if _date_part(r.get("arrival_date", "")) < start_str
        and _date_part(r.get("departure_date", "")) > start_str
    ]
    if staying:
        print(f"  ┌── CURRENTLY STAYING ({len(staying)}) " + "─" * 34)
        for r in staying:
            departure = _date_part(r.get("departure_date", ""))
            print(f"    🛏  {_guest_name(r)}  @{r.get('_property_name', '?')}  → leaves {departure}")
        print()

def show_occupancy(start: str = None, end: str = None):
    """Calculate occupancy % per property from reservation data."""
    today = date.today()
    if not start:
        start = f"{today.year}-01-01"
    if not end:
        end = today.isoformat()

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    total_days = (end_date - start_date).days + 1

    print(f"\n📊  Occupancy Report — {start} to {end} ({total_days} days)\n")

    reservations = get_all_reservations(start, end, includes=["guest", "financials"])

    by_prop: dict[str, list] = {}
    for r in reservations:
        status = (r.get("reservation_status") or {}).get("current", {}).get("category", "")
        if status != "accepted":
            continue
        prop = r.get("_property_name", "?")
        by_prop.setdefault(prop, []).append(r)

    grand_nights = 0
    grand_revenue = 0
    grand_bookings = 0

    for prop_name in sorted(PROPERTIES.values()):
        items = by_prop.get(prop_name, [])
        nights = sum(r.get("nights", 0) for r in items)
        bookings = len(items)
        revenue = 0
        for r in items:
            f = r.get("financials", {})
            if f:
                revenue += (f.get("guest", {}).get("total_price", {}).get("amount", 0))

        occupancy_pct = (nights / total_days * 100) if total_days > 0 else 0
        avg_nightly = (revenue / 100 / nights) if nights > 0 else 0

        print(f"  🏡 {prop_name}")
        print(f"     {bookings} booking(s) · {nights} night(s) · {occupancy_pct:.0f}% occupancy")
        print(f"     €{revenue/100:.2f} revenue · €{avg_nightly:.0f}/night avg")
        print()

        grand_nights += nights
        grand_revenue += revenue
        grand_bookings += bookings

    avg_occ = (grand_nights / (total_days * len(PROPERTIES)) * 100) if total_days > 0 else 0
    avg_rate = (grand_revenue / 100 / grand_nights) if grand_nights > 0 else 0
    print(f"  ── TOTAL ─────────────────────────────────────────")
    print(f"  {grand_bookings} booking(s) · {grand_nights} night(s) · {avg_occ:.0f}% avg occupancy")
    print(f"  €{grand_revenue/100:.2f} revenue · €{avg_rate:.0f}/night avg\n")

def show_conversations():
    """List recent guest conversations (reservations arriving/departing within ±7 days)."""
    today = date.today()
    start = (today - timedelta(days=7)).isoformat()
    end = (today + timedelta(days=7)).isoformat()

    print(f"\n💬  Recent Conversations — {start} to {end}\n")

    reservations = get_reservations(start, end)
    if not reservations:
        print("  No recent reservations.\n")
        return

    reservations.sort(key=lambda r: r.get("arrival_date", ""))
    for r in reservations:
        name = _guest_name(r)
        prop = r.get("_property_name", "?")
        arrival = _date_part(r.get("arrival_date", ""))
        departure = _date_part(r.get("departure_date", ""))
        res_id = r.get("id", "")
        code = r.get("code", "")
        conv_id = r.get("conversation_id", "")
        platform = r.get("platform", "")

        status_icon = "🟢" if arrival >= today.isoformat() else "🔵"
        print(f"  {status_icon} {name}  @{prop}")
        print(f"     {arrival} → {departure} · #{code} · {platform}")
        if conv_id:
            print(f"     Conversation: {conv_id}")
        print(f"     Reservation: {res_id}")
        print()

def show_calendar(month: str = None, prop_filter: str = None):
    """Visual calendar showing availability and pricing per property."""
    from calendar import monthrange, month_name
    today = date.today()

    if month:
        if len(month) == 7:  # YYYY-MM
            year, mon = int(month[:4]), int(month[5:7])
        elif len(month) == 4 and month.isdigit():  # Just month number
            year, mon = today.year, int(month)
        else:
            year, mon = today.year, today.month
    else:
        year, mon = today.year, today.month

    days_in_month = monthrange(year, mon)[1]
    start = f"{year}-{mon:02d}-01"
    end = f"{year}-{mon:02d}-{days_in_month:02d}"
    props = _filter_properties(prop_filter)

    print(f"\n📅  Calendar — {month_name[mon]} {year}\n")

    for prop_id, prop_name in props.items():
        days = get_calendar(prop_id, start, end)
        if not days:
            print(f"  🏡 {prop_name}: no calendar data\n")
            continue

        # Build day map
        day_map = {}
        for d in days:
            day_map[d["date"]] = d

        booked = 0
        available = 0
        revenue_potential = 0

        print(f"  🏡 {prop_name}")
        print(f"  {'Mo':>4} {'Tu':>4} {'Mi':>4} {'Do':>4} {'Fr':>4} {'Sa':>4} {'So':>4}")

        # Find what day of week the 1st falls on (0=Mon)
        first_dow = date(year, mon, 1).weekday()
        row = "  " + "    " * first_dow

        for day_num in range(1, days_in_month + 1):
            day_str = f"{year}-{mon:02d}-{day_num:02d}"
            info = day_map.get(day_str, {})
            status = info.get("status", {})
            available_flag = status.get("available", True)
            reason = status.get("reason", "")

            if reason == "RESERVED":
                marker = f" \033[91m{day_num:2d}\033[0m "  # red
                booked += 1
            elif not available_flag:
                marker = f" \033[90m{day_num:2d}\033[0m "  # gray (blocked)
            else:
                marker = f" \033[92m{day_num:2d}\033[0m "  # green
                available += 1
                price = info.get("price", {}).get("amount", 0)
                revenue_potential += price

            row += marker
            dow = date(year, mon, day_num).weekday()
            if dow == 6:  # Sunday
                print(row)
                row = "  "

        if row.strip():
            print(row)

        occ_pct = (booked / days_in_month * 100) if days_in_month > 0 else 0
        print(f"     {booked} booked · {available} available · {occ_pct:.0f}% occupancy")
        if revenue_potential > 0:
            print(f"     €{revenue_potential / 100:.0f} potential revenue from open nights")
        print()
        time.sleep(0.3)

    # Legend
    print(f"  Legend: \033[91m■\033[0m booked  \033[92m■\033[0m available  \033[90m■\033[0m blocked\n")


def show_guest(search_name: str, prop_filter: str = None):
    """Search for a guest by name across recent reservations."""
    today = date.today()
    # Search ±90 days
    start = (today - timedelta(days=90)).isoformat()
    end = (today + timedelta(days=90)).isoformat()
    props = _filter_properties(prop_filter)

    print(f"\n🔍  Searching for \"{search_name}\"...\n")

    reservations = get_all_reservations(start, end, includes=["guest", "financials"], props=props)
    search_lower = search_name.lower()

    matches = []
    for r in reservations:
        guest_nm = _guest_name(r).lower()
        if search_lower in guest_nm:
            matches.append(r)

    if not matches:
        print(f"  No guests matching \"{search_name}\" found in ±90 day window.\n")
        return

    matches.sort(key=lambda r: r.get("arrival_date", ""), reverse=True)
    print(f"  Found {len(matches)} reservation(s):\n")

    for r in matches:
        name = _guest_name(r)
        prop = r.get("_property_name", "?")
        arrival = _date_part(r.get("arrival_date", ""))
        departure = _date_part(r.get("departure_date", ""))
        nights = r.get("nights", "?")
        platform = r.get("platform", "")
        code = r.get("code", "")
        conv_id = r.get("conversation_id", "")
        res_id = r.get("id", "")

        guest = r.get("guest") or {}
        lang = guest.get("language", "?")
        location = guest.get("location", "")
        email = guest.get("email", "")
        phones = guest.get("phone_numbers", [])

        guests_info = r.get("guests") or {}
        total_guests = guests_info.get("total", "?")
        adults = guests_info.get("adult_count", 0)
        children = guests_info.get("child_count", 0)

        status = (r.get("reservation_status") or {}).get("current", {}).get("category", "?")
        financials = r.get("financials", {})
        total_price = financials.get("guest", {}).get("total_price", {}).get("formatted", "?") if financials else "?"

        # Status indicator
        today_str = today.isoformat()
        if status == "cancelled":
            icon = "❌"
        elif arrival > today_str:
            icon = "🟢"  # upcoming
        elif departure > today_str:
            icon = "🛏"  # currently staying
        else:
            icon = "🔵"  # past

        print(f"  {icon} {name}  @{prop}")
        print(f"     {arrival} → {departure} · {nights}n · {total_guests}g ({adults}a {children}c) · {platform}")
        print(f"     Status: {status} · Total: {total_price} · Lang: {lang}")
        if location:
            print(f"     From: {location}")
        if email:
            print(f"     Email: {email}")
        if phones:
            print(f"     Phone: {', '.join(phones)}")
        print(f"     Reservation: {res_id} · Code: #{code}")
        if conv_id:
            print(f"     Conversation: {conv_id}")
        print()


def show_gaps(days: int = 30, prop_filter: str = None):
    """Find unbooked nights across properties — revenue opportunities."""
    today = date.today()
    end = today + timedelta(days=days)
    start_str = today.isoformat()
    end_str = end.isoformat()
    props = _filter_properties(prop_filter)

    print(f"\n📊  Availability Gaps — next {days} day(s)\n")

    total_gap_nights = 0
    total_potential = 0

    for prop_id, prop_name in props.items():
        cal_days = get_calendar(prop_id, start_str, end_str)
        if not cal_days:
            continue

        # Find consecutive available stretches
        gaps = []
        current_gap = []
        for d in cal_days:
            if d.get("status", {}).get("available", False):
                current_gap.append(d)
            else:
                if current_gap:
                    gaps.append(current_gap)
                    current_gap = []
        if current_gap:
            gaps.append(current_gap)

        if not gaps:
            print(f"  🏡 {prop_name}: fully booked! 🎉\n")
            continue

        gap_nights = sum(len(g) for g in gaps)
        total_gap_nights += gap_nights
        prop_potential = sum(
            d.get("price", {}).get("amount", 0)
            for g in gaps for d in g
        )
        total_potential += prop_potential

        print(f"  🏡 {prop_name} — {gap_nights} open night(s)")

        for gap in gaps:
            gap_start = gap[0]["date"]
            gap_end = gap[-1]["date"]
            gap_len = len(gap)
            avg_price = sum(d.get("price", {}).get("amount", 0) for d in gap) // max(gap_len, 1)
            potential = sum(d.get("price", {}).get("amount", 0) for d in gap)

            if gap_len == 1:
                print(f"     {gap_start} (1 night) · €{avg_price / 100:.0f}/night")
            else:
                print(f"     {gap_start} → {gap_end} ({gap_len} nights) · €{avg_price / 100:.0f}/night avg · €{potential / 100:.0f} potential")
        print()
        time.sleep(0.3)

    if total_gap_nights > 0:
        print(f"  ── SUMMARY ───────────────────────────────────────")
        print(f"  {total_gap_nights} total open nights across {len(props)} property(ies)")
        print(f"  €{total_potential / 100:.0f} total potential revenue at current pricing\n")
    elif not prop_filter:
        print(f"  All properties fully booked for next {days} days! 🎉\n")


def show_dashboard():
    """Daily operations dashboard — everything a host needs in one view."""
    today = date.today()
    print(f"\n{'=' * 60}")
    print(f"  🏠 DAILY DASHBOARD — {today.strftime('%A %B %d, %Y')}")
    print(f"{'=' * 60}")

    # 1. Today's check-ins/outs
    today_str = today.isoformat()
    reservations = get_reservations(
        (today - timedelta(days=30)).isoformat(),
        (today + timedelta(days=3)).isoformat()
    )

    check_ins_today = [r for r in reservations if _date_part(r.get("arrival_date", "")) == today_str]
    check_outs_today = [r for r in reservations if _date_part(r.get("departure_date", "")) == today_str]

    print(f"\n  ┌── TODAY")
    if check_ins_today:
        for r in check_ins_today:
            guests = (r.get("guests") or {}).get("total", "?")
            print(f"  │  ✈️  IN   {_guest_name(r)}  @{r.get('_property_name', '?')}  ({r.get('nights', '?')}n · {guests}g)")
    if check_outs_today:
        for r in check_outs_today:
            print(f"  │  🏠 OUT  {_guest_name(r)}  @{r.get('_property_name', '?')}")
    if not check_ins_today and not check_outs_today:
        print(f"  │  No check-ins or check-outs today")

    # Flag turnovers
    in_props = {r.get("_property_name") for r in check_ins_today}
    out_props = {r.get("_property_name") for r in check_outs_today}
    for t in in_props & out_props:
        print(f"  │  ⚠️  TURNOVER at {t}")

    # 2. Tomorrow + day after
    for offset in range(1, 3):
        day = today + timedelta(days=offset)
        day_str = day.isoformat()
        day_ins = [r for r in reservations if _date_part(r.get("arrival_date", "")) == day_str]
        day_outs = [r for r in reservations if _date_part(r.get("departure_date", "")) == day_str]
        if day_ins or day_outs:
            label = "TOMORROW" if offset == 1 else day.strftime("%a %b %d")
            print(f"  ├── {label}")
            for r in day_ins:
                print(f"  │  ✈️  IN   {_guest_name(r)}  @{r.get('_property_name', '?')}")
            for r in day_outs:
                print(f"  │  🏠 OUT  {_guest_name(r)}  @{r.get('_property_name', '?')}")

    # 3. Currently staying
    staying = [
        r for r in reservations
        if _date_part(r.get("arrival_date", "")) < today_str
        and _date_part(r.get("departure_date", "")) > today_str
    ]
    if staying:
        print(f"  ├── CURRENTLY STAYING ({len(staying)})")
        for r in staying:
            dep = _date_part(r.get("departure_date", ""))
            days_left = (date.fromisoformat(dep) - today).days
            print(f"  │  🛏  {_guest_name(r)}  @{r.get('_property_name', '?')}  → {dep} ({days_left}d left)")

    # 4. Nuki lock status (if available)
    try:
        sys.path.insert(0, str(Path.home() / ".openclaw/workspace"))
        import nuki
        locks = nuki.get_smartlocks()
        if locks:
            print(f"  ├── LOCKS")
            for lk in locks:
                name = nuki.get_lock_name(lk)
                state = lk.get("state", {})
                lock_state = nuki.LOCK_STATES.get(state.get("state", 255), "unknown")
                icon = nuki.LOCK_ICONS.get(state.get("state", 255), "\U0001f510")
                battery = state.get("batteryCharge", "?")
                bat_warn = " \u26a0\ufe0f LOW" if state.get("batteryCritical") else ""
                print(f"  │  {icon} {name}: {lock_state} · {battery}%{bat_warn}")
    except Exception:
        pass

    # 5. Availability gaps (next 14 days)
    print(f"  └── GAPS (next 14 days)")
    gap_total = 0
    for prop_id, prop_name in PROPERTIES.items():
        cal_days = get_calendar(prop_id, today_str, (today + timedelta(days=14)).isoformat())
        avail = [d for d in cal_days if d.get("status", {}).get("available", False)]
        if avail:
            gap_total += len(avail)
            potential = sum(d.get("price", {}).get("amount", 0) for d in avail)
            print(f"     {prop_name}: {len(avail)} open night(s) · €{potential / 100:.0f} potential")
        else:
            print(f"     {prop_name}: fully booked 🎉")
        time.sleep(0.2)

    if gap_total == 0:
        print(f"     All properties fully booked! 🎉")

    print(f"\n{'=' * 60}\n")


def show_token_check():
    """Validate token with lightweight API call and check file age."""
    print("\n🔑  Token Health Check\n")

    # Check file exists and age
    if not TOKEN_PATH.exists():
        print("  ❌ Token file not found!")
        return

    stat = TOKEN_PATH.stat()
    age_days = (date.today() - date.fromtimestamp(stat.st_mtime)).days
    print(f"  Token file: {TOKEN_PATH}")
    print(f"  Last modified: {age_days} day(s) ago")

    if age_days > 330:
        print(f"  ⚠️  WARNING: Token is {age_days} days old — may expire soon (365-day limit)")
    elif age_days > 300:
        print(f"  ⚡ Token aging — {365 - age_days} days until potential expiry")
    else:
        print(f"  ✅ Token age OK — ~{365 - age_days} days remaining")

    # Validate with lightweight API call
    try:
        data = _api_get("properties")
        props = data.get("data", []) if isinstance(data, dict) else []
        print(f"  ✅ API connection OK — {len(props)} properties accessible")
    except Exception as e:
        print(f"  ❌ API connection FAILED: {e}")

def interactive_menu():
    while True:
        print("\n🏠 Hospitable Menu")
        print("  1. Today's check-ins/check-outs")
        print("  2. Specific date")
        print("  3. Date range")
        print("  4. Reviews")
        print("  5. Send guest message")
        print("  6. Upcoming (next 7 days)")
        print("  7. Occupancy report")
        print("  8. Recent conversations")
        print("  9. Token check")
        print("  0. Exit")
        choice = input("\n  Choice: ").strip()

        if choice == "1":
            show_day(date.today().isoformat())
        elif choice == "2":
            d = input("  Date (YYYY-MM-DD): ").strip()
            show_day(d)
        elif choice == "3":
            s = input("  Start (YYYY-MM-DD): ").strip()
            e = input("  End (YYYY-MM-DD): ").strip()
            show_range(s, e)
        elif choice == "4":
            show_reviews()
        elif choice == "5":
            cid = input("  Conversation ID: ").strip()
            msg = input("  Message: ").strip()
            ok = send_guest_message(cid, msg)
            print("  ✅ Sent!" if ok else "  ❌ Failed.")
        elif choice == "6":
            show_upcoming()
        elif choice == "7":
            show_occupancy()
        elif choice == "8":
            show_conversations()
        elif choice == "9":
            show_token_check()
        elif choice == "0":
            break

# ── Main ──────────────────────────────────────────────────────────────────────

def _parse_global_args(args: list) -> tuple:
    """Extract --property flag from args, return (remaining_args, prop_filter)."""
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


def main():
    raw_args = sys.argv[1:]
    args, prop_filter = _parse_global_args(raw_args)

    if not args:
        show_day(date.today().isoformat())
    elif args[0] == "--upcoming":
        try:
            days = int(args[1]) if len(args) > 1 else 7
        except ValueError:
            days = 7
        show_upcoming(days)
    elif args[0] == "--occupancy":
        start = args[1] if len(args) > 1 else None
        end = args[2] if len(args) > 2 else None
        show_occupancy(start, end)
    elif args[0] == "--conversations":
        show_conversations()
    elif args[0] == "--token-check":
        show_token_check()
    elif args[0] in ("--menu", "-m"):
        interactive_menu()
    elif args[0] in ("--reviews", "-r"):
        mode = "recent"
        if len(args) > 1 and args[1] in ("--pending", "--low", "--stats"):
            mode = args[1].lstrip("-")
        show_reviews(mode=mode, prop_filter=prop_filter)
    elif args[0] == "--dashboard":
        show_dashboard()
    elif args[0] == "--calendar":
        month = args[1] if len(args) > 1 else None
        show_calendar(month, prop_filter)
    elif args[0] == "--guest":
        if len(args) < 2:
            print("Usage: hospitable.py --guest <name>")
            sys.exit(1)
        show_guest(" ".join(args[1:]), prop_filter)
    elif args[0] == "--gaps":
        try:
            gap_days = int(args[1]) if len(args) > 1 else 30
        except ValueError:
            gap_days = 30
        show_gaps(gap_days, prop_filter)
    elif args[0] in ("--help", "-h"):
        print(__doc__)
    elif len(args) >= 2:
        show_range(args[0], args[1])
    else:
        show_day(args[0])

if __name__ == "__main__":
    main()
