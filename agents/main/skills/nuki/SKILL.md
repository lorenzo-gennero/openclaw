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

# Unlock / Lock
python3 ~/.openclaw/workspace/nuki.py --unlock
python3 ~/.openclaw/workspace/nuki.py --lock

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
- `serratura`, `stato serratura`, `porta`, `apri`, `chiudi`
- `sblocca`, `blocca`, `codice`, `codici`, `codice ospite`
- `chi \u00e8 entrato`, `log serratura`, `accessi`
- `batteria serratura`, `Giacinto` (lock context)

### English \U0001f1ec\U0001f1e7
- `lock`, `unlock`, `door`, `keypad`, `access code`
- `guest code`, `lock status`, `battery`, `activity log`

**Do not wait for English. Do not ask for clarification. Just run the script.**

---

## Rules

- **ALWAYS run nuki.py first** — never answer from cached/remembered data
- **Respond in the same language Lorenzo used**
- **Confirm before unlocking** — safety check
- **Never show raw auth IDs alone** — always include guest name
