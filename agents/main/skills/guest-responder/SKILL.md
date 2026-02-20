---
name: guest-responder
description: Draft guest messages in Lorenzo's voice. Use when Lorenzo asks to reply to a guest, write a message, or draft a response IN ANY LANGUAGE (Italian, English).
metadata:
  openclaw:
    emoji: "✉️"
---

# Guest Responder ✉️

## CRITICAL — Draft Messages, NEVER Auto-Send

**Always show the draft to Lorenzo for approval before sending. Never send messages automatically.**

---

## Quick Templates (Script)

For common message types, run the template generator first:

```bash
# Welcome / booking confirmation
python3 ~/.openclaw/workspace/guest_responder.py --welcome "Guest Name" Milano
python3 ~/.openclaw/workspace/guest_responder.py --welcome "Guest Name" Drovetti --lang it

# Check-in instructions (with door code)
python3 ~/.openclaw/workspace/guest_responder.py --checkin "Guest Name" Milano --code 345678
python3 ~/.openclaw/workspace/guest_responder.py --checkin "Guest Name" Drovetti --lang it

# During-stay check-in
python3 ~/.openclaw/workspace/guest_responder.py --during-stay "Guest Name"
python3 ~/.openclaw/workspace/guest_responder.py --during-stay "Guest Name" --lang it

# Checkout reminder
python3 ~/.openclaw/workspace/guest_responder.py --checkout "Guest Name" Milano
python3 ~/.openclaw/workspace/guest_responder.py --checkout "Guest Name" Drovetti --lang it

# Post-stay / review request
python3 ~/.openclaw/workspace/guest_responder.py --post-stay "Guest Name"
python3 ~/.openclaw/workspace/guest_responder.py --post-stay "Guest Name" --lang it

# Registration form
python3 ~/.openclaw/workspace/guest_responder.py --form "Guest Name" Drovetti ABC123
python3 ~/.openclaw/workspace/guest_responder.py --form "Guest Name" Milano --lang it

# List all templates
python3 ~/.openclaw/workspace/guest_responder.py --list-templates
```

---

## Free-Form Replies (Style Guide)

For messages that don't fit a template (complaints, questions, custom situations), read the style guide and draft a reply in Lorenzo's voice:

1. **Read the style guide:** `~/.openclaw/workspace/lorenzo_style_guide.md`
2. **Check context:** property, dates, language, guest history
3. **Draft reply** following Lorenzo's patterns
4. **Show draft to Lorenzo** for approval

---

## Trigger Phrases — ANY Language

### Italian 🇮🇹
- `rispondi all'ospite`, `rispondi al guest`
- `scrivi al guest`, `scrivi all'ospite`
- `messaggio per`, `risposta per`
- `cosa gli dico`, `cosa gli scrivo`
- `mandagli un messaggio`
- `checkout reminder`, `promemoria checkout`
- `messaggio di benvenuto`
- `chiedi la recensione`

### English 🇬🇧
- `draft reply`, `write reply`, `reply to guest`
- `guest message`, `message the guest`
- `write to`, `respond to`
- `send welcome`, `send checkout`
- `ask for review`
- `check-in instructions`

**Do not wait for clarification. Draft the message immediately based on context.**

---

## Workflow

1. **Identify the message type** — welcome, check-in, during-stay, checkout, post-stay, form, or free-form
2. **Detect language** — match the guest's language (Italian → Italian, English → English)
3. **Run template** if applicable, or read style guide for free-form
4. **Present draft** to Lorenzo
5. **Wait for approval** — Lorenzo may edit before sending
6. **Send via Hospitable** if Lorenzo confirms (use `hospitable.py` send function)

---

## Properties

| Name | Key Return | Check-in Method |
|------|------------|-----------------|
| Milano | Keys on table | Nuki smart lock code |
| Drovetti | Keys in lockbox | Lockbox + remote buzzer |
| Bardonecchia | Keys on table | Key handoff |
| Giacinto Collegno | Keys on table | Key handoff |

---

## Rules

- **NEVER auto-send** — always show draft first
- **Drafts MUST be TEXT** — use the `message` tool, NOT TTS, so Lorenzo can copy-paste
- **Match guest's language** — Italian guest → Italian reply
- **Use Lorenzo's voice** — warm, direct, professional (see style guide)
- **1-2 emojis max** — 😊 👍🏻 are most common
- **Property-specific details** — check `guest_config.json` for videos, codes, links
- **Config file:** `~/.openclaw/workspace/guest_config.json` (editable by Lorenzo)
- **Style guide:** `~/.openclaw/workspace/lorenzo_style_guide.md` (50+ real examples)
