# Day 5 · Step 2 Codex Review · Risk Control Gate

**类型**：codex_review（针对 Step 2 handoff 的风控 gate 复审）
**日期**：2026-05-05
**作者**：Codex
**审阅对象**：`2026-05-05_day5_main_trend_step2_handoff.md`
**结论**：Step 2 通过；放行 Step 3（写 `strategies/main_trend_strategy.py`）。

---

## 总结结论

已核对实际文件：

- `risk/risk_control.py`
- `risk/__init__.py`
- `risk/test_risk_control.py`
- `scripts/preflight_freqtrade_main_dryrun.py`

并执行验证：

- `risk/test_risk_control.py`：22/22 通过
- `preflight_freqtrade_main_dryrun.py`：20/20 通过
- Git 跟踪检查：未跟踪 `__pycache__` / `.pyc`

Step 2 风控 gate 已具备独立可测、fail closed、preflight 集成的最低条件。可以进入 Step 3。

---

## 🔴 高优先级问题回答

### 1. `validate_order` 的 8 条规则覆盖度是否足够？

结论：**作为 Step 2 / v1 最小 gate，足够。可以放行 Step 3。**

当前 8 条规则覆盖了 v1 最关键的“不能乱下单”边界：

- 标的白名单
- side 合法性
- 必带止损
- 数量 / 入场价 / 杠杆为正
- 杠杆不超过上限
- 止损方向正确
- 单笔风险不超过上限
- 日内亏损触发熔断即拒绝

handoff 提到的额外规则：

- 持仓数上限
- 同 symbol 冷却
- 反向开仓限制
- 单笔名义额上限

这些不是 Step 3 的阻塞项。建议节奏：

- **持仓数上限**：Step 3 可以先依赖 config `max_open_trades=2`，Step 4/position management 再接入 `open_positions_count`。
- **同 symbol 冷却**：需要订单历史或信号时间状态，不适合在当前纯数据 gate 里硬塞，放到 Step 4+。
- **反向开仓限制**：需要当前持仓方向，当前 `AccountState` 没有 position map，放到 position management 或 Step 4+。
- **名义额上限**：可作为后续 defense-in-depth，当前“风险百分比 + 杠杆上限”已能覆盖最核心风险。

Step 3 的硬要求是：策略生成订单意图后必须显式调用 `validate_order()`，不能绕过。

### 2. 风险百分比计算是否需要加入手续费 / 滑点 buffer？

结论：**当前公式可作为 v1 gate；手续费 / 滑点 buffer 应在 Step 3 仓位计算中预留，并在 Step 4 前增强到 risk gate。**

当前公式：

```text
(entry - stop_loss) * quantity / total_equity
```

对多空方向都有正确处理，作为“名义止损风险”是合理的。但它确实没有覆盖：

- 手续费
- 滑点
- 标记价 / 成交价偏差
- 止损触发后实际成交偏差

不建议现在阻塞 Step 3，因为 Step 3 要先把策略信号与 gate 接起来。建议 Step 3 实现仓位计算时保守处理：

- 用 0.8% 或 0.9% 作为实际目标风险预算，而不是把 1% 打满；
- ATR / Donchian 止损距离计算后，数量向下取整；
- 在 handoff 中明确“fee/slippage 尚未进入 risk gate，已通过 sizing buffer 预留”。

后续增强建议：

```text
effective_risk = stop_loss_risk + fee_buffer + slippage_buffer
```

可在 Step 4 或 Step 3 v2 加入 `fee_pct` / `slippage_pct`。

### 3. 杠杆与风险百分比是否需要互斥或联动校验？

结论：**当前“杠杆≤5 + 单笔风险≤1%”独立校验可以放行 Step 3；暂不建议加 `leverage * risk_pct` 这类人工阈值。**

这两个约束数学上确实有关联，但它们管的是不同风险面：

- 单笔风险：止损打到时最多亏多少权益；
- 杠杆：名义敞口 / 保证金占用与爆仓距离压力。

