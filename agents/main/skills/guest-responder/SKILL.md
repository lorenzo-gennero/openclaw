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

For messages that don't fit a template (complaints, questions, custom situations):

1. **Read the config file FIRST:** `cat ~/.openclaw/workspace/guest_config.json` — check for relevant videos, links, and property details
2. **Read the style guide:** `cat ~/.openclaw/workspace/lorenzo_style_guide.md` — check the Troubleshooting section for matching videos and the example pairs for tone
3. **Check context:** property, dates, language, guest history
4. **Include relevant links:** If the guest has a PROBLEM, you MUST check `troubleshooting_videos` in the config and include the matching YouTube video in your draft. If the guest asks for RECOMMENDATIONS, include the `recommendations_link`.
5. **Draft reply** following Lorenzo's patterns
6. **Show draft to Lorenzo** for approval

### CRITICAL: Always Check Config for Problem-Related Messages

When Lorenzo says something like "electricity problem", "sofa bed", "hot water", "elevator" — you MUST:
1. Read `guest_config.json`
2. Find the matching video in `troubleshooting_videos` for that property
3. Include the YouTube link in the draft

**Milano troubleshooting videos (quick reference):**
- Sofa bed open: `https://youtu.be/BLICzW5BnLU`
- Sofa bed close: `https://youtu.be/BR-SsjCgqCY`
- Hot water/shower: `https://youtu.be/gMiZkQbm04c`
- Electricity/breaker: `https://youtu.be/Th1pxWFlLuU`
- Elevator: `https://youtu.be/VWsDkN7Zwus`

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

1. **Read `guest_config.json`** — ALWAYS do this first to have property details, videos, and links ready
2. **Identify the message type** — welcome, check-in, during-stay, checkout, post-stay, form, or free-form
3. **Detect language** — match the guest's language (Italian → Italian, English → English)
4. **Run template** if applicable, or read style guide for free-form
5. **For problems:** check `troubleshooting_videos` and include the relevant YouTube link
6. **For recommendations:** include the property's `recommendations_link`
7. **Present draft as TEXT** to Lorenzo (use message tool, NOT TTS)
8. **Wait for approval** — Lorenzo may edit before sending
9. **Send via Hospitable** if Lorenzo confirms (use `hospitable.py` send function)

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
- **Troubleshooting videos** — when guests report problems (sofa bed, hot water, electricity, elevator), check `guest_config.json` → `troubleshooting_videos` and include the relevant YouTube link in the reply
- **Recommendations** — when guests ask for tips/restaurants/things to do, link the property's Hostfully guidebook from `guest_config.json` → `recommendations_link`
- **Config file:** `~/.openclaw/workspace/guest_config.json` (editable by Lorenzo)
- **Style guide:** `~/.openclaw/workspace/lorenzo_style_guide.md` (50+ real examples)
