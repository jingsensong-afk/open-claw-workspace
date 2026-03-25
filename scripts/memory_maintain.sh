#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-health}"
WS="/root/.openclaw/workspace"
LANCE_PY="$WS/skills/lancedb-memory/lancedb_memory.py"

qmd_health() {
  echo "[QMD] status"
  qmd status >/dev/null
  echo "[QMD] ok"
}

qmd_refresh() {
  echo "[QMD] update"
  qmd update
  echo "[QMD] embed"
  qmd embed
  echo "[QMD] refresh done"
}

lance_health() {
  echo "[LanceDB] import + recent"
  python3 - <<'PY'
import importlib.util, asyncio
p='/root/.openclaw/workspace/skills/lancedb-memory/lancedb_memory.py'
spec=importlib.util.spec_from_file_location('lm',p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
async def t():
    r=await m.lance_memory_provider.get_recent(1)
    print('recent_count',len(r))
asyncio.run(t())
PY
  echo "[LanceDB] ok"
}

lance_write_test() {
  python3 - <<'PY'
import importlib.util, asyncio, datetime
p='/root/.openclaw/workspace/skills/lancedb-memory/lancedb_memory.py'
spec=importlib.util.spec_from_file_location('lm',p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
async def t():
    i=await m.lance_memory_provider.add(f'healthcheck {datetime.datetime.now().isoformat()}', {'type':'healthcheck'})
    print('write_id',i)
asyncio.run(t())
PY
}

case "$CMD" in
  health)
    qmd_health
    lance_health
    ;;
  refresh)
    qmd_refresh
    ;;
  full)
    qmd_health
    qmd_refresh
    lance_health
    lance_write_test
    ;;
  *)
    echo "Usage: $0 {health|refresh|full}"
    exit 1
    ;;
esac
