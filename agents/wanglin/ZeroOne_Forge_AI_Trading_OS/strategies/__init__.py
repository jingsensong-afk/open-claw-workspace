"""ZeroOne Forge · 策略包

每个策略文件实现一个 IStrategy 子类，由 Freqtrade 通过 strategy_path 加载。

【硬约束（Codex Step 3 spec）】
- 任何下单前必须显式 import + 调用 risk.validate_order()，gate 通过才允许
- 策略不得自己判断"这笔订单可不可以"，最终决定权在 risk_control gate
- v1 仅 BTC/ETH，仅多头
- Donchian 突破信号必须用 .shift(1) 防 lookahead 偏差
"""
