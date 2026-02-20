#!/bin/bash
# Auto-backup tracked OpenClaw config files
# Only stages files already tracked by git (won't add new untracked files)
cd ~/.openclaw
git add -u
git diff --cached --quiet && echo "Nothing to commit." && exit 0
git commit -m "Auto backup $(date '+%Y-%m-%d %H:%M')"
git push origin main
