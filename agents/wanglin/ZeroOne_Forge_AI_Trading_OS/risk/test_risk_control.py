"""
risk_control.py 的 smoke test。覆盖 Codex Step 2 spec 要求的 8 个最低场景，
另加边界 / 异常 / 多重违规场景共 17 个。

【运行】
    .venv/bin/python -m risk.test_risk_control
（从 ZeroOne_Forge_AI_Trading_OS/ 目录下跑）

或：
    .venv/bin/python agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/test_risk_control.py
（从仓库根跑）

【退出码】
0 = 全过；1 = 至少一个失败
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

# 让脚本既能 `python -m risk.test_risk_control` 跑，也能 `python risk/test_risk_control.py` 跑
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from risk.risk_control import (
    AccountState,
    ProposedOrder,
    RiskConfigError,
    RiskDecision,
    RiskLimits,
    load_risk_limits,
    validate_order,
)


# ---------- 测试工具 ----------

class TestRunner:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[tuple[str, str]] = []

    def case(self, name: str, decision: RiskDecision, expect_approved: bool,
             expect_reason_contains: str | None = None) -> None:
        ok = decision.approved == expect_approved
        if ok and expect_reason_contains is not None:
            ok = any(expect_reason_contains in r for r in decision.reasons)
        if ok:
            self.passed += 1
            mark = "✅"
            detail = "approved" if decision.approved else f"rejected: {decision.reasons[0] if decision.reasons else ''}"
            print(f"  {mark} {name} · {detail}")
        else:
            actual = "approved" if decision.approved else f"rejected({decision.reasons})"
            self.failed.append((name, actual))
            print(f"  ❌ {name} · 预期 approved={expect_approved}, 实际 {actual}")


# ---------- 标准固件（每个 case 在此基础上微调）----------

# 总权益 100,000 USDT，1% 风险预算 = 1,000 USDT
STD_ACCOUNT = AccountState(
    total_equity=Decimal("100000"),
    available_balance=Decimal("100000"),
    daily_realized_pnl=Decimal("0"),
    open_positions_count=0,
)

STD_LIMITS = RiskLimits(
    max_leverage_cap=Decimal("5"),
    risk_per_trade_pct=Decimal("0.01"),
    daily_loss_halt_pct=Decimal("0.03"),
)

# 标准订单：BTC 多单 60000 入场 / 59400 止损（距离 1% = 600 USDT/coin）
# 数量 1 BTC → 总风险 600 USDT = 0.6% 总权益（预算内）
def std_order(**overrides) -> ProposedOrder:
    base = dict(
        symbol="BTC/USDT:USDT",
        side="long",
        entry_price=Decimal("60000"),
        stop_loss_price=Decimal("59400"),
        quantity=Decimal("1"),
        leverage=Decimal("3"),
    )
    base.update(overrides)
    return ProposedOrder(**base)


# ---------- 主测试 ----------

def test_validate_order(t: TestRunner) -> None:
    print("\n[A] validate_order · Codex 要求的 8 个最低场景")
    print("-" * 64)

    # 场景 1：0.5% 单笔风险 → 通过
    # 数量 0.83 BTC × 600 USDT 距离 ≈ 498 USDT = 0.498% 总权益 < 1%
    o = std_order(quantity=Decimal("0.83"))
    t.case("0.5% 单笔风险 · 通过", validate_order(o, STD_ACCOUNT, STD_LIMITS), True)

    # 场景 2：1.5% 单笔风险 → 拒绝
    # 数量 2.5 BTC × 600 USDT = 1500 USDT = 1.5% > 1%
    o = std_order(quantity=Decimal("2.5"))
    t.case("1.5% 单笔风险 · 拒绝", validate_order(o, STD_ACCOUNT, STD_LIMITS),
           False, "单笔风险")

    # 场景 3：5x 杠杆（边界）→ 通过
    o = std_order(leverage=Decimal("5"))
    t.case("5x 杠杆（边界）· 通过", validate_order(o, STD_ACCOUNT, STD_LIMITS), True)

    # 场景 4：6x 杠杆 → 拒绝
    o = std_order(leverage=Decimal("6"))
    t.case("6x 杠杆 · 拒绝", validate_order(o, STD_ACCOUNT, STD_LIMITS),
           False, "leverage")

    # 场景 5：日亏损 2% → 通过
    acc = AccountState(
        total_equity=Decimal("100000"),
        available_balance=Decimal("98000"),
        daily_realized_pnl=Decimal("-2000"),  # -2%
        open_positions_count=0,
    )
    t.case("日亏损 2% · 通过", validate_order(std_order(), acc, STD_LIMITS), True)

    # 场景 6：日亏损 3%（边界）→ 拒绝
    acc = AccountState(
        total_equity=Decimal("100000"),
        available_balance=Decimal("97000"),
        daily_realized_pnl=Decimal("-3000"),  # -3%
        open_positions_count=0,
    )
    t.case("日亏损 3%（边界）· 拒绝", validate_order(std_order(), acc, STD_LIMITS),
           False, "熔断")

    # 场景 7：无止损 → 拒绝
    o = std_order(stop_loss_price=None)
    t.case("无止损 · 拒绝", validate_order(o, STD_ACCOUNT, STD_LIMITS),
           False, "stop_loss_price")

    # 场景 8：非 BTC/ETH pair → 拒绝
    o = std_order(symbol="DOGE/USDT:USDT")
    t.case("非白名单标的 DOGE · 拒绝", validate_order(o, STD_ACCOUNT, STD_LIMITS),
           False, "白名单")


def test_validate_order_extra(t: TestRunner) -> None:
    print("\n[B] validate_order · 边界 / 异常 / 多重违规")
    print("-" * 64)

    # 9. 标准订单，全部 OK
    t.case("标准 BTC 多单（一切合规）",
           validate_order(std_order(), STD_ACCOUNT, STD_LIMITS), True)

    # 10. 标准 ETH 订单
    o = std_order(symbol="ETH/USDT:USDT", entry_price=Decimal("3000"),
                  stop_loss_price=Decimal("2970"))  # 距离 1%
    t.case("标准 ETH 多单 · 通过",
           validate_order(o, STD_ACCOUNT, STD_LIMITS), True)

    # 11. side="short" 且止损正确（高于入场）
    o = std_order(side="short", stop_loss_price=Decimal("60600"))  # 60000 + 1%
    t.case("BTC 空单 + 止损在入场上方 · 通过",
           validate_order(o, STD_ACCOUNT, STD_LIMITS), True)

    # 12. side="long" 但止损在入场上方（方向错误）
    o = std_order(stop_loss_price=Decimal("60500"))  # 高于入场
    t.case("多单止损在入场上方 · 拒绝",
           validate_order(o, STD_ACCOUNT, STD_LIMITS), False, "方向错误")

    # 13. side 非法
    o = std_order(side="HOLD")
    t.case("side='HOLD' · 拒绝",
           validate_order(o, STD_ACCOUNT, STD_LIMITS), False, "side")

    # 14. 杠杆为 0
    o = std_order(leverage=Decimal("0"))
    t.case("leverage=0 · 拒绝",
           validate_order(o, STD_ACCOUNT, STD_LIMITS), False, "leverage")

    # 15. quantity 为负
    o = std_order(quantity=Decimal("-1"))
    t.case("quantity=-1 · 拒绝",
           validate_order(o, STD_ACCOUNT, STD_LIMITS), False, "quantity")

    # 16. 多重违规：6x 杠杆 + 1.5% 风险 + 非白名单
    o = std_order(symbol="DOGE/USDT:USDT", leverage=Decimal("8"),
                  quantity=Decimal("3"))
    decision = validate_order(o, STD_ACCOUNT, STD_LIMITS)
    multi_ok = (
        not decision.approved
        and len(decision.reasons) >= 3
        and any("白名单" in r for r in decision.reasons)
        and any("leverage" in r for r in decision.reasons)
        and any("单笔风险" in r for r in decision.reasons)
    )
    if multi_ok:
        t.passed += 1
        print(f"  ✅ 多重违规一次性返回所有原因 · {len(decision.reasons)} 条原因")
    else:
        t.failed.append(("多重违规", str(decision)))
        print(f"  ❌ 多重违规一次性返回所有原因 · 实际 {decision}")

    # 17. 总权益为 0（异常状态）
    bad_acc = AccountState(
        total_equity=Decimal("0"),
        available_balance=Decimal("0"),
        daily_realized_pnl=Decimal("0"),
    )
    t.case("总权益=0 的账户 · 拒绝",
           validate_order(std_order(), bad_acc, STD_LIMITS),
           False, "total_equity")


def test_load_risk_limits(t: TestRunner) -> None:
    print("\n[C] load_risk_limits · config 加载 + 硬上限校验")
    print("-" * 64)

    import json
    import tempfile

    def write_tmp(content: dict) -> Path:
        p = Path(tempfile.mkstemp(suffix=".json")[1])
        p.write_text(json.dumps(content))
        return p

    # 18. 正常 config
    p = write_tmp({"max_leverage_cap": 5, "risk_per_trade_pct": 0.01,
                   "daily_loss_halt_pct": 0.03})
    try:
        limits = load_risk_limits(p)
        ok = limits.max_leverage_cap == Decimal("5") and limits.risk_per_trade_pct == Decimal("0.01")
        if ok:
            t.passed += 1
            print(f"  ✅ 合法 config 加载 · {limits}")
        else:
            t.failed.append(("合法 config", str(limits)))
    finally:
        p.unlink()

    # 19. 缺字段 → 抛异常
    p = write_tmp({"max_leverage_cap": 5})  # 缺两项
    try:
        try:
            load_risk_limits(p)
            t.failed.append(("缺字段", "未抛异常"))
            print(f"  ❌ 缺字段应抛 RiskConfigError，实际未抛")
        except RiskConfigError as e:
            if "缺少必需字段" in str(e):
                t.passed += 1
                print(f"  ✅ 缺字段 · 抛 RiskConfigError")
            else:
                t.failed.append(("缺字段消息", str(e)))
    finally:
        p.unlink()

    # 20. 杠杆超绝对硬上限（10 > 5）→ 抛异常
    p = write_tmp({"max_leverage_cap": 10, "risk_per_trade_pct": 0.01,
                   "daily_loss_halt_pct": 0.03})
    try:
        try:
            load_risk_limits(p)
            t.failed.append(("杠杆超硬上限", "未抛异常"))
            print(f"  ❌ 杠杆 10 应抛 RiskConfigError，实际未抛")
        except RiskConfigError as e:
            if "max_leverage_cap" in str(e):
                t.passed += 1
                print(f"  ✅ 杠杆 10 超硬上限 · 抛 RiskConfigError")
            else:
                t.failed.append(("杠杆消息", str(e)))
    finally:
        p.unlink()

    # 21. 单笔风险超绝对硬上限（5% > 1%）→ 抛异常
    p = write_tmp({"max_leverage_cap": 5, "risk_per_trade_pct": 0.05,
                   "daily_loss_halt_pct": 0.03})
    try:
        try:
            load_risk_limits(p)
            t.failed.append(("风险超硬上限", "未抛异常"))
        except RiskConfigError as e:
            if "risk_per_trade_pct" in str(e):
                t.passed += 1
                print(f"  ✅ 单笔风险 5% 超硬上限 · 抛 RiskConfigError")
    finally:
        p.unlink()

    # 22. 文件不存在 → 抛异常
    nonexistent = Path("/tmp/__not_exists__.json")
    try:
        load_risk_limits(nonexistent)
        t.failed.append(("文件不存在", "未抛异常"))
    except RiskConfigError as e:
        if "不存在" in str(e):
            t.passed += 1
            print(f"  ✅ 文件不存在 · 抛 RiskConfigError")


def main() -> int:
    print("=" * 64)
    print("risk_control · smoke test")
    print("=" * 64)

    t = TestRunner()
    test_validate_order(t)
    test_validate_order_extra(t)
    test_load_risk_limits(t)

    print("\n" + "=" * 64)
    if not t.failed:
        print(f"✅ 全部 {t.passed} 个测试通过")
        return 0
    else:
        print(f"❌ {len(t.failed)} 失败 / {t.passed} 通过")
        for name, actual in t.failed:
            print(f"   - {name}: {actual}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
