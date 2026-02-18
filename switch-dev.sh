#!/bin/bash
openclaw config set agents.defaults.model.primary "openrouter/anthropic/claude-opus-4.6"
openclaw gateway restart
echo "Switched to Claude Opus for Dev"
