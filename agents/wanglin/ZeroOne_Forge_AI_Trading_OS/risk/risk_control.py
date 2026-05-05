"""
ZeroOne Forge · 风控 Gate（Step 2）

【职责】
所有"产生订单意图"的代码（策略文件、手动下单脚本、未来的 cron 复核器等）
在真实下单**之前**必须把订单意图传给 validate_order()，gate 通过才能下单。

【设计原则（来自 Codex Step 2 spec）】
- config 是 single source of truth：load_risk_limits() 从 freqtrade_main_dryrun.json 读
  max_leverage_cap / risk_per_trade_pct / daily_loss_halt_pct，不在代码里另写默认值
- 缺字段 / 字段超过绝对硬上限 → fail closed（raise RiskConfigError，不静默继续）
- 订单违反任意规则 → fail closed（返回 approved=False，附明确拒绝原因）
- 多个违规同时返回，不是只报第一个
- 接口纯数据，无副作用：不打日志、不发请求、不读外部 state

【绝对硬上限】（无论 config 写什么都不能超过）
- 杠杆 ≤ 5
- 单笔风险 ≤ 1%
- 日内熔断 ≤ 3%
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path


# ---------- 绝对硬上限（防御深度，preflight 已在 config 层校验，这里再守一道）----------

ABSOLUTE_MAX_LEVERAGE = Decimal("5")
ABSOLUTE_MAX_RISK_PER_TRADE = Decimal("0.01")    # 1%
ABSOLUTE_MAX_DAILY_LOSS_HALT = Decimal("0.03")   # 3%
ABSOLUTE_MAX_OPEN_TRADES = 5                      # 单账户同时持仓数硬上限

# v1 默认允许的标的白名单（与 config.exchange.pair_whitelist 对应；
# 后续若需要差异化，可改成从 config 读取）
DEFAULT_ALLOWED_PAIRS: frozenset[str] = frozenset({"BTC/USDT:USDT", "ETH/USDT:USDT"})


# ---------- 异常 ----------

class RiskConfigError(Exception):
    """风控配置加载或合法性校验失败时抛出。"""


# ---------- 数据结构 ----------

@dataclass(frozen=True)
class RiskLimits:
    """从 config 加载并经过硬上限校验的风控参数。"""
    max_leverage_cap: Decimal
    risk_per_trade_pct: Decimal
    daily_loss_halt_pct: Decimal
    max_open_trades: int


@dataclass(frozen=True)
class ProposedOrder:
    """策略 / 复核器产出的订单意图。

    side: "long" 或 "short"
    entry_price: 计划入场价
    stop_loss_price: 止损价。**None 视为无止损 → 直接拒绝**
    quantity: 数量（标的单位）
    leverage: 计划使用的杠杆倍数
    """
    symbol: str
    side: str
    entry_price: Decimal
    stop_loss_price: Decimal | None
    quantity: Decimal
    leverage: Decimal


@dataclass(frozen=True)
class OpenPosition:
    """一个当前持仓的最小描述（用于 gate 检查"是否已有同向同币种持仓"）。"""
    symbol: str
    side: str  # "long" 或 "short"


@dataclass(frozen=True)
class AccountState:
    """下单瞬间的账户快照。

    total_equity: 总权益（用于计算单笔风险百分比 + 日亏损百分比）
    available_balance: 可用保证金
    daily_realized_pnl: 当日已实现盈亏（负数表示亏损）
    open_positions: 当前持仓的元组（gate 用来检查反向 / 同向 / 数量上限）
    """
    total_equity: Decimal
    available_balance: Decimal
    daily_realized_pnl: Decimal
    open_positions: tuple[OpenPosition, ...] = ()

    @property
    def open_positions_count(self) -> int:
        return len(self.open_positions)


@dataclass(frozen=True)
class RiskDecision:
    """gate 审批结果。多个违规同时返回，方便策略一次性看到全部原因。"""
    approved: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)


# ---------- 配置加载 ----------

def load_risk_limits(config_path: Path) -> RiskLimits:
    """从 freqtrade_main_dryrun.json 读取风控上限，并校验绝对硬上限。

    fail closed 的场景：
    - 文件不存在 / JSON 不合法 / 缺字段 → RiskConfigError
    - 字段不是数值 / 非正数 / 超过绝对硬上限 → RiskConfigError
    """
    if not config_path.exists():
        raise RiskConfigError(f"风控配置文件不存在：{config_path}")

    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        raise RiskConfigError(f"风控配置 JSON 解析失败 ({config_path}): {e}")

    required = ("max_leverage_cap", "risk_per_trade_pct", "daily_loss_halt_pct",
                "max_open_trades")
    missing = [k for k in required if k not in config]
    if missing:
        raise RiskConfigError(f"风控配置缺少必需字段：{missing}")

    # 转 Decimal（接收 int / float / 数字字符串都允许）
    try:
        leverage_cap = Decimal(str(config["max_leverage_cap"]))
        risk_per_trade = Decimal(str(config["risk_per_trade_pct"]))
        daily_loss = Decimal(str(config["daily_loss_halt_pct"]))
        max_open = int(config["max_open_trades"])
    except Exception as e:
        raise RiskConfigError(f"风控字段类型转换失败：{e}")

    # 绝对硬上限校验（防御深度）
    if leverage_cap <= 0 or leverage_cap > ABSOLUTE_MAX_LEVERAGE:
        raise RiskConfigError(
            f"max_leverage_cap {leverage_cap} 必须在 (0, {ABSOLUTE_MAX_LEVERAGE}]"
        )
    if risk_per_trade <= 0 or risk_per_trade > ABSOLUTE_MAX_RISK_PER_TRADE:
        raise RiskConfigError(
            f"risk_per_trade_pct {risk_per_trade} 必须在 (0, {ABSOLUTE_MAX_RISK_PER_TRADE}]"
        )
    if daily_loss <= 0 or daily_loss > ABSOLUTE_MAX_DAILY_LOSS_HALT:
        raise RiskConfigError(
            f"daily_loss_halt_pct {daily_loss} 必须在 (0, {ABSOLUTE_MAX_DAILY_LOSS_HALT}]"
        )
    if max_open <= 0 or max_open > ABSOLUTE_MAX_OPEN_TRADES:
        raise RiskConfigError(
            f"max_open_trades {max_open} 必须在 [1, {ABSOLUTE_MAX_OPEN_TRADES}]"
        )

    return RiskLimits(
        max_leverage_cap=leverage_cap,
        risk_per_trade_pct=risk_per_trade,
        daily_loss_halt_pct=daily_loss,
        max_open_trades=max_open,
    )


# ---------- 核心 gate ----------

def validate_order(
    order: ProposedOrder,
    account: AccountState,
    limits: RiskLimits,
    allowed_pairs: frozenset[str] = DEFAULT_ALLOWED_PAIRS,
) -> RiskDecision:
    """对一笔订单意图执行所有风控检查。

    返回 RiskDecision(approved=True, reasons=()) 表示通过；
    返回 RiskDecision(approved=False, reasons=(...)) 含全部失败原因。

    检查项：
    1. 标的必须在白名单
    2. side 必须是 "long" / "short"
    3. 必须带止损价
    4. 止损价相对入场价方向必须正确
    5. 数量、入场价、杠杆必须为正
    6. 杠杆 ≤ limits.max_leverage_cap
    7. 单笔风险 (止损距离 × 数量) / 总权益 ≤ limits.risk_per_trade_pct
    8. 日内已实现亏损绝对值 / 总权益 < limits.daily_loss_halt_pct
       （等于阈值即触发熔断，拒绝新开仓）
    9. 同一 symbol 已有任意 side 持仓 → 拒绝（v1 不允许加仓 / 不允许对冲反向）
    10. 当前持仓数 ≥ limits.max_open_trades → 拒绝
    """
    failures: list[str] = []

    # 1. 标的白名单
    if order.symbol not in allowed_pairs:
        failures.append(
            f"symbol '{order.symbol}' 不在白名单 {sorted(allowed_pairs)}"
        )

    # 2. side 合法性
    if order.side not in ("long", "short"):
        failures.append(f"side 必须是 'long' 或 'short'，收到 {order.side!r}")

    # 3. 必带止损
    if order.stop_loss_price is None:
        failures.append("缺少 stop_loss_price（必带止损）")

    # 4. 数量 / 入场价 / 杠杆 正数校验
    if order.quantity <= 0:
        failures.append(f"quantity 必须为正，收到 {order.quantity}")
    if order.entry_price <= 0:
        failures.append(f"entry_price 必须为正，收到 {order.entry_price}")
    if order.leverage <= 0:
        failures.append(f"leverage 必须为正，收到 {order.leverage}")

    # 5. 杠杆上限
    if order.leverage > limits.max_leverage_cap:
        failures.append(
            f"leverage {order.leverage} 超过上限 {limits.max_leverage_cap}"
        )

    # 6. 止损方向 + 单笔风险（仅在 1-4 没问题时才计算，避免被坏数据干扰）
    can_compute_risk = (
        order.stop_loss_price is not None
        and order.side in ("long", "short")
        and order.quantity > 0
        and order.entry_price > 0
    )
    if can_compute_risk:
        # 止损方向：long 的止损必须低于入场，short 的止损必须高于入场
        if order.side == "long":
            risk_per_unit = order.entry_price - order.stop_loss_price
        else:
            risk_per_unit = order.stop_loss_price - order.entry_price

        if risk_per_unit <= 0:
            failures.append(
                f"stop_loss_price {order.stop_loss_price} 相对 {order.side} "
                f"的 entry_price {order.entry_price} 方向错误"
            )
        else:
            # 7. 单笔风险百分比
            total_risk = risk_per_unit * order.quantity
            if account.total_equity <= 0:
                failures.append(
                    f"account.total_equity {account.total_equity} 必须为正才能计算风险占比"
                )
            else:
                risk_pct = total_risk / account.total_equity
                if risk_pct > limits.risk_per_trade_pct:
                    failures.append(
                        f"单笔风险 {risk_pct:.6f} 超过上限 {limits.risk_per_trade_pct}"
                    )

    # 8. 日内熔断
    if account.total_equity > 0 and account.daily_realized_pnl < 0:
        loss_pct = abs(account.daily_realized_pnl) / account.total_equity
        if loss_pct >= limits.daily_loss_halt_pct:
            failures.append(
                f"日内已实现亏损 {loss_pct:.6f} 触及熔断阈值 "
                f"{limits.daily_loss_halt_pct}，拒绝新开仓"
            )

    # 9. 同 symbol 已有任意 side 持仓 → 拒绝（v1 不允许加仓 / 不允许同币种同时持仓对冲）
    for pos in account.open_positions:
        if pos.symbol == order.symbol:
            failures.append(
                f"已有 {order.symbol} {pos.side} 持仓，v1 不允许同 symbol 再开仓（无论方向）"
            )
            break

    # 10. 当前持仓数 ≥ max_open_trades → 拒绝
    if account.open_positions_count >= limits.max_open_trades:
        failures.append(
            f"当前持仓数 {account.open_positions_count} 已达上限 "
            f"{limits.max_open_trades}，拒绝新开仓"
        )

    if failures:
        return RiskDecision(approved=False, reasons=tuple(failures))
    return RiskDecision(approved=True, reasons=())