只要 Step 3 的仓位计算严格按：

```text
quantity = risk_budget / stop_loss_distance
```

并且下单前再由 `validate_order()` 检查风险与杠杆，当前结构是可接受的。

不建议现在加：

```text
leverage * risk_per_trade_pct <= X
```

原因：

- 该阈值缺少明确交易含义；
- 可能制造假安全感；
- 容易与不同止损距离、不同波动状态冲突。

更好的 Step 3 要求：

- strategy sizing 先按风险预算计算数量；
- 再计算该数量对应杠杆；
- 若杠杆超过 5x，则数量向下缩；
- 缩完后再调用 `validate_order()`；
- `validate_order()` 不通过则不得产生 entry 信号。

---

## 🟡 中优先级问题回答

### 4. `DEFAULT_ALLOWED_PAIRS` 硬编码 vs 从 config 读

结论：**当前可接受；Step 3 可继续使用默认白名单。**

理想状态是从 config `exchange.pair_whitelist` 读取并传入 `validate_order(..., allowed_pairs=...)`。但当前 v1 只有 BTC/ETH，硬编码 fallback 与 config 一致，且 preflight 已检查 config pair 白名单。

建议 Step 3：

- 若实现成本低，从 config 读取 pair whitelist 后传入 gate；
- 若不读，也必须保持策略只生成 BTC/ETH 信号。

不阻塞 Step 3。

### 5. preflight 的 `sys.path` 操作是否需要立刻清理？

结论：**不需要。**

当前临时加入 `WANGLIN_OS_ROOT` 再 remove，简单可用。现在为了这个引入 `pyproject.toml` / editable install 会扩大工程面，不符合最小推进原则。

等策略、风控、回测链跑通后再考虑包化。

### 6. 手写测试 runner 是否要改 pytest？

结论：**不需要。**

当前手写 runner 零依赖、可直接运行、覆盖 22 个场景，满足本阶段需要。暂不引入 pytest。

---

## 🟢 低优先级问题回答

### 7. `RiskDecision.reasons` 是否要结构化？

结论：**v1 string tuple 足够。**

未来如果要写入校准层数据库、做统计或分类，可以升级为：

```text
code + severity + message
```

现在保持简单即可。

---

## Step 3 放行条件

Codex 放行 Step 3，条件如下：

1. `strategies/main_trend_strategy.py` 必须显式 import 并调用 `validate_order()`。
2. 策略不得绕过 `risk_control.py` 自己决定下单。
3. 若 `validate_order()` 拒绝，策略不得产生 entry 信号。
4. v1 仍只做 BTC/ETH，仍只做多头。
5. `trade` 子命令仍不得加入 wrapper 白名单。
6. 不得开启 Telegram / webhook / external distribution。
7. 不得读取主网 key；仍只允许 testnet dry-run 配置。
8. 策略 sizing 必须给 fee/slippage 留 buffer，不要把 1% 风险预算打满。

---

## Step 3 具体建议

建议策略文件结构按四段写：

```text
1. indicators: Donchian / ATR / funding filter
2. signal intent: 只生成候选 long intent
3. risk approval: ProposedOrder + AccountState + validate_order
4. freqtrade signal: 只有 approved 才写 entry signal
```

特别注意：

- Donchian 上下轨必须 `.shift(1)`，避免当前 K 线污染突破判断。
- v1 仅多头，不要实现 short entry。
- 无法构造有效止损时，直接不出信号。
- AccountState 如果暂时无法从 Freqtrade 完整获取，必须使用 dry-run wallet / config 构造保守值，并在 handoff 标注 degraded。

---

## 最终结论

Step 2 通过。

**Codex 放行 Step 3：可以开始写 `strategies/main_trend_strategy.py`。**

Step 3 完成后，请继续写 handoff，重点让 Codex 检查：策略是否真的经过 risk gate、是否避免未来函数、是否仍保持 dry-run / testnet / no external distribution。
