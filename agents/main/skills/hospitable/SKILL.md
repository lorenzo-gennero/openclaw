---
name: hospitable
description: Manage Airbnb properties, reservations, guest messages and calendar via the Hospitable API. Use this skill whenever Lorenzo asks about properties, bookings, check-ins, check-outs, guests, or wants to send messages to guests.
metadata:
  openclaw:
    emoji: 🏠
---

# Hospitable 🏠

## CRITICAL — Run BEFORE Answering ANY Property Question

**ALWAYS run the appropriate command before answering ANY question about properties, bookings, guests, check-ins, check-outs, revenue, or occupancy. Never answer from memory.**

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
- `ospiti`, `quanti ospiti`, `prossimi giorni`
- `check-in`, `check-out`
- `settimana`, `mese`, `oggi`
- `Milano`, `Bardonecchia`, `Torino`, `Drovetti`, `Giacinto`
- `quanto ho guadagnato`, `entrate`, `ricavi`, `revenue`
- `occupazione`, `tasso di occupazione`
- `conversazioni`, `messaggi ospiti`

### English 🇬🇧
- `booking`, `bookings`, `how many bookings`
- `check-in`, `check-out`, `upcoming`, `next few days`
- `guests`, `who's arriving`, `who's leaving`
- `revenue`, `earnings`, `income`, `compare`
- `occupancy`, `occupancy rate`
- `conversations`, `guest messages`
- Any property name

**Do not wait for English. Do not ask for clarification. Just run the script.**

---

## Properties

| Name | Full UUID |
|------|-----------|
| Milano (Viale Brianza) | `cd4bf5fb-16ef-49c8-b3db-93437e5f009f` |
| Bardonecchia (Via Melezet) | `912db8e2-ef92-44fa-b257-6f843c87e520` |
| Drovetti (Via Drovetti, Torino) | `ec148f18-8c8a-456b-8bd9-b86e1c4086f9` |
| Giacinto Collegno (Via Collegno, Torino) | `4cb5b686-ed1e-470c-90e8-e50500b0d77a` |

---

## Rules

- **ALWAYS run hospitable.py first** — never answer from cached/remembered data
- **Respond in the same language Lorenzo used**
- **Confirm before sending any guest messages**
- **Never show raw UUIDs** — always use property names
