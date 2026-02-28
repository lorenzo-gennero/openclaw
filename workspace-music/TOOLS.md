# TOOLS.md - Local Notes

## Josh Knowledge Base CLI

All commands run from `/Users/lorenzogennero/openclaw-agents/`:

```bash
# Semantic search + Claude synthesis (for complex multi-tutorial questions)
python3 -m agents.josh.main query "question here"

# Structured session plan (drums → bass → harmony → FX → arrangement)
python3 -m agents.josh.main session "style or goal here"

# Regenerate discovery pages (hidden gems, learning paths, weekly challenge)
python3 -m agents.josh.main discover

# Regenerate reference pages (plugins index, artist profiles, technique deepdives)
python3 -m agents.josh.main references

# Technique tag analytics and coverage gaps
python3 -m agents.josh.main heatmap
```

## Vault Location

**Absolute path:** `/Users/lorenzogennero/Library/Mobile Documents/iCloud~md~obsidian/Documents/JoshBrain/Josh-Brain/`
**Workspace symlink:** `Josh-Brain/` (use the read tool to read files directly — no shell commands needed)

## TTS

- Use warm, concise tone for voice responses
- Keep TTS under 30 words — technical details go in text
