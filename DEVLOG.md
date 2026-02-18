# OpenClaw DevLog

## 2026-02-19 — Full System Overhaul

### Changes Made

1. **AGENTS.md propagated to all workspaces** — AGENTS.md in main workspace already had correct content (TTS only, no message tool, max 15 words). Propagated to: workspace-airbnb, workspace-music, workspace-manager, workspace-dev.

2. **SOUL.md (main)** — Completely rewritten with 5 sections: Hospitable Integration (with curl backup), Agent Switching full mapping, Revenue, Property IDs, Voice Optimization.

3. **workspace-airbnb/SOUL.md (Massimo)** — Rewritten with all 4 properties, mandatory hospitable.py usage, Italian trigger mapping, switch-back instructions.

4. **workspace-music/SOUL.md (Josh)** — Rewritten with Lorenzo's full context (GENNRO, Ableton, minimal house), Chris Stussy/Josh Baker/Rossi styles, Ableton tips, FabFilter usage.

5. **workspace-manager/SOUL.md** — Rewritten with smart routing logic (keywords → correct agent), revenue section, Lorenzo's business context.

6. **workspace-dev/SOUL.md** — Rewritten with full OpenClaw system knowledge, key commands, reload config, hospitable integration, known issues.

7. **skills/agent-switcher/SKILL.md** — Updated with full name→command mapping table including friendly names (massimo, josh).

8. **skills/hospitable/SKILL.md** — Already excellent; no changes needed.

9. **GitHub** — Committed and pushed: `feat: complete system overhaul - all agents, hospitable, switching` (13 files changed).

---

### How to Use the Agent System

- Say **"Massimo"** → switch to Airbnb property manager
- Say **"Josh"** → switch to Music production assistant
- Say **"Manager"** → switch to Business Manager
- Say **"Dev"** → switch to Developer
- Say **"back"** or **"main"** → return to main agent

---

### Hospitable Integration

- Ask any booking question in any language (Italian, English, French...)
- Massimo will run `python3 ~/.openclaw/workspace/hospitable.py` and answer
- Trigger words: prenotazioni, ospiti, chi arriva, chi parte, bookings, guests, check-in, check-out

---

### Known Issues

- **GitHub SSH**: SSH key not configured for github.com (`Permission denied (publickey)`). HTTPS push works fine (used that instead). If SSH is needed: `ssh-keygen -t ed25519 -C "lorenzo"` then add key to GitHub settings.
- **Triple message bug**: Fixed via AGENTS.md — all agents now explicitly prohibited from calling `message` tool.

---

### Testing Results

| Test | Result |
|---|---|
| `hospitable.py 2026-02-19` | ✅ 2 check-ins (Tommy Dielen @Milano, Home Exchange @Giacinto) |
| `hospitable.py 2026-02-17 2026-02-23` | ✅ 8 reservations across 4 properties |
| `hospitable.py --reviews` | ✅ 4 properties, reviews with needs-response flags |
| `switch_agent.sh massimo` | ✅ Switching confirmed |
| `switch_agent.sh main` | ✅ Switching confirmed |
| AGENTS.md propagation | ✅ All 4 workspaces updated |
| Git push | ✅ Pushed to origin/main (15b7620..8c80493) |
