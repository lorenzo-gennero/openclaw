---
name: deals
description: Track Mac Mini M4 prices on Willhaben (AT) and Kleinanzeigen (DE). Use when Lorenzo asks about Mac Mini deals, prices, or listings.
metadata:
  openclaw:
    emoji: "\U0001f4b0"
---

# Deals

## Commands

```bash
# Check both sites, show new + cheapest listings
python3 ~/.openclaw/workspace/mac_mini_tracker.py

# Show ALL current listings (not just new)
python3 ~/.openclaw/workspace/mac_mini_tracker.py --all

# Price history and trends from DB
python3 ~/.openclaw/workspace/mac_mini_tracker.py --history

# Clear the seen-listings database
python3 ~/.openclaw/workspace/mac_mini_tracker.py --reset
```

---

## Trigger Phrases

### Italian
- `mac mini`, `prezzi mac mini`, `offerte mac mini`
- `willhaben`, `kleinanzeigen`
- `quanto costa un mac mini`

### English
- `mac mini deals`, `mac mini prices`, `cheapest mac mini`
- `check willhaben`, `check kleinanzeigen`
- `any new listings`

---

## Negotiation Messages

When Lorenzo asks to draft a message for a listing:
- **10-15% below asking price**
- **English** (both platforms serve German-speaking markets but sellers often accept English)
- **Polite, direct, 3-4 sentences**
- Mention quick pickup and cash payment
- Example: "Hi, I'm interested in your Mac Mini M4. Would you accept EUR X? I can pick it up today/tomorrow and pay cash. Thanks!"

---

## Rules

- **Run the script first** — never answer from memory
- **Summarize concisely** — top 3 cheapest, any new listings, price trend
- **Respond in Lorenzo's language**
