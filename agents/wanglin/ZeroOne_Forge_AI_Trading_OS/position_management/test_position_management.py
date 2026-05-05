"""
position_management smoke test。覆盖 daily_pnl 与 position_state 的正常路径 +
fail closed 边界。

【运行】
    .venv/bin/python agents/wanglin/ZeroOne_Forge_AI_Trading_OS/position_management/test_position_management.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

# 让脚本独立可跑
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from position_management.daily_pnl import (  # noqa: E402
    TradeRecord,
    aggregate_daily_realized_pnl,
)
from position_management.position_state import extract_open_positions  # noqa: E402


# ---------- 工具 ----------

class TestRunner:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[tuple[str, str]] = []

    def case(self, name: str, actual, expected) -> None:
        if actual == expected:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed.append((name, f"expected={expected} actual={actual}"))
            print(f"  ❌ {name} · expected={expected} actual={actual}")


@dataclass
class FakeTrade:
    """模拟 Freqtrade Trade 对象（只需要测试用到的字段）。"""
    pair: str
    is_open: bool = False
    is_short: bool = False
    close_date: datetime | None = None
    close_profit_abs: Decimal | None = None


# ---------- daily_pnl ----------

def test_daily_pnl(t: TestRunner) -> None:
    print("\n[A] aggregate_daily_realized_pnl")
    print("-" * 64)

    now = datetime(2026, 5, 5, 14, 0, 0, tzinfo=timezone.utc)
    today_morning = now.replace(hour=9, minute=0, second=0)
    yesterday = now - timedelta(days=1)

    # 1. 空列表 → 0
    t.case("空交易列表", aggregate_daily_realized_pnl([], now=now), Decimal("0"))

    # 2. 仅未平仓订单 → 0
    open_trades = [FakeTrade(pair="BTC/USDT:USDT", is_open=True)]
    t.case("仅未平仓订单", aggregate_daily_realized_pnl(open_trades, now=now), Decimal("0"))

    # 3. 今天平仓 +120 + 今天平仓 -50 → +70
    today_closed = [
        FakeTrade(pair="BTC/USDT:USDT", is_open=False, close_date=today_morning,
                  close_profit_abs=Decimal("120")),
        FakeTrade(pair="ETH/USDT:USDT", is_open=False, close_date=today_morning,
                  close_profit_abs=Decimal("-50")),
    ]
    t.case("今天 +120 + 今天 -50",
           aggregate_daily_realized_pnl(today_closed, now=now), Decimal("70"))

    # 4. 昨天平仓 → 不算入今天
    mixed = [
        FakeTrade(pair="BTC/USDT:USDT", is_open=False, close_date=yesterday,
                  close_profit_abs=Decimal("999")),
        FakeTrade(pair="BTC/USDT:USDT", is_open=False, close_date=today_morning,
                  close_profit_abs=Decimal("100")),
    ]
    t.case("昨天 +999 不计入今天",
           aggregate_daily_realized_pnl(mixed, now=now), Decimal("100"))

    # 5. close_date 为 None → 跳过
    bad = [FakeTrade(pair="BTC/USDT:USDT", is_open=False, close_date=None,
                     close_profit_abs=Decimal("100"))]
    t.case("close_date=None 跳过", aggregate_daily_realized_pnl(bad, now=now), Decimal("0"))

    # 6. close_profit_abs 为 None → 跳过
    bad = [FakeTrade(pair="BTC/USDT:USDT", is_open=False, close_date=today_morning,
                     close_profit_abs=None)]
    t.case("close_profit_abs=None 跳过",
           aggregate_daily_realized_pnl(bad, now=now), Decimal("0"))

    # 7. close_date 在未来（异常时间戳）→ 跳过
    future = now + timedelta(hours=1)
    bad = [FakeTrade(pair="BTC/USDT:USDT", is_open=False, close_date=future,
                     close_profit_abs=Decimal("100"))]
    t.case("未来时间戳跳过", aggregate_daily_realized_pnl(bad, now=now), Decimal("0"))

    # 8. now 没 tzinfo → 当 UTC 处理
    naive_now = datetime(2026, 5, 5, 14, 0, 0)
    t.case("naive now 当 UTC",
           aggregate_daily_realized_pnl(today_closed, now=naive_now), Decimal("70"))


# ---------- position_state ----------

def test_position_state(t: TestRunner) -> None:
    print("\n[B] extract_open_positions")
    print("-" * 64)

    # 9. 空列表 → 空 tuple
    t.case("空交易列表", extract_open_positions([]), ())

    # 10. 全部已平仓 → 空 tuple
    closed_only = [FakeTrade(pair="BTC/USDT:USDT", is_open=False)]
    t.case("全部已平仓", extract_open_positions(closed_only), ())

    # 11. 一笔 long 持仓
    one_long = [FakeTrade(pair="BTC/USDT:USDT", is_open=True, is_short=False)]
    from risk import OpenPosition
    t.case("一笔 BTC long", extract_open_positions(one_long),
           (OpenPosition(symbol="BTC/USDT:USDT", side="long"),))

    # 12. 一笔 short 持仓
    one_short = [FakeTrade(pair="ETH/USDT:USDT", is_open=True, is_short=True)]
    t.case("一笔 ETH short", extract_open_positions(one_short),
           (OpenPosition(symbol="ETH/USDT:USDT", side="short"),))

    # 13. 混合：1 BTC long + 1 ETH short + 1 closed → 只返回前两个
    mixed = [
        FakeTrade(pair="BTC/USDT:USDT", is_open=True, is_short=False),
        FakeTrade(pair="ETH/USDT:USDT", is_open=True, is_short=True),
        FakeTrade(pair="DOGE/USDT:USDT", is_open=False, is_short=False),
    ]
    expected = (
        OpenPosition(symbol="BTC/USDT:USDT", side="long"),
        OpenPosition(symbol="ETH/USDT:USDT", side="short"),
    )
    t.case("BTC long + ETH short + 1 已平仓", extract_open_positions(mixed), expected)

    # 14. pair 字段缺失 → 跳过（fail closed）
    @dataclass
    class BrokenTrade:
        is_open: bool = True
        is_short: bool = False
        # 缺 pair
    broken = [BrokenTrade()]
    t.case("缺 pair 字段跳过", extract_open_positions(broken), ())


def main() -> int:
    print("=" * 64)
    print("position_management · smoke test")
    print("=" * 64)
    t = TestRunner()
    test_daily_pnl(t)
    test_position_state(t)
    print("\n" + "=" * 64)
    if not t.failed:
        print(f"✅ 全部 {t.passed} 个测试通过")
        return 0
    else:
        print(f"❌ {len(t.failed)} 失败 / {t.passed} 通过")
        for name, msg in t.failed:
            print(f"   - {name}: {msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
