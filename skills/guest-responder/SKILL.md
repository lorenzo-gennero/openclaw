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

### CRITICAL: Always Check Config + Style Guide for Problem-Related Messages

When Lorenzo says something like "electricity problem", "sofa bed", "hot water", "elevator", "AC", "heating", "cold", "WiFi", "keys", "lockbox", "boiler" — you MUST:
1. Read `guest_config.json` — find the matching entry in `troubleshooting_videos` AND `troubleshooting_instructions`
2. Read `lorenzo_style_guide.md` — find the "Troubleshooting by Category" section for the REAL pattern Lorenzo used
3. Include the YouTube link AND the step-by-step instructions in the draft
4. Follow Lorenzo's 5-step approach: acknowledge → self-service fix → offer escalation → follow up → compensate if needed

**Milano troubleshooting (quick reference):**
- Electricity/power out: Check switches RIGHT side of door first. If not fixed → cellar. Video `https://youtu.be/Th1pxWFlLuU` + backup keys lockbox code 2709, door behind lift (ground floor), cellar door. Offer to come by.
- Circuit breakers (apartment-level): "On the left-hand side of the entrance door"
- Sofa bed open: `https://youtu.be/BLICzW5BnLU` (30 EUR surcharge for setup)
- Sofa bed close: `https://youtu.be/BR-SsjCgqCY`
- Hot water/shower: `https://youtu.be/gMiZkQbm04c`
- Building exit: White button in front of elevator at ground floor. End of video: `https://youtu.be/VWsDkN7Zwus`
- AC cold: MODE button → snowflake icon. In check-in video at 50-second mark.
- AC heat: MODE button → sun icon.

**Drovetti troubleshooting (quick reference):**
- AC/climate: Link digital guide FIRST `https://v2.hostfully.com/gwznxzs` THEN video `https://youtu.be/bo4tJ04uHy8`
- Heating cold at night: Central heating off 11pm-5am. Radiator valves to 4-5. AC on sun icon as backup.
- Hot water/boiler: Switch next to bathroom mirror (left side). If off, turn ON and wait.
- Building entry: Host buzzes in remotely. Guest must message 20 min before.

**Giacinto Collegno troubleshooting (quick reference):**
- Electricity/power: Check wall buttons next to fridge, behind Nespresso machine. All must be ON.
- Heating cold at night: Central heating off 11pm-5am. Radiator valves to 4-5. AC on sun icon.
- Induction cooktop: Regular coffee maker won't work. Use Nespresso with pods.

**Bardonecchia troubleshooting (quick reference):**
- Hot water/boiler: Electric 80L, switch RIGHT side of bathroom door. Leave ON. Takes 1-2 hours. 4 consecutive showers NOT possible.
- TV remote: Small = volume. Big remote: SOURCE → HDMI 1/2 → Prime Video. Netflix needs guest's own account.

**WiFi (all properties):**
- Check with ISP. Offer Airalo eSIM backup: code LORENZ5261, https://ref.airalo.com/1z4y

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

| Name | Key Return | Check-in Method | Check-in Video (EN) | Check-in Video (IT) |
|------|------------|-----------------|---------------------|---------------------|
| Milano | Keys on table | Nuki keypad 196767 | youtu.be/VWsDkN7Zwus | youtu.be/qm7YtDNaZoE |
| Drovetti | Keys in lockbox | Lockbox 3006 + remote buzzer | youtu.be/k0ExFJAwdYY | youtu.be/F5uMElJKNUw |
| Bardonecchia | Keys in lockbox | Lockbox 3006 | youtube.com/watch?v=YBYohemaAo8 | youtu.be/-S1LGzRrON8 |
| Giacinto Collegno | Keys on table | Lockbox 2709 + remote buzzer | youtube.com/watch?v=sgj4z3YtONE | youtu.be/Z8Yjq42AAlA |

---

## Rules

- **NEVER auto-send** — always show draft first
- **Drafts MUST be TEXT** — use the `message` tool, NOT TTS, so Lorenzo can copy-paste
- **Match guest's language** — Italian guest → Italian reply
- **Use Lorenzo's voice** — warm, direct, professional (see style guide)
- **1-2 emojis max** — 😊 👍🏻 are most common
- **Property-specific details** — check `guest_config.json` for videos, codes, links, and `troubleshooting_instructions`
- **Troubleshooting** — when guests report ANY problem, check `guest_config.json` → `troubleshooting_instructions` for the exact fix. Include relevant YouTube video AND step-by-step instructions.
- **Recommendations** — when guests ask for tips/restaurants/things to do, link the property's Hostfully guidebook from `guest_config.json` → `recommendations_link`
- **Heating issues (Turin)** — Central heating off 11pm-5am. Radiator valves to 4-5. AC as heat pump (sun icon).
- **Include Hostfully guide** — In check-in instructions, ALWAYS include the property's Hostfully digital guide link inline.
- **Config file:** `~/.openclaw/workspace/guest_config.json` (editable by Lorenzo)
- **Style guide:** `~/.openclaw/workspace/lorenzo_style_guide.md` (100+ real examples, all troubleshooting patterns)
- **Full analysis:** `~/.openclaw/workspace/hospitable_messages_analysis.md` (comprehensive reference)
