#!/bin/bash
openclaw config set agents.defaults.model.primary "openrouter/anthropic/claude-haiku-4.5"
openclaw gateway restart
echo "Switched to Claude Haiku for Dev"
