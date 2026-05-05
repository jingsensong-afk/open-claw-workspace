"""ZeroOne Forge · 持仓管理（Step 4）

把策略需要的"账户状态聚合"职责从 strategy 中抽出来，让 risk gate 拿到真实而非
degraded 的 AccountState。两个核心子模块：

- daily_pnl     聚合当日已平仓订单的实现盈亏 → 喂给 daily_realized_pnl
- position_state  从 Freqtrade Trade 列表抽取最小 OpenPosition，喂给 risk gate

【硬约束（Codex Step 4 spec）】
- 失败时 fail closed（异常上抛或返回保守值）
- 不引入真实交易、外部分发或新增 key
- 不削弱 risk gate 已有 8 条规则
- 时区统一（默认 UTC）
"""

from .daily_pnl import (
    TradeRecord,
    aggregate_daily_realized_pnl,
)
from .position_state import (
    extract_open_positions,
)

__all__ = [
    "TradeRecord",
    "aggregate_daily_realized_pnl",
    "extract_open_positions",
]
