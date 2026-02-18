---
name: hospitable
description: Manage Airbnb properties, reservations and check-ins via Hospitable API. Use when Lorenzo asks about properties, bookings, check-ins, check-outs or guests IN ANY LANGUAGE.
metadata:
  openclaw:
    emoji: 🏠
---

# Hospitable 🏠

## ⚡ TRIGGER — ANY Language

**When Lorenzo asks ANYTHING about bookings, check-ins, check-outs, guests, or properties IN ANY LANGUAGE (English, Italian, French, etc.), IMMEDIATELY run:**

```bash
python3 ~/.openclaw/workspace/hospitable.py
```

### Italian triggers (examples — not exhaustive):
- "quante prenotazioni" → bookings query
- "chi arriva oggi" / "chi arriva questa settimana" → check-ins
- "chi parte oggi" → check-outs
- "ospiti" → guests
- "proprietà" → properties
- "settimana" / "mese" → date range query
- "Massimo" / "Milano" / "Bardonecchia" / "Torino" → property reference

**Do not wait for English. Do not ask for clarification. Just run the script.**

## ⚡ Primary Method — Use hospitable.py

For ALL reservation queries, run `~/.openclaw/workspace/hospitable.py`. Do NOT craft raw curl commands for reservations.

```bash
# Today's check-ins and check-outs
python3 ~/.openclaw/workspace/hospitable.py

# Specific day
python3 ~/.openclaw/workspace/hospitable.py 2026-02-19

# Date range (all reservations grouped by property)
python3 ~/.openclaw/workspace/hospitable.py 2026-02-01 2026-03-31

# This week example
python3 ~/.openclaw/workspace/hospitable.py 2026-02-17 2026-02-23
```

## Properties
| Short ID | Full UUID | Name |
|----------|-----------|------|
| cd4bf5fb | cd4bf5fb-16ef-49c8-b3db-93437e5f009f | Milano |
| 912db8e2 | 912db8e2-ef92-44fa-b257-6f843c87e520 | Bardonecchia |
| ec148f18 | ec148f18-8c8a-456b-8bd9-b86e1c4086f9 | Drovetti (Turin) |
| 4cb5b686 | 4cb5b686-ed1e-470c-90e8-e50500b0d77a | Giacinto Collegno (Turin) |

## Raw API (advanced use only)

Token: `cat ~/.openclaw/workspace/hospitable_token.txt`

```bash
TOKEN=$(cat ~/.openclaw/workspace/hospitable_token.txt) && curl -sg "https://public.api.hospitable.com/v2/properties" -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
```

## Rules
- **Always use hospitable.py for reservation queries** — it handles auth, property names, guest names, and date filtering automatically.
- **Respond in the same language Lorenzo used** — if he asked in Italian, answer in Italian.
- Confirm before sending any guest messages.
- The script can be imported: `from hospitable import get_reservations` returns a list of dicts with `_property_name`, `guest`, `arrival_date`, `departure_date`, `nights`, `guests`, `code`, `platform`.
