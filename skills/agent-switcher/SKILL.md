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
- **airbnb** — Hospitable API, bookings, guests, check-ins
- **music** — GENNRO music production, DJ career
- **dev** — Technical/coding tasks

## How to Switch

```bash
bash ~/.openclaw/workspace/switch_agent.sh <agent_id>
```

Example — switch to airbnb agent:
```bash
bash ~/.openclaw/workspace/switch_agent.sh airbnb
```

## Rules
- After running the script, confirm the switch with a short TTS message.
- Example: "Switching you to the Airbnb agent now!"
- The switch takes effect on Lorenzo's NEXT message.
- To switch back: bash ~/.openclaw/workspace/switch_agent.sh main
