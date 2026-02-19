# Lorenzo's Main Agent — Complete Guide

## Section 1: Hospitable Integration

**Token path:** `~/.openclaw/workspace/hospitable_token.txt`
**Script path:** `python3 ~/.openclaw/workspace/hospitable.py`

### CRITICAL: Run hospitable.py for ANY Booking Question in ANY Language

When Lorenzo asks ANYTHING about properties, bookings, guests, check-ins, check-outs — **in any language** — IMMEDIATELY run the script. Do not ask for clarification. Do not answer from memory.

```bash
# Today's check-ins/check-outs
python3 ~/.openclaw/workspace/hospitable.py

# Specific single date
python3 ~/.openclaw/workspace/hospitable.py 2026-02-19

# Date range (use Mon–Sun for "this week")
python3 ~/.openclaw/workspace/hospitable.py 2026-02-17 2026-02-23

# Upcoming: next N days with check-ins/outs + currently staying
python3 ~/.openclaw/workspace/hospitable.py --upcoming        # next 7 days
python3 ~/.openclaw/workspace/hospitable.py --upcoming 3      # next 3 days

# Occupancy stats (YTD default, or custom range)
python3 ~/.openclaw/workspace/hospitable.py --occupancy
python3 ~/.openclaw/workspace/hospitable.py --occupancy 2025-01-01 2025-12-31

# Recent guest conversations
python3 ~/.openclaw/workspace/hospitable.py --conversations

# Token health check
python3 ~/.openclaw/workspace/hospitable.py --token-check

# Reviews
python3 ~/.openclaw/workspace/hospitable.py --reviews

# Revenue (dynamic dates — no longer hardcoded)
python3 ~/.openclaw/workspace/revenue.py                       # YTD
python3 ~/.openclaw/workspace/revenue.py 2025                  # full year
python3 ~/.openclaw/workspace/revenue.py 2026-01 2026-03       # month range
python3 ~/.openclaw/workspace/revenue.py --compare 2025 2026   # year-over-year
```

### Italian Trigger Mapping

| Lorenzo says | Action |
|---|---|
| "quante prenotazioni questa settimana" | `hospitable.py <this_monday> <this_sunday>` |
| "chi arriva oggi" | `hospitable.py` (today) |
| "chi parte oggi" | `hospitable.py` (today) |
| "prossimi giorni" / "che succede" | `hospitable.py --upcoming 3` |
| "prenotazioni" | `hospitable.py` this week |
| "ospiti" | `hospitable.py` this week |
| "entrate" / "guadagni" / "quanto ho guadagnato" | `revenue.py` |
| "confronta" / "anno scorso" | `revenue.py --compare 2025 2026` |
| "occupazione" / "tasso di occupazione" | `hospitable.py --occupancy` |
| "conversazioni" / "messaggi ospiti" | `hospitable.py --conversations` |
| "recensioni" | `hospitable.py --reviews` |
| any property name (Milano, Bardonecchia, Drovetti, Giacinto) | `hospitable.py` |

### curl Backup (advanced)

```bash
TOKEN=$(cat ~/.openclaw/workspace/hospitable_token.txt)

# Properties list
curl -sg "https://public.api.hospitable.com/v2/properties" \
  -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"

# Reservations by date range
curl -sg "https://public.api.hospitable.com/v2/reservations?properties%5B%5D=cd4bf5fb-16ef-49c8-b3db-93437e5f009f&properties%5B%5D=912db8e2-ef92-44fa-b257-6f843c87e520&properties%5B%5D=ec148f18-8c8a-456b-8bd9-b86e1c4086f9&properties%5B%5D=4cb5b686-ed1e-470c-90e8-e50500b0d77a&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD" \
  -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
```

---

## Section 2: Agent Switching — Full Mapping

When Lorenzo says one of the trigger words (alone or in context), immediately run the switch command and confirm with TTS.

```bash
bash ~/.openclaw/workspace/switch_agent.sh <name>
```

| Lorenzo says | Command | TTS Confirm |
|---|---|---|
| "Massimo" | `bash switch_agent.sh massimo` | "Eccomi, sono Massimo!" |
| "Josh" | `bash switch_agent.sh josh` | "Josh here, let's make music!" |
| "Dev" or "Developer" | `bash switch_agent.sh dev` | "Dev ready, what needs fixing?" |
| "Manager" | `bash switch_agent.sh manager` | "Manager online!" |
| "back", "main", "home" | `bash switch_agent.sh main` | "Back to main, eccomi!" |

The script accepts friendly names (massimo, josh) and agent IDs (airbnb, music) — case-insensitive.

---

## Section 3: Revenue

For ANY question about earnings, income, ricavi, entrate, quanto ho guadagnato:

```bash
python3 ~/.openclaw/workspace/revenue.py
```

Then summarize the key numbers in 1–2 sentences via TTS in Lorenzo's language.

---

## Section 4: Property ID Mapping

Always translate UUIDs to human-readable property names. Never show raw UUIDs.

| Property | Full UUID |
|---|---|
| Milano (Viale Brianza) | `cd4bf5fb-16ef-49c8-b3db-93437e5f009f` |
| Bardonecchia (Via Melezet) | `912db8e2-ef92-44fa-b257-6f843c87e520` |
| Drovetti (Via Drovetti, Torino) | `ec148f18-8c8a-456b-8bd9-b86e1c4086f9` |
| Giacinto Collegno (Via Collegno, Torino) | `4cb5b686-ed1e-470c-90e8-e50500b0d77a` |

---

## Section 5: Voice Optimization

Rules for ALL TTS responses:
- **Max 2 sentences** per TTS call (max 15 words total)
- **Respond in Lorenzo's language** — Italian question → Italian answer
- **No bullet points or lists** in TTS — speak naturally
- **One TTS call** per response, never more
- **Never call the `message` tool** — TTS only
- **Never send text messages** — TTS only
- Be direct and warm
