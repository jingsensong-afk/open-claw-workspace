"""ZeroOne Forge AI 交易 OS · 风控模块

本包是策略下单前的强制 gate，独立于具体策略，被所有"产生订单意图"的代码调用。
config 是 single source of truth，risk_control 不另写默认值；缺字段或超限直接 fail closed。

接口（详见 risk_control.py 文档字符串）：
- RiskLimits        风控上限的不可变结构
- ProposedOrder     策略产生的订单意图（待审批）
- AccountState      当前账户状态快照（用于日内熔断 / 风险预算计算）
- RiskDecision      gate 审批结果（approved + 失败原因列表）
- load_risk_limits  从 config JSON 读取上限
- validate_order    核心 gate 函数
"""

from .risk_control import (
    AccountState,
    OpenPosition,
    ProposedOrder,
    RiskConfigError,
    RiskDecision,
    RiskLimits,
    load_risk_limits,
    validate_order,
)

__all__ = [
    "AccountState",
    "OpenPosition",
    "ProposedOrder",
    "RiskConfigError",
    "RiskDecision",
    "RiskLimits",
    "load_risk_limits",
    "validate_order",
]
