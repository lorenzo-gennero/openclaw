#!/usr/bin/env python3
"""
Nuki Smart Lock helper for Lorenzo.

Usage:
  python3 nuki.py                                          → lock status + battery
  python3 nuki.py --status                                 → lock status + battery
  python3 nuki.py --unlock [name]                          → unlock a lock
  python3 nuki.py --lock [name]                            → lock a lock
  python3 nuki.py --logs [N]                               → activity log (default 20)
  python3 nuki.py --codes                                  → list keypad codes
  python3 nuki.py --create-code <name> <code> <from> <until> → create guest code
  python3 nuki.py --delete-code <auth_id>                  → delete a code
  python3 nuki.py --cleanup                                → remove expired codes
  python3 nuki.py --guest-codes                            → cross-ref with Hospitable
  python3 nuki.py --token-check                            → token health
"""

import sys
import json
import random
import subprocess
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, date, timezone
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

TOKEN_PATH = Path.home() / ".openclaw/workspace/nuki_token.txt"
BASE_URL = "https://api.nuki.io"

# Smartlock ID → friendly name
LOCKS = {
    "694097108": "Milano (Viale Brianza)",
}

# ── HTTP Helpers ─────────────────────────────────────────────────────────────

def _token() -> str:
    return TOKEN_PATH.read_text().strip()

def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _api_get(path: str, params: dict = None, retries: int = 3) -> any:
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

def _api_post(path: str, body: dict = None, retries: int = 3) -> any:
    url = f"{BASE_URL}/{path}"
    data = json.dumps(body).encode() if body else b""
    req = urllib.request.Request(url, data=data, headers=_headers(), method="POST")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw.strip() else {}
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

def _api_put(path: str, body: dict, retries: int = 3) -> any:
    url = f"{BASE_URL}/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(), method="PUT")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw.strip() else {}
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

def _api_delete(path: str, retries: int = 3) -> bool:
    url = f"{BASE_URL}/{path}"
    req = urllib.request.Request(url, headers=_headers(), method="DELETE")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status in (200, 204)
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

def get_smartlocks() -> list[dict]:
    """Fetch all smart locks."""
    return _api_get("smartlock")

def get_smartlock(lock_id: str) -> dict:
    """Fetch single smart lock details."""
    return _api_get(f"smartlock/{lock_id}")

def get_lock_name(lock: dict) -> str:
    """Get friendly name for a lock, falling back to API name."""
    lock_id = str(lock.get("smartlockId", lock.get("id", "")))
    return LOCKS.get(lock_id, lock.get("name", f"Lock {lock_id}"))

def find_lock_id(name: str = None) -> str:
    """Find lock ID by name. If name is None and only one lock, return that."""
    locks = get_smartlocks()
    if not locks:
        print("  No smart locks found.")
        sys.exit(1)
    if name is None:
        if len(locks) == 1:
            return str(locks[0]["smartlockId"])
        print("  Multiple locks found. Specify a name:")
        for lk in locks:
            print(f"    - {get_lock_name(lk)} (ID: {lk['smartlockId']})")
        sys.exit(1)
    name_lower = name.lower()
    for lk in locks:
        friendly = get_lock_name(lk).lower()
        if name_lower in friendly or friendly in name_lower:
            return str(lk["smartlockId"])
    print(f"  Lock not found: {name}")
    print("  Available locks:")
    for lk in locks:
        print(f"    - {get_lock_name(lk)}")
    sys.exit(1)

def get_auth_list(lock_id: str) -> list[dict]:
    """Fetch keypad authorizations for a lock."""
    return _api_get(f"smartlock/{lock_id}/auth")

def get_logs(lock_id: str, limit: int = 20) -> list[dict]:
    """Fetch activity log entries."""
    return _api_get(f"smartlock/{lock_id}/log", {"limit": limit})

# ── Code Generation ──────────────────────────────────────────────────────────

def generate_code() -> str:
    """Generate a valid 6-digit keypad code (digits 1-9, not starting with '12')."""
    while True:
        code = "".join(str(random.randint(1, 9)) for _ in range(6))
        if not code.startswith("12"):
            return code

def validate_code(code: str) -> bool:
    """Validate a keypad code: 6 digits, 1-9 only, no '12' prefix."""
    if len(code) != 6:
        return False
    if not all(c in "123456789" for c in code):
        return False
    if code.startswith("12"):
        return False
    return True

# ── Formatting ───────────────────────────────────────────────────────────────

LOCK_STATES = {
    0: "uncalibrated",
    1: "locked",
    2: "unlocking",
    3: "unlocked",
    4: "locking",
    5: "unlatched",
    6: "unlocked (lock'n'go)",
    7: "unlatching",
    253: "boot run",
    254: "motor blocked",
    255: "undefined",
}

