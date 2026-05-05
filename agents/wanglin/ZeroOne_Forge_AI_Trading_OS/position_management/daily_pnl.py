"""
当日已实现盈亏聚合（Step 4）

【职责】
给定一组交易记录，把今天（默认 UTC 0:00 起）已平仓的订单的 realized PnL
求和，作为 risk gate 的 `daily_realized_pnl` 输入。

【设计原则】
- 纯数据 + 纯计算，不调外部 API
- 接受任何符合 TradeRecord 字段约定的可迭代对象（duck typing 友好）
- 时区统一 UTC（与 Binance 服务器、Freqtrade 内部一致）
- 异常 / 未知字段 → fail closed（跳过该条交易）

【调用方】
- strategies/main_trend_strategy.py 在 confirm_trade_entry 中调用
- 未来 Step 5+ 的复盘脚本也可以复用
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, Optional


@dataclass(frozen=True)
class TradeRecord:
    """一条交易记录的最小描述。Freqtrade 的 Trade ORM 对象可通过 to_record() 转。"""
    pair: str
    is_open: bool
    close_date: Optional[datetime]      # 已平仓时刻（None = 未平仓）
    close_profit_abs: Optional[Decimal]  # 已实现盈亏（USDT 等 stake_currency 计价）


def aggregate_daily_realized_pnl(
    trades: Iterable[TradeRecord],
    now: Optional[datetime] = None,
) -> Decimal:
    """聚合"今天"（UTC 0:00 起到 now）已平仓订单的实现盈亏。

    返回 Decimal（USDT 等 stake currency 计价）。负数表示亏损。

    【fail closed 行为】
    - 仍开仓 (is_open=True) → 跳过
    - close_date 为 None → 跳过
    - close_profit_abs 为 None → 跳过
    - close_date 比"今天 0:00"早 → 跳过
    - close_date 在未来（now 之后）→ 跳过（防御异常时间戳）

    【时区】
    若 now 没有 tzinfo，按 UTC 处理。所有 trade.close_date 同样视为 UTC。
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total = Decimal("0")
    for t in trades:
        if t.is_open:
            continue
        if t.close_date is None:
            continue
        if t.close_profit_abs is None:
            continue

        cd = t.close_date if t.close_date.tzinfo else t.close_date.replace(tzinfo=timezone.utc)
        if cd < today_start:
            continue
        if cd > now:
            # 防御异常：close_date 不应该在未来
            continue

        try:
            total += Decimal(str(t.close_profit_abs))
        except Exception:
            # fail closed：无法转 Decimal 的条目跳过
            continue

    return total
