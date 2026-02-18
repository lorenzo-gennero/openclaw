---
name: agent-switcher
description: Switch between specialized agents (main, manager, airbnb, music, dev) from Telegram. Use when Lorenzo types /agent <name> or asks to switch to a specific agent.
metadata:
  openclaw:
    emoji: 🔀
---

# Agent Switcher 🔀

When Lorenzo says `/agent <name>` or "switch to airbnb agent" etc., run the switch script.

## Available Agents
- **main** — General assistant (default)
- **manager** — Property & business management
- **airbnb** / **massimo** — Hospitable API, bookings, guests, check-ins
- **music** / **josh** — GENNRO music production, DJ career
- **dev** — Technical/coding tasks

## How to Switch

```bash
bash ~/.openclaw/workspace/switch_agent.sh <name>
```

The script accepts both friendly names and agent IDs — case-insensitive.

| Lorenzo says | Command |
|---|---|
| "Massimo" | `bash switch_agent.sh massimo` |
| "Josh" | `bash switch_agent.sh josh` |
| "Dev" or "Developer" | `bash switch_agent.sh dev` |
| "Manager" | `bash switch_agent.sh manager` |
| "back", "main", "home" | `bash switch_agent.sh main` |

## Rules
- After running the script, confirm the switch with a short TTS message.
- Example: "Eccomi, sono Massimo!" or "Josh here!"
- The switch takes effect on Lorenzo's NEXT message.
- To switch back: bash ~/.openclaw/workspace/switch_agent.sh main
