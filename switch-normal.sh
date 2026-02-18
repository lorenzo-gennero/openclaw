#!/bin/bash
openclaw config set agents.defaults.model.primary "openrouter/google/gemini-3-flash-preview"
openclaw gateway restart
echo "Switched to Gemini Flash"
