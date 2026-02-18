#!/bin/bash
cd ~/.openclaw
git add .
git commit -m "Auto backup $(date '+%Y-%m-%d %H:%M')" --allow-empty
git push origin main
