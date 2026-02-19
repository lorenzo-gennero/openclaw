#!/usr/bin/env python3
"""
M4 Mac Mini Price Tracker — Willhaben.at & Kleinanzeigen.de

Usage:
  python3 mac_mini_tracker.py            → check both sites, show new + cheapest
  python3 mac_mini_tracker.py --reset    → clear the seen-listings database
  python3 mac_mini_tracker.py --all      → show ALL current listings (not just new)
"""

import sys
import json
import re
import sqlite3
import time
import urllib.request
import urllib.error
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

# -- Config -------------------------------------------------------------------

DB_PATH = Path.home() / ".openclaw/workspace/mac_mini_tracker.db"

SEARCHES = {
    "willhaben": {
        "url": "https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?keyword=mac+mini+m4&sort=1",
        "country": "AT",
    },
    "kleinanzeigen": {
        "url": "https://www.kleinanzeigen.de/s-preis::/mac-mini-m4/k0",
        "country": "DE",
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
}

# -- Database -----------------------------------------------------------------

def _init_db():
    db = sqlite3.connect(str(DB_PATH))
    db.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            site TEXT,
            title TEXT,
            price_cents INTEGER,
            currency TEXT DEFAULT 'EUR',
            url TEXT,
            location TEXT,
            first_seen TEXT,
            last_seen TEXT
        )
    """)
    db.commit()
    return db


def _upsert(db, listing: dict):
    now = datetime.utcnow().isoformat()
    row = db.execute("SELECT id FROM listings WHERE id = ?", (listing["id"],)).fetchone()
    if row:
        db.execute(
            "UPDATE listings SET price_cents=?, last_seen=? WHERE id=?",
            (listing["price_cents"], now, listing["id"]),
        )
        return False  # not new
    else:
        db.execute(
            "INSERT INTO listings (id, site, title, price_cents, currency, url, location, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?)",
            (listing["id"], listing["site"], listing["title"], listing["price_cents"], listing.get("currency", "EUR"), listing["url"], listing.get("location", ""), now, now),
        )
        return True  # new listing


def _reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    print("Database reset.")

# -- HTTP ---------------------------------------------------------------------

def _fetch_html(url: str, retries: int = 3) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                print(f"  [ERROR] Failed to fetch {url}: {e}")
                return ""

# -- Willhaben Parser --------------------------------------------------------

class WillhabenParser(HTMLParser):
    """
    Willhaben renders search results as JSON-LD or inside structured divs.
    We look for the Next.js __NEXT_DATA__ script which contains all listings as JSON.
    Fallback: parse <a> tags with listing hrefs.
    """
    def __init__(self):
        super().__init__()
        self.listings = []
        self._in_script = False
        self._script_data = ""
        self._capture_next_data = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attrs_dict = dict(attrs)
            if attrs_dict.get("id") == "__NEXT_DATA__":
                self._in_script = True
                self._capture_next_data = True
                self._script_data = ""

    def handle_data(self, data):
        if self._in_script and self._capture_next_data:
            self._script_data += data

    def handle_endtag(self, tag):
        if tag == "script" and self._capture_next_data:
            self._in_script = False
            self._capture_next_data = False
            self._parse_next_data()

    def _parse_next_data(self):
        try:
            data = json.loads(self._script_data)
            self._extract_from_json(data)
        except (json.JSONDecodeError, KeyError):
            pass

    def _extract_from_json(self, obj):
        """Recursively search the JSON for ad/listing data."""
        if isinstance(obj, dict):
            # Willhaben typically has advertSummaryList or similar
            if "advertSummaryList" in obj:
                for ad in obj["advertSummaryList"].get("advertSummary", []):
                    self._parse_willhaben_ad(ad)
                return
            # Also check for searchResult or rows
            if "searchResult" in obj:
                self._extract_from_json(obj["searchResult"])
                return
            if "rows" in obj and isinstance(obj["rows"], list):
                for row in obj["rows"]:
                    self._extract_from_json(row)
                return
            for v in obj.values():
                self._extract_from_json(v)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_from_json(item)

    def _parse_willhaben_ad(self, ad: dict):
        try:
            ad_id = str(ad.get("id", ""))
            title = ad.get("description", ad.get("title", ""))
            # Attributes contain price, location etc
            attrs = {a["name"]: a["values"][0] for a in ad.get("attributes", {}).get("attribute", []) if a.get("values")}
            price_str = attrs.get("PRICE", attrs.get("PRICE/AMOUNT", "0"))
            price = _parse_price(price_str)
            location = attrs.get("LOCATION", attrs.get("ADDRESS", ""))
            url = f"https://www.willhaben.at/iad/object?adId={ad_id}"
            if ad_id and title:
                self.listings.append({
                    "id": f"wh_{ad_id}",
                    "site": "willhaben",
                    "title": title.strip(),
                    "price_cents": price,
                    "url": url,
                    "location": location,
                })
        except Exception:
            pass


def _scrape_willhaben(html: str) -> list[dict]:
    parser = WillhabenParser()
    parser.feed(html)
    if parser.listings:
        return parser.listings

    # Fallback: regex for JSON-LD or inline ad data
    # Try to find __NEXT_DATA__ via regex if parser missed it
    m = re.search(r'<script\s+id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            parser2 = WillhabenParser()
            parser2._extract_from_json(data)
            if parser2.listings:
                return parser2.listings
        except json.JSONDecodeError:
            pass

    # Last fallback: regex for listing links and prices
    listings = []
    pattern = re.compile(
        r'href="(/iad/kaufen-und-verkaufen/d/[^"]*-(\d+)/)"[^>]*>',
        re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        href, ad_id = match.group(1), match.group(2)
        # Try to grab surrounding text for title/price
        context = html[max(0, match.start() - 500):match.end() + 500]
        title = _extract_text_near(context, "title") or f"Willhaben listing #{ad_id}"
        price = _find_price_in_context(context)
        listings.append({
            "id": f"wh_{ad_id}",
            "site": "willhaben",
            "title": title,
            "price_cents": price,
            "url": f"https://www.willhaben.at{href}",
            "location": "Austria",
        })
    return listings

# -- Kleinanzeigen Parser ----------------------------------------------------

class KleinanzeigenParser(HTMLParser):
    """Parse Kleinanzeigen search results page."""
    def __init__(self):
        super().__init__()
        self.listings = []
        self._current = None
        self._in_title = False
        self._in_price = False
        self._in_location = False
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        # Each listing is an <article> or <li> with class containing "ad-listitem"
        if tag == "article" or (tag == "li" and "ad-listitem" in cls):
            data_id = attrs_dict.get("data-adid", attrs_dict.get("data-id", ""))
            if data_id:
                self._current = {
                    "id": f"ka_{data_id}",
                    "site": "kleinanzeigen",
                    "title": "",
                    "price_cents": 0,
                    "url": "",
                    "location": "",
                }

        if self._current:
            # Title link
            if tag == "a" and "ellipsis" in cls:
                href = attrs_dict.get("href", "")
                if href and "/s-anzeige/" in href:
                    if not href.startswith("http"):
                        href = f"https://www.kleinanzeigen.de{href}"
                    self._current["url"] = href
                self._in_title = True

            # Price
            if "aditem-main--middle--price" in cls or "price-label" in cls:
                self._in_price = True

            # Location
            if "aditem-main--top--left" in cls or "aditem-main--top--right" in cls:
                self._in_location = True

    def handle_data(self, data):
        if self._current:
            if self._in_title:
                self._current["title"] += data.strip()
            elif self._in_price:
                price = _parse_price(data)
                if price > 0:
                    self._current["price_cents"] = price
            elif self._in_location:
                loc = data.strip()
                if loc and len(loc) > 2:
                    self._current["location"] = loc

    def handle_endtag(self, tag):
        if tag in ("a",):
            self._in_title = False
        if tag in ("p", "span", "div"):
            self._in_price = False
            self._in_location = False
        if tag in ("article", "li") and self._current:
            if self._current.get("title"):
                self.listings.append(self._current)
            self._current = None


def _scrape_kleinanzeigen(html: str) -> list[dict]:
    parser = KleinanzeigenParser()
    parser.feed(html)
    if parser.listings:
        return parser.listings

    # Fallback: regex approach
    listings = []
    pattern = re.compile(
        r'data-adid="(\d+)".*?href="(/s-anzeige/[^"]*)".*?>(.*?)</a>',
        re.DOTALL,
    )
    for match in pattern.finditer(html):
        ad_id, href, title_html = match.group(1), match.group(2), match.group(3)
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        context = html[match.start():min(len(html), match.end() + 800)]
        price = _find_price_in_context(context)
        listings.append({
            "id": f"ka_{ad_id}",
            "site": "kleinanzeigen",
            "title": title or f"Kleinanzeigen listing #{ad_id}",
            "price_cents": price,
            "url": f"https://www.kleinanzeigen.de{href}",
            "location": "Germany",
        })
    return listings

# -- Listing Filter -----------------------------------------------------------

# Accessory / irrelevant keywords (lowercase) — if title contains any, skip it
EXCLUDE_KEYWORDS = [
    "dock", "docking", "hub", "adapter", "kabel", "cable",
    "mikrofon", "microphone", "gehäuse", "case", "tasche", "bag",
    "halterung", "mount", "ladegerät", "charger", "ständer", "stand",
    "netzteil", "power adapter", "ssd gehäuse", "ssd-gehäuse",
    "wacom", "monitor", "gaming pc",
    "suche", "ankauf",
]

# Non-Mac-Mini products that show up in search results
EXCLUDE_PRODUCTS = [
    "macbook", "mac book", "mac pro", "mac studio", "imac",
]

# Listings where the primary product is NOT a Mac Mini (trade offers, etc.)
EXCLUDE_PRIMARY = [
    "asus nuc", "intel nuc", "gegen mac",
]


def _is_actual_mac_mini(listing: dict) -> bool:
    """Return True only if the listing is an actual Mac Mini for sale."""
    title = listing["title"].lower()

    # Must contain "mac mini" or "macmini" somewhere
    if "mac mini" not in title and "macmini" not in title:
        return False

    # Exclude accessories and irrelevant items
    for kw in EXCLUDE_KEYWORDS:
        if kw in title:
            return False

    # Exclude other Apple products that mention mac mini in passing
    for prod in EXCLUDE_PRODUCTS:
        if prod in title:
            return False

    # Exclude trade offers where Mac Mini isn't the product being sold
    for pat in EXCLUDE_PRIMARY:
        if pat in title:
            return False

    return True

# -- Helpers ------------------------------------------------------------------

def _parse_price(text: str) -> int:
    """Extract price in cents from text like '449,00', '€ 499', '1.149 EUR'."""
    text = text.replace("\xa0", " ").replace("VB", "").replace("VHB", "").strip()
    # Match numbers with optional comma/dot decimals
    m = re.search(r"(\d[\d.,]*\d|\d+)", text)
    if not m:
        return 0
    num_str = m.group(1)
    # European format: 1.234,56 → has both dot and comma, dot is thousands
    if "," in num_str and "." in num_str:
        num_str = num_str.replace(".", "").replace(",", ".")
    elif "," in num_str:
        # 449,00 or 1234,56 — comma is decimal separator
        num_str = num_str.replace(",", ".")
    elif "." in num_str:
        # Could be 1.149 (German thousands) or 449.00 (decimal)
        # If there's exactly one dot and 3 digits after it, treat as thousands separator
        parts = num_str.split(".")
        if len(parts) == 2 and len(parts[1]) == 3:
            num_str = num_str.replace(".", "")  # 1.149 → 1149
        # Otherwise keep as decimal (e.g. 449.00)
    try:
        return int(float(num_str) * 100)
    except ValueError:
        return 0


def _extract_text_near(html_chunk: str, attr: str) -> str:
    """Try to extract text from title attrs or tag content."""
    m = re.search(rf'{attr}="([^"]*)"', html_chunk, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""


def _find_price_in_context(html_chunk: str) -> int:
    """Find a price-like number in HTML context."""
    # Look for euro prices
    for pattern in [
        r"(\d[\d.,]*)\s*(?:€|EUR|euro)",
        r"(?:€|EUR)\s*(\d[\d.,]*)",
        r'price[^>]*>[\s€]*(\d[\d.,]*)',
    ]:
        m = re.search(pattern, html_chunk, re.IGNORECASE)
        if m:
            return _parse_price(m.group(1))
    return 0


def _fmt_price(cents: int) -> str:
    if cents <= 0:
        return "price N/A"
    return f"{cents / 100:,.2f}"

# -- Main Logic ---------------------------------------------------------------

def run(show_all: bool = False):
    db = _init_db()
    all_listings = []
    new_listings = []

    for site_name, cfg in SEARCHES.items():
        print(f"\nFetching {site_name} ({cfg['country']})...")
        html = _fetch_html(cfg["url"])
        if not html:
            print(f"  Could not fetch {site_name}.")
            continue

        if site_name == "willhaben":
            listings = _scrape_willhaben(html)
        elif site_name == "kleinanzeigen":
            listings = _scrape_kleinanzeigen(html)
        else:
            listings = []

        filtered = [l for l in listings if _is_actual_mac_mini(l)]
        print(f"  Found {len(listings)} listing(s), {len(filtered)} actual Mac Mini(s).")
        for lst in filtered:
            is_new = _upsert(db, lst)
            all_listings.append(lst)
            if is_new:
                new_listings.append(lst)

    db.commit()

    # Sort by price (0 = unknown, push to end)
    def sort_key(x):
        p = x["price_cents"]
        return (0, p) if p > 0 else (1, 0)

    all_listings.sort(key=sort_key)
    new_listings.sort(key=sort_key)

    # Output
    print(f"\n{'=' * 60}")
    print(f"  M4 Mac Mini Tracker — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 60}")

    if new_listings:
        print(f"\n  NEW LISTINGS ({len(new_listings)}):")
        print(f"  {'-' * 50}")
        for i, lst in enumerate(new_listings, 1):
            _print_listing(i, lst)
    else:
        print("\n  No new listings since last check.")

    if show_all and all_listings:
        print(f"\n  ALL CURRENT LISTINGS ({len(all_listings)}):")
        print(f"  {'-' * 50}")
        for i, lst in enumerate(all_listings, 1):
            _print_listing(i, lst)

    # Cheapest across both sites
    priced = [l for l in all_listings if l["price_cents"] > 0]
    if priced:
        cheapest = min(priced, key=lambda x: x["price_cents"])
        print(f"\n  CHEAPEST: {cheapest['title'][:60]}")
        print(f"           {_fmt_price(cheapest['price_cents'])} | {cheapest['site']} ({cheapest.get('location', '')})")
        print(f"           {cheapest['url']}")

    # Summary stats from DB
    total = db.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    print(f"\n  Total tracked listings: {total}")
    print()

    db.close()


def _print_listing(idx: int, lst: dict):
    site_tag = "WH" if lst["site"] == "willhaben" else "KA"
    price = _fmt_price(lst["price_cents"])
    title = lst["title"][:55]
    loc = lst.get("location", "")[:25]
    print(f"  {idx:>2}. [{site_tag}] {price:>10} | {title}")
    if loc:
        print(f"      {loc}")
    print(f"      {lst['url']}")

# -- Entry Point --------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if "--reset" in args:
        _reset_db()
        return
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    show_all = "--all" in args
    run(show_all=show_all)


if __name__ == "__main__":
    main()
