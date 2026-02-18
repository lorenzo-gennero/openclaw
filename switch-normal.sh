#!/bin/bash
openclaw config set agents.defaults.model.primary "openrouter/openai/gpt-4o-mini"
openclaw gateway restart
echo "Switched to gpt-4o-mini"
