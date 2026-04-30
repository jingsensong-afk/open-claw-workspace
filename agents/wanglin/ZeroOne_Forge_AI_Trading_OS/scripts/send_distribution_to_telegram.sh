#!/usr/bin/env bash
set -euo pipefail
SUMMARY_FILE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/distribution_layer/distribution_summary_v2.json"
if [ ! -f "$SUMMARY_FILE" ]; then
  echo "distribution summary v2 missing" >&2
  exit 1
fi
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/distribution_layer/distribution_summary_v2.json')
data=json.loads(p.read_text())
print('【ZeroOne Forge AI交易OS】')
print(data.get('summary',''))
syms=data.get('symbols',[])
if syms:
    print('strategy: ' + ', '.join(syms))
PY
