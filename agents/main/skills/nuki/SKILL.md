---
name: nuki
description: Manage Nuki Smart Lock — lock/unlock, guest keypad codes, activity logs, battery status. Use when Lorenzo asks about the lock, door, access codes, or guest keys IN ANY LANGUAGE.
metadata:
  openclaw:
    emoji: "\U0001f510"
---

# Nuki Smart Lock \U0001f510

## CRITICAL — Run BEFORE Answering ANY Lock/Door Question

**ALWAYS run the appropriate command before answering ANY question about the lock, door, guest codes, access, or lock status. Never answer from memory.**

---

## Commands

```bash
# Lock status + battery (default)
python3 ~/.openclaw/workspace/nuki.py
python3 ~/.openclaw/workspace/nuki.py --status

# Unlock a lock
python3 ~/.openclaw/workspace/nuki.py --unlock
python3 ~/.openclaw/workspace/nuki.py --unlock "Giacinto Collegno"

# Lock a lock
python3 ~/.openclaw/workspace/nuki.py --lock
python3 ~/.openclaw/workspace/nuki.py --lock "Giacinto Collegno"

# Activity log (last N entries, default 20)
python3 ~/.openclaw/workspace/nuki.py --logs
python3 ~/.openclaw/workspace/nuki.py --logs 50

# List all keypad codes
python3 ~/.openclaw/workspace/nuki.py --codes

# Create a guest keypad code (6 digits, 1-9, no '12' prefix)
python3 ~/.openclaw/workspace/nuki.py --create-code "Mario Rossi" 345678 2026-02-20T15:00 2026-02-23T11:00

# Delete a keypad code
python3 ~/.openclaw/workspace/nuki.py --delete-code <auth_id>

# Remove all expired codes
python3 ~/.openclaw/workspace/nuki.py --cleanup

# Cross-reference Hospitable guests with keypad codes
python3 ~/.openclaw/workspace/nuki.py --guest-codes

# Token health check
python3 ~/.openclaw/workspace/nuki.py --token-check
```

---

## Trigger Phrases — ANY Language

### Italian \U0001f1ee\U0001f1f9
- `serratura`, `stato serratura`, `la serratura`
- `porta`, `la porta`, `apri la porta`
- `chiave`, `chiavi`, `codice`, `codici`
- `apri`, `sblocca`, `apri la porta`
- `chiudi`, `blocca`, `chiudi la porta`
- `codice ospite`, `codice per l'ospite`
- `chi \u00e8 entrato`, `log serratura`, `accessi`
- `batteria serratura`, `batteria porta`
- `Giacinto`, `Collegno` (when asking about lock/door)

### English \U0001f1ec\U0001f1e7
- `lock`, `unlock`, `door`, `smart lock`
- `keypad`, `keypad code`, `access code`
- `guest code`, `create code`, `delete code`
- `lock status`, `battery`, `lock battery`
- `who entered`, `activity log`, `lock log`
- `expired codes`, `cleanup codes`

**Do not wait for English. Do not ask for clarification. Just run the script.**

---

## Property — Lock Mapping

| Property | Lock | ID |
|----------|------|----|
| Milano (Viale Brianza) | Nuki Smart Lock | 694097108 |

---

## Workflow

1. **Run the script first** — always
2. **Parse the output** — it gives lock state, battery, codes, logs
3. **Summarize in Lorenzo's language** — Italian if he asked in Italian
4. **Be concise** — 1-2 sentences via TTS

---

## Code Rules

When creating guest codes:
- **6 digits only**, digits 1-9 (no zeros)
- **Cannot start with '12'** (Nuki restriction)
- Use `--create-code` with guest name, code, check-in datetime, check-out datetime
- Always verify with `--codes` after creation
- Run `--cleanup` after guest checkout to remove expired codes

---

## Rules

- **ALWAYS run nuki.py first** — never answer from cached/remembered data
- **Respond in the same language Lorenzo used**
- **Confirm before unlocking** — safety check
- **Never show raw auth IDs alone** — always include guest name
- The script can be imported: `from nuki import get_smartlocks, show_status, generate_code`
