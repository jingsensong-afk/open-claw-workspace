# Day 5 Codex Review · MainTrendStrategy v1

**类型**：codex_review（针对 pre_review 的动手前反馈）
**日期**：2026-05-05（计划日期）
**作者**：Codex
**审阅对象**：`2026-05-05_day5_main_trend_pre_review.md`
**结论**：有条件通过；先补安全门、数据边界、回测边界，再进入实现。

---

## 总结结论

MainTrendStrategy v1 的方向可以推进：先从 BTC/ETH 中频趋势策略切入，比直接做热点币、山寨币或自动实盘更稳，也符合王林 OS 第四层从“能下单”升级到“按策略判断后下单”的演进节奏。

但本轮不能直接按 pre_review 原案进入实现。必须先补三个硬前置：

1. **启动安全门**：dry-run / testnet / no external distribution 必须有机器可检查的 preflight，而不是只写在配置说明里。
2. **风控不可绕过**：风控模块必须独立，策略只生成意图，最终下单前必须经过 risk gate。
3. **回测样本扩展**：不能只测 2024-2025，必须覆盖 2022 熊市与 2024 牛市，避免趋势策略在单一行情里“看起来很好”。

---

## 高优先级意见

### 1. 必须新增 dry-run preflight，而不是只依赖 Freqtrade 配置

pre_review 写了 `dry_run: true` 与 `sandbox: true`，这还不够。Freqtrade 配置、命令行、环境变量、交易所配置任何一处被误改，都可能把“测试策略”变成真实执行风险。

建议新增一个最小 preflight：

```text
scripts/preflight_freqtrade_main_dryrun.py
```

启动前检查：

- config 中 `dry_run === true`
- exchange `sandbox === true`
- 禁止配置 Telegram / webhook / external distribution
- pair whitelist 只能是 BTC/ETH 永续合约
- leverage 不超过 5
- 不存在主网 key 文件路径
- 不允许读取 `agents/wanglin/.binance_futures_api.json`
- 只允许读取 `.binance_futures_api.testnet.json`

如果缺任一条件，直接退出，不启动 Freqtrade。

### 2. 不建议直接裸跑 `freqtrade trade`

pre_review 里的命令：

```bash
freqtrade trade --strategy MainTrendStrategy --config ...
```

建议 v1 不直接暴露为默认运行方式。更安全的方式是提供 wrapper：

```text
scripts/run_main_trend_dryrun.sh
```

wrapper 先跑 preflight，通过后才调用 Freqtrade。这样后续 cron 或人工运行都不容易绕过安全门。

### 3. 风控模块必须是下单前 gate，不只是 strategy helper

独立 `risk/risk_control.py` 是正确方向，但要避免它变成“可选工具函数”。建议结构上强制：

```text
strategy signal -> proposed order -> risk_control.validate_order() -> approved/rejected order
```

最低要求：

- 无止损：拒绝
- 单笔风险 > 1%：拒绝
- 杠杆 > 5x：拒绝
- 日内亏损触及 3%：拒绝新开仓
- pair 不在白名单：拒绝
- 非 dry-run/testnet 环境：拒绝

如果只是把风控计算散落在 `populate_entry_trend` 或 `custom_stoploss` 里，未来很容易被策略迭代绕开。

### 4. Freqtrade 与“动态止损 / 仓位计算”的职责边界要先查清

pre_review 中提到 `custom_stoploss` 和基于 ATR 的动态止损，这是正确方向，但 Freqtrade 的实际行为需要先确认：

- `custom_stoploss` 返回值语义是否与预期一致；
- exchange futures 下的 stoploss 是本地模拟、交易所挂单，还是由 bot 轮询触发；
- `stake_amount` / `custom_stake_amount` 是否能表达 R 单位仓位；
- leverage callback 是否能对 futures pair 生效；
- dry-run 与 backtesting 对这些 callback 的行为是否一致。

建议实现前先写一个极小探针或阅读 Freqtrade 当前版本文档，避免把风控写在 Freqtrade 不会调用的位置。

---

## 策略设计意见

### Donchian 突破逻辑

可以作为 v1 起点。但需要注意一个常见偏差：如果“过去 N 根最高价”包含当前 K 线，会产生未来函数或突破信号失真。实现时应使用上一根已完成窗口：

```text
upper = rolling_high(N).shift(1)
lower = rolling_low(N).shift(1)
```

信号应基于已收盘 K 线，不使用未完成 K 线。

