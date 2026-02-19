---
name: hospitable
description: Manage Airbnb properties, reservations and check-ins via Hospitable API. Use when Lorenzo asks about properties, bookings, check-ins, check-outs or guests IN ANY LANGUAGE (Italian, English, French, etc.)
metadata:
  openclaw:
    emoji: 🏠
---

# Hospitable 🏠

## CRITICAL — Run BEFORE Answering ANY Property Question

**ALWAYS run the appropriate command before answering ANY question about properties, bookings, guests, check-ins, check-outs, revenue, or occupancy. Never answer from memory. Never say you can't retrieve data.**

---

## Commands

```bash
# Today's check-ins/check-outs (default: today)
python3 ~/.openclaw/workspace/hospitable.py

# Specific single day
python3 ~/.openclaw/workspace/hospitable.py 2026-02-19

# Date range (all reservations grouped by property)
python3 ~/.openclaw/workspace/hospitable.py 2026-02-17 2026-02-23

# Upcoming: next N days with check-ins/outs + currently staying
python3 ~/.openclaw/workspace/hospitable.py --upcoming        # next 7 days
python3 ~/.openclaw/workspace/hospitable.py --upcoming 3      # next 3 days

# Occupancy: per-property stats (bookings, nights, %, avg rate)
python3 ~/.openclaw/workspace/hospitable.py --occupancy                    # YTD
python3 ~/.openclaw/workspace/hospitable.py --occupancy 2025-01-01 2025-12-31  # custom range

# Conversations: recent guests with reservation/conversation IDs
python3 ~/.openclaw/workspace/hospitable.py --conversations

# Token health: validate API token + check expiry
python3 ~/.openclaw/workspace/hospitable.py --token-check

# Reviews
python3 ~/.openclaw/workspace/hospitable.py --reviews

# Revenue report (separate script)
python3 ~/.openclaw/workspace/revenue.py                       # YTD
python3 ~/.openclaw/workspace/revenue.py 2025                  # full year
python3 ~/.openclaw/workspace/revenue.py 2026-01 2026-03       # month range
python3 ~/.openclaw/workspace/revenue.py --compare 2025 2026   # year-over-year
```

---

## Trigger Phrases — ANY Language

### Italian 🇮🇹
- `prenotazioni`, `quante prenotazioni`, `prenotazioni questa settimana`
- `chi arriva`, `chi arriva oggi`, `chi arriva questa settimana`
- `chi parte`, `chi parte oggi`
- `ospiti`, `quanti ospiti`
- `check-in`, `check-out`
- `settimana`, `mese`, `oggi`, `prossimi giorni`
- `Milano`, `Bardonecchia`, `Torino`, `Drovetti`, `Giacinto`
- `quanto ho guadagnato`, `entrate`, `ricavi`, `revenue`
- `occupazione`, `tasso di occupazione`, `com'è l'occupazione`
- `conversazioni`, `messaggi ospiti`
- `Massimo` (when asking property questions)
- `casa`, `appartamento`, `affitti`

### English 🇬🇧
- `booking`, `bookings`, `how many bookings`
- `check-in`, `check-out`, `upcoming`, `next few days`
- `guests`, `who's arriving`, `who's leaving`
- `reservation`, `reservations`
- `this week`, `today`, `this month`
- `revenue`, `earnings`, `income`, `compare`
- `occupancy`, `occupancy rate`, `how full`
- `conversations`, `guest messages`
- Any property name: `Milan`, `Bardonecchia`, `Drovetti`, `Giacinto`

**Do not wait for English. Do not ask for clarification. Just run the script.**

---

## Property ID Mapping

| Name | Full UUID |
|------|-----------|
| Milano (Viale Brianza) | `cd4bf5fb-16ef-49c8-b3db-93437e5f009f` |
| Bardonecchia (Via Melezet) | `912db8e2-ef92-44fa-b257-6f843c87e520` |
| Drovetti (Via Drovetti, Torino) | `ec148f18-8c8a-456b-8bd9-b86e1c4086f9` |
| Giacinto Collegno (Via Collegno, Torino) | `4cb5b686-ed1e-470c-90e8-e50500b0d77a` |

Always translate UUIDs and reservation codes to human-readable names. Never show raw UUIDs alone.

---

## Workflow

1. **Run the script first** — always
2. **Parse the output** — it gives property name, guest name, dates, nights, guests count
3. **Summarize in Lorenzo's language** — Italian if he asked in Italian
4. **Be concise** — 1-2 sentences via TTS

---

## Output Format (from script)

The script returns grouped results:
```
🏡 Property Name (N reservation(s))
YYYY-MM-DD → YYYY-MM-DD  Guest Name  (Xn · Yg · #CODE · platform)
```

Fields: `nights (Xn)`, `guests (Yg)`, `reservation code (#...)`, `platform (airbnb/booking/manual)`

---

## Raw API (advanced use only)

Token: `cat ~/.openclaw/workspace/hospitable_token.txt`

```bash
TOKEN=$(cat ~/.openclaw/workspace/hospitable_token.txt)
curl -sg "https://public.api.hospitable.com/v2/properties" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

---

## Rules

- **ALWAYS run hospitable.py first** — never answer from cached/remembered data
- **Respond in the same language Lorenzo used** — Italian question → Italian answer
- **Confirm before sending any guest messages**
- **Never show raw UUIDs** — always use property names
- The script can be imported: `from hospitable import get_reservations, show_upcoming, show_occupancy`