LOCK_ICONS = {
    1: "\U0001f512",  # locked
    3: "\U0001f513",  # unlocked
    5: "\U0001f513",  # unlatched
    6: "\U0001f513",  # unlocked (lock'n'go)
}

ACTION_NAMES = {
    1: "unlock",
    2: "lock",
    3: "unlatch",
    4: "lock'n'go",
    5: "lock'n'go with unlatch",
    224: "door opened",
    225: "door closed",
    226: "door sensor jammed",
    240: "firmware update",
    243: "auto lock",
    252: "auto unlock",
}

SOURCE_NAMES = {
    0: "Keypad",
    1: "Manual",
    2: "App (via Bluetooth)",
    3: "Auto",
    4: "Web API",
    5: "Auto",
    6: "Homekit",
    255: "Keypad (code)",
}

def _fmt_datetime(dt_str: str) -> str:
    """Format ISO datetime to readable format."""
    if not dt_str:
        return "—"
    try:
        # Handle various formats
        dt_str = dt_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt_str[:16] if len(dt_str) >= 16 else dt_str

def _mask_code(code: str) -> str:
    """Mask a keypad code: show first and last digit."""
    if not code or len(code) < 3:
        return code or "—"
    return code[0] + "*" * (len(code) - 2) + code[-1]

# ── Commands ─────────────────────────────────────────────────────────────────

def show_status():
    """Show all locks with state, battery, last activity."""
    print("\n\U0001f510  Nuki Smart Locks\n")
    locks = get_smartlocks()
    if not locks:
        print("  No smart locks found.\n")
        return
    for lk in locks:
        lock_id = str(lk["smartlockId"])
        name = get_lock_name(lk)
        state = lk.get("state", {})
        lock_state_num = state.get("state", 255)
        lock_state = LOCK_STATES.get(lock_state_num, "unknown")
        icon = LOCK_ICONS.get(lock_state_num, "\U0001f510")
        battery = state.get("batteryCharge", "?")
        battery_critical = state.get("batteryCritical", False)
        last_activity = _fmt_datetime(lk.get("updateDate", ""))

        battery_str = f"{battery}%"
        if battery_critical:
            battery_str += " \u26a0\ufe0f CRITICAL"

        print(f"  {icon} {name} — {lock_state.title()} \u00b7 Battery {battery_str} \u00b7 Last: {last_activity}")
        print(f"     ID: {lock_id}")

        # Show LOCKS mapping hint if lock not in LOCKS dict
        if lock_id not in LOCKS:
            print(f"     \u2139\ufe0f  Add to LOCKS dict: \"{lock_id}\": \"{lk.get('name', 'Name')}\"")
    print()

def do_unlock(name: str = None):
    """Unlock a specific lock."""
    lock_id = find_lock_id(name)
    friendly = LOCKS.get(lock_id, name or "lock")
    print(f"\n\U0001f513  Unlocking {friendly}...")
    try:
        _api_post(f"smartlock/{lock_id}/action/unlock")
        print(f"  \u2705 Unlock command sent to {friendly}\n")
    except Exception as e:
        print(f"  \u274c Unlock failed: {e}\n")

def do_lock(name: str = None):
    """Lock a specific lock."""
    lock_id = find_lock_id(name)
    friendly = LOCKS.get(lock_id, name or "lock")
    print(f"\n\U0001f512  Locking {friendly}...")
    try:
        _api_post(f"smartlock/{lock_id}/action/lock")
        print(f"  \u2705 Lock command sent to {friendly}\n")
    except Exception as e:
        print(f"  \u274c Lock failed: {e}\n")

def show_logs(limit: int = 20):
    """Show recent activity log entries."""
    print(f"\n\U0001f4cb  Activity Log (last {limit})\n")
    locks = get_smartlocks()
    for lk in locks:
        lock_id = str(lk["smartlockId"])
        name = get_lock_name(lk)
        print(f"  \U0001f510 {name}")
        print("  " + "\u2500" * 55)
        try:
            entries = get_logs(lock_id, limit)
            if not entries:
                print("    No log entries.\n")
                continue
            for entry in entries:
                ts = _fmt_datetime(entry.get("date", ""))
                action_num = entry.get("action", 0)
                action = ACTION_NAMES.get(action_num, f"action:{action_num}")
                source_num = entry.get("source", 0)
                source = SOURCE_NAMES.get(source_num, f"source:{source_num}")
                auth_name = entry.get("name", "")

                # Icon based on action
                if action_num in (1, 252):
                    icon = "\U0001f513"
                elif action_num in (2, 243):
                    icon = "\U0001f512"
                elif action_num == 224:
                    icon = "\U0001f6aa"
                else:
                    icon = "\u2022"

                name_part = f" ({auth_name})" if auth_name else ""
                print(f"    {ts}  {icon} {action.title()} by {source}{name_part}")
            print()
        except Exception as e:
            print(f"    Error fetching logs: {e}\n")

