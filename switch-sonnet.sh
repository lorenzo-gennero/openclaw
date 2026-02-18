#!/bin/bash
openclaw config set agents.defaults.model.primary "openrouter/anthropic/claude-sonnet-4.5"
openclaw gateway restart
echo "Switched to Claude Sonnet"