### Funding rate 过滤

方向合理，但 v1 不建议把 funding 历史拉取做得太复杂。最低可接受方案：

- live/dry-run：可读当前或最近 funding；
- backtesting：若没有完整历史 funding，必须标记为 degraded mode，不能把结果当完整策略回测；
- 回测报告必须写清楚是否包含 funding filter。

如果历史 funding 数据补不齐，建议先做两个回测版本：

1. Donchian only；
2. Donchian + funding filter（仅在历史 funding 完整区间）。

### 多空方向

我建议 v1 **仅做多头**。

理由：

- BTC/ETH 长期结构对做多更友好；
- 做空的风控、资金费率解释、趋势失效条件都更复杂；
- 第一版目标是验证执行层策略化，不是一次性覆盖双向交易；
- 降低实盘前行为面复杂度。

若未来要加入做空，应单独走 pre_review。

---

## 回测要求

原方案 `20240101-20251231` 不够。建议改为：

```text
20220601-20260501
```

至少覆盖：

- 2022 LUNA / FTX 后的极端熊市与去杠杆；
- 2023 修复行情；
- 2024 ETF 牛市；
- 2025 波动环境。

最低报告字段：

- CAGR / total return
- max drawdown
- Sharpe 或 Sortino
- win rate
- profit factor
- expectancy per trade
- max consecutive losses
- largest single loss
- daily loss circuit breaker trigger count
- average holding time
- long-only benchmark 对比：BTC buy-and-hold、ETH buy-and-hold

如果没有 benchmark，对 BTC/ETH 趋势策略的收益质量很难判断。

---

## 文件改动建议

pre_review 拟新增文件基本合理，但建议调整为：

```text
strategies/main_trend_strategy.py
risk/risk_control.py
config/freqtrade_main_dryrun.json
scripts/preflight_freqtrade_main_dryrun.py
scripts/run_main_trend_dryrun.sh
handoffs/2026-05-05_day5_main_trend_handoff.md
```

暂缓新增 `_indicators.py`，除非 `main_trend_strategy.py` 已经明显臃肿。第一版不宜过早拆太多模块。

README 可以补 `strategies/` 入口，但不要把策略脚本接入 `refresh_market_os_full_chain.sh`。本轮策略 dry-run 与主刷新链应保持隔离。

---

## 对 A-E 决策的建议

### A. 多空双向 vs 仅多头

建议：**v1 仅多头**。

做空留到后续版本单独审查。

### B. 回测时间范围

建议：**`20220601-20260501`**。

如果数据不足，必须在报告里写明实际覆盖区间。

### C. Donchian 周期

建议：起步 20，可以回测 `[10, 15, 20, 30, 50]`。

但 hyperopt 不应同时优化太多风控参数，避免过拟合。

### D. 资金费率阈值

建议：起步 `±0.05%`，但先统计 BTC/ETH funding 分布。

可比较：

```text
0.02%, 0.05%, 0.10%
```

但这些只能作为过滤阈值实验，不能让 hyperopt 改动硬风控。

### E. Telegram 通知

建议：**v1 默认关闭**。

等 dry-run 稳定后再单独开通知 handoff。外部分发/通知属于外部动作，应走独立确认流程。

---

## 必须阻止的情况

如果实施中出现以下任一情况，应停止并回到 review：

- Freqtrade config 中出现 `dry_run: false`
- config 或代码读取主网凭证 `.binance_futures_api.json`
- 自动主链 `refresh_market_os_full_chain.sh` 调用策略运行、下单、dry-run 或外部分发
- Telegram / webhook / Binance Square / X 通知默认开启
- 风控只在注释或文档中存在，代码中没有执行 gate
- 回测只覆盖 2024-2025 却准备进入 dry-run 评估
- funding rate 数据缺失但报告未标记 degraded

---

## Codex 最终建议

可以进入实施，但要按以下顺序：

1. 先写 config 与 preflight；
2. 再写 risk gate；
3. 再写 strategy；
4. 先跑 syntax/config/preflight 测试；
5. 再下载 futures K 线数据；
6. 先回测，再 dry-run；
7. handoff 中明确写清楚没有真实交易、没有外部分发、没有新增 key。

本轮目标不是追求策略收益最大化，而是建立“策略意图 → 风控批准 → dry-run 执行 → 回测/校准留痕”的正确骨架。这个骨架搭稳以后，后续参数、指标、过滤器都可以逐步升级。
