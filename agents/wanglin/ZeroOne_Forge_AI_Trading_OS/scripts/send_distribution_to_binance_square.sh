#!/usr/bin/env bash
set -euo pipefail
KEY_FILE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/.binance_square_api_key"
TEXT_FILE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/distribution_layer/binance_square_distribution_draft_v1.txt"
OUT_FILE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/distribution_layer/binance_square_last_publish_result.json"
if [ ! -f "$KEY_FILE" ]; then
  echo "missing binance square api key" >&2
  exit 1
fi
if [ ! -f "$TEXT_FILE" ]; then
  echo "missing binance square text file" >&2
  exit 1
fi
KEY=$(cat "$KEY_FILE")
BODY=$(python3 - <<'PY2'
import json, pathlib
text=pathlib.Path("/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/distribution_layer/binance_square_distribution_draft_v1.txt").read_text()
print(json.dumps({"bodyTextOnly": text}, ensure_ascii=False))
PY2
)
curl -sS 'https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add'   -H "X-Square-OpenAPI-Key: $KEY"   -H 'Content-Type: application/json'   -H 'clienttype: binanceSkill'   --data "$BODY" > "$OUT_FILE"
cat "$OUT_FILE"
