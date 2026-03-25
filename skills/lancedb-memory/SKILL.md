# lancedb-memory

LanceDB-backed long-term memory utilities (Python).

## Installed Version
- 1.0.0
- Source: clawhub (fallback from skillhub search)

## What was hardened
- Replaced hardcoded macOS path `/Users/prerak/clawd/memory/lancedb` with `/root/.openclaw/memory/lancedb`
- Replaced hardcoded `sys.path.append('/Users/prerak/...')` with relative path resolution
- Installed runtime dependency: `lancedb` (Python)

## Runtime prerequisites
- Python 3.12+
- pip
- `lancedb` package

## Notes
- This skill is third-party and not OpenClaw built-in.
- Keep it pinned to 1.0.0 unless we review newer versions first.
- Current environment runs CPU-only for QMD/LanceDB workflows (no GPU acceleration configured).
