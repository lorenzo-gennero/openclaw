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
  python3 hospitable.py --reviews              → property reviews
  python3 hospitable.py --menu                 → interactive menu
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

BASE_URL = "https://public.api.hospitable.com/v2"

# ── HTTP Helpers ──────────────────────────────────────────────────────────────

def _token() -> str:
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

def get_reservations(start: str, end: str, includes: list[str] = None) -> list[dict]:
    all_reservations = []
    for prop_id in PROPERTIES:
        all_reservations.extend(_fetch(prop_id, start, end, includes))
    return all_reservations

def get_all_reservations(start: str, end: str, includes: list[str] = None) -> list[dict]:
    """Get all reservations across all properties, with pagination."""
    all_reservations = []
    for prop_id in PROPERTIES:
        all_reservations.extend(_fetch_all_pages(prop_id, start, end, includes))
    return all_reservations

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

def get_reviews() -> dict:
    """Fetch reviews for all properties."""
    results = {}
    for prop_id, name in PROPERTIES.items():
        try:
            data = _api_get(f"properties/{prop_id}/reviews")
            items = data.get("data", []) if isinstance(data, dict) else []
            results[name] = items
        except Exception:
            results[name] = []
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

def show_reviews():
    print("\n⭐  Property Reviews\n")
    reviews = get_reviews()
    for prop, items in reviews.items():
        avg = sum(r.get("public", {}).get("rating", 0) for r in items) / len(items) if items else 0
        print(f"  🏡 {prop} — {len(items)} review(s)  avg ★{avg:.1f}")
        for rv in items[:5]:
            pub = rv.get("public", {})
            rating = pub.get("rating", "?")
            comment = (pub.get("review") or "")[:120]
            date_str = rv.get("reviewed_at", "")[:10]
            can_respond = rv.get("can_respond", False)
            respond_tag = " [⚠️ needs response]" if can_respond and not rv.get("responded_at") else ""
            print(f"    ★{rating} ({date_str}){respond_tag}: {comment}")
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

def main():
    args = sys.argv[1:]
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
        show_reviews()
    elif args[0] in ("--help", "-h"):
        print(__doc__)
    elif len(args) >= 2:
        show_range(args[0], args[1])
    else:
        show_day(args[0])

if __name__ == "__main__":
    main()
