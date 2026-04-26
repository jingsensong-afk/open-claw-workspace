#!/usr/bin/env bash
set -euo pipefail
TEXT_FILE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/distribution_layer/telegram_distribution_text_v1.txt"
if [ ! -f "$TEXT_FILE" ]; then
  echo "telegram distribution text missing" >&2
  exit 1
fi
cat "$TEXT_FILE"