def show_codes():
    """List all keypad authorization codes."""
    print("\n\U0001f510  Keypad Codes\n")
    locks = get_smartlocks()
    for lk in locks:
        lock_id = str(lk["smartlockId"])
        name = get_lock_name(lk)
        print(f"  \U0001f510 {name}")
        print("  " + "\u2500" * 55)
        try:
            auths = get_auth_list(lock_id)
            # Filter to keypad codes (type 13 = keypad code)
            codes = [a for a in auths if a.get("type") == 13]
            if not codes:
                print("    No keypad codes.\n")
                continue
            for auth in codes:
                auth_id = auth.get("id", "?")
                auth_name = auth.get("name", "Unknown")
                code = str(auth.get("code", ""))
                enabled = auth.get("enabled", False)
                allowed_from = _fmt_datetime(auth.get("allowedFromDate", ""))
                allowed_until = _fmt_datetime(auth.get("allowedUntilDate", ""))

                status = "\u2705" if enabled else "\u274c"
                print(f"    {status} {auth_name}  |  Code: {_mask_code(code)}  |  ID: {auth_id}")
                print(f"       Valid: {allowed_from} → {allowed_until}")
            print()
        except Exception as e:
            print(f"    Error fetching codes: {e}\n")

def create_code(name: str, code: str, from_dt: str, until_dt: str):
    """Create a time-limited keypad code for a guest."""
    if not validate_code(code):
        print(f"\n  \u274c Invalid code: {code}")
        print("  Rules: 6 digits, 1-9 only, cannot start with '12'")
        sys.exit(1)

    locks = get_smartlocks()
    if not locks:
        print("  No locks found.")
        sys.exit(1)

    lock_id = str(locks[0]["smartlockId"])
    lock_name = get_lock_name(locks[0])

    # Build the authorization payload
    payload = {
        "name": name,
        "type": 13,  # keypad code
        "code": int(code),
        "allowedFromDate": from_dt,
        "allowedUntilDate": until_dt,
        "allowedWeekDays": 127,  # all days
        "enabled": True,
    }

    print(f"\n\U0001f510  Creating keypad code on {lock_name}...")
    print(f"  Name: {name}")
    print(f"  Code: {_mask_code(code)}")
    print(f"  Valid: {from_dt} → {until_dt}")

    try:
        _api_put(f"smartlock/{lock_id}/auth", payload)
        print(f"  \u2705 Code created successfully!\n")
    except Exception as e:
        print(f"  \u274c Failed to create code: {e}\n")

def delete_code(auth_id: str):
    """Delete a specific authorization/code."""
    locks = get_smartlocks()
    if not locks:
        print("  No locks found.")
        sys.exit(1)

    lock_id = str(locks[0]["smartlockId"])
    lock_name = get_lock_name(locks[0])

    print(f"\n\U0001f5d1  Deleting code {auth_id} from {lock_name}...")
    try:
        _api_delete(f"smartlock/{lock_id}/auth/{auth_id}")
        print(f"  \u2705 Code {auth_id} deleted.\n")
    except Exception as e:
        print(f"  \u274c Failed to delete code: {e}\n")

def cleanup_codes():
    """Find and delete all expired codes."""
    print("\n\U0001f9f9  Cleaning Up Expired Codes\n")
    now = datetime.now(timezone.utc)
    removed = 0
    locks = get_smartlocks()
    for lk in locks:
        lock_id = str(lk["smartlockId"])
        lock_name = get_lock_name(lk)
        try:
            auths = get_auth_list(lock_id)
            codes = [a for a in auths if a.get("type") == 13]
            for auth in codes:
                until_str = auth.get("allowedUntilDate", "")
                if not until_str:
                    continue
                try:
                    until_str = until_str.replace("Z", "+00:00")
                    until_dt = datetime.fromisoformat(until_str)
                    if until_dt < now:
                        auth_id = auth.get("id")
                        auth_name = auth.get("name", "?")
                        print(f"  Removing expired: {auth_name} (until {_fmt_datetime(until_str)}) from {lock_name}")
                        _api_delete(f"smartlock/{lock_id}/auth/{auth_id}")
                        removed += 1
                except Exception:
                    continue
        except Exception as e:
            print(f"  Error processing {lock_name}: {e}")

    if removed == 0:
        print("  No expired codes found.\n")
    else:
        print(f"\n  \u2705 Removed {removed} expired code(s).\n")

def show_guest_codes():
    """Cross-reference Hospitable reservations with active Nuki codes."""
    print("\n\U0001f510  Guest Codes — Hospitable Cross-Reference\n")

    # Get upcoming reservations via hospitable.py
    hospitable_script = Path.home() / ".openclaw/workspace/hospitable.py"
    if not hospitable_script.exists():
        print("  \u274c hospitable.py not found. Cannot cross-reference.\n")
        return

    try:
        result = subprocess.run(
            [sys.executable, str(hospitable_script), "--upcoming", "14"],
            capture_output=True, text=True, timeout=30,
        )
        upcoming_output = result.stdout
    except Exception as e:
        print(f"  \u274c Error running hospitable.py: {e}\n")
        return

    # Get all active codes
    locks = get_smartlocks()
    active_codes = {}
    for lk in locks:
        lock_id = str(lk["smartlockId"])
        try:
            auths = get_auth_list(lock_id)
            for auth in auths:
                if auth.get("type") == 13 and auth.get("enabled"):
                    code_name = auth.get("name", "").lower().strip()
                    active_codes[code_name] = {
                        "id": auth.get("id"),
                        "name": auth.get("name"),
                        "from": _fmt_datetime(auth.get("allowedFromDate", "")),
                        "until": _fmt_datetime(auth.get("allowedUntilDate", "")),
                        "lock": get_lock_name(lk),
                    }
        except Exception:
            continue

    # Print upcoming reservations output
    print("  \u250c\u2500\u2500 Upcoming Reservations:")
    print(upcoming_output)

    # Print active codes
    print("  \u250c\u2500\u2500 Active Keypad Codes:")
    if active_codes:
        for code_name, info in active_codes.items():
            print(f"    \u2705 {info['name']}  ({info['from']} → {info['until']})  @{info['lock']}")
    else:
        print("    No active keypad codes.")
    print()

    # Simple name matching to flag missing codes
    # Parse guest names from hospitable output (lines with IN/OUT markers)
    import re
    guest_names = set()
    for line in upcoming_output.split("\n"):
        # Match patterns like "IN   Guest Name  @Property" or "OUT  Guest Name  @Property"
        match = re.search(r"(?:IN|OUT)\s+(.+?)\s+@", line)
        if match:
            guest_names.add(match.group(1).strip().lower())

    if guest_names:
        print("  \u250c\u2500\u2500 Code Status per Guest:")
        for guest in sorted(guest_names):
            has_code = any(guest in cn or cn in guest for cn in active_codes)
            status = "\u2705 has code" if has_code else "\u26a0\ufe0f  NO CODE"
            print(f"    {status}  {guest.title()}")
        print()

def show_token_check():
    """Validate token with GET /smartlock, check token file age."""
    print("\n\U0001f511  Nuki Token Health Check\n")

    if not TOKEN_PATH.exists():
        print("  \u274c Token file not found!")
        print(f"  Expected: {TOKEN_PATH}")
        return

    stat = TOKEN_PATH.stat()
    age_days = (date.today() - date.fromtimestamp(stat.st_mtime)).days
    print(f"  Token file: {TOKEN_PATH}")
    print(f"  Last modified: {age_days} day(s) ago")

    # Validate with API call
    try:
        locks = get_smartlocks()
        print(f"  \u2705 API connection OK — {len(locks)} smart lock(s) found")
        for lk in locks:
            lock_id = str(lk["smartlockId"])
            name = lk.get("name", "?")
            print(f"     \U0001f510 {name} (ID: {lock_id})")
    except Exception as e:
        print(f"  \u274c API connection FAILED: {e}")

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or args[0] == "--status":
        show_status()
    elif args[0] == "--unlock":
        name = args[1] if len(args) > 1 else None
        do_unlock(name)
    elif args[0] == "--lock":
        name = args[1] if len(args) > 1 else None
        do_lock(name)
    elif args[0] == "--logs":
        try:
            limit = int(args[1]) if len(args) > 1 else 20
        except ValueError:
            limit = 20
        show_logs(limit)
    elif args[0] == "--codes":
        show_codes()
    elif args[0] == "--create-code":
        if len(args) < 5:
            print("Usage: nuki.py --create-code <name> <code> <from> <until>")
            print("  code: 6 digits (1-9), not starting with '12'")
            print("  from/until: ISO datetime (e.g. 2026-02-20T15:00)")
            print(f"\n  Suggested random code: {generate_code()}")
            sys.exit(1)
        create_code(args[1], args[2], args[3], args[4])
    elif args[0] == "--delete-code":
        if len(args) < 2:
            print("Usage: nuki.py --delete-code <auth_id>")
            sys.exit(1)
        delete_code(args[1])
    elif args[0] == "--cleanup":
        cleanup_codes()
    elif args[0] == "--guest-codes":
        show_guest_codes()
    elif args[0] == "--token-check":
        show_token_check()
    elif args[0] in ("--help", "-h"):
        print(__doc__)
    else:
        print(f"Unknown command: {args[0]}")
        print(__doc__)

if __name__ == "__main__":
    main()
