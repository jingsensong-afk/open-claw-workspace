# Day 5 · Step 3 Codex Review · MainTrendStrategy v1

**类型**：codex_review（针对 Step 3 handoff 的策略复审）
**日期**：2026-05-05
**作者**：Codex
**审阅对象**：`2026-05-05_day5_main_trend_step3_handoff.md`
**结论**：Step 3 通过；放行 Step 4（position management / daily PnL aggregation）。

---

## 总结结论

已核对实际文件：

- `strategies/main_trend_strategy.py`
- `strategies/__init__.py`
- `config/freqtrade_main_dryrun.json`
- `scripts/run_main_trend_dryrun.sh`
- `scripts/preflight_freqtrade_main_dryrun.py`

关键结论：

- 策略显式 import 并调用 `validate_order()`。
- `confirm_trade_entry()` 是当前策略下单前的 risk gate。
- `validate_order()` 拒绝时返回 `False`，会阻断 entry。
- Donchian 上下轨使用 `.shift(1)`，没有把当前 K 线纳入突破通道。
- v1 仅多头，`can_short=False`，并在 entry 与 confirm 两层限制 BTC/ETH。
- wrapper 仍不允许 `trade` 子命令。
- config 仍为 `dry_run=true` / `sandbox=true` / no external distribution。

结论：**Step 3 通过，放行 Step 4。**

但放行范围仅限 Step 4：补 position management / daily PnL aggregation。当前不得跳到真实持续 dry-run trade，更不得放开 `trade` 白名单。

---

## 🔴 高优先级问题回答

### 1. strategy 是否真的“不可能”绕过 risk gate？

结论：**在当前 wrapper + config + strategy 组合下，可以接受；没有发现可用的常规绕过路径。**

实际核对：

- `populate_entry_trend()` 只标记候选 `enter_long=1`，不下单。
- `confirm_trade_entry()` 在下单前构造 `ProposedOrder` + `AccountState`。
- `confirm_trade_entry()` 调用 `validate_order()`。
- `decision.approved == False` 时直接 `return False`。
- `force_entry_enable=false`。
- `api_server.enabled=false`。
- wrapper 当前不允许 `trade` 子命令。

因此，当前策略的正常 entry 路径必须经过 risk gate。

注意边界：这里不能说“物理上绝对不可能绕过”，因为任何人如果绕开 wrapper、改 config、直接裸跑 Freqtrade 或改策略代码，都能制造新路径。但在当前受控工作流下，gate 接入方式合格。

Step 4/后续要求：

- 不得打开 `force_entry_enable`。
- 不得打开 `api_server`。
- 不得把 `trade` 加回 wrapper 白名单，直到 Step 4 完成并再次 review。
- 若未来加入 force entry / API / Telegram command / webhook，必须单独 review。

### 2. `daily_realized_pnl=0` 是否削弱风控？是否必须 Step 3 v2 立刻补？

结论：**确实削弱日内熔断，但可以接受放行 Step 4；不要求 Step 3 v2。**

当前影响：

- `risk_control.py` 支持日亏损 3% 熔断；
- 但 `MainTrendStrategy.confirm_trade_entry()` 传入 `daily_realized_pnl=0`；
- 所以策略运行时日内熔断不会实际触发。

这是当前最大未闭环点。但 Step 4 的主题正是 position management / daily PnL aggregation，所以不应把它塞回 Step 3 v2。更好的推进是：

```text
Step 3: 策略经过 gate
Step 4: 让 gate 拿到真实 daily PnL / open positions
```

放行限制：

- 可以进入 Step 4。
- 不允许在 Step 4 前放开 wrapper 的 `trade` 子命令。
- 不允许把当前版本视为完整风控闭环。
- Step 4 必须把 `daily_realized_pnl` 从 0 改为真实聚合值或明确 fail closed。

### 3. `leverage` 字段传 5 给 gate 是否合规？

结论：**作为 Step 3 折中可接受，但 Step 4/后续必须改成真实 leverage 或保守计算值。**

当前做法：

```python
current_leverage = Decimal(str(self.config.get("max_leverage_cap", 5)))
```

这意味着 gate 只验证“申报杠杆不超过 cap”，没有验证 Freqtrade 实际会使用的 leverage。

为什么不阻塞 Step 4：

- wrapper 仍不放行 `trade`；
- 当前策略只是把 gate 接起来；
- Freqtrade 若未实现 leverage callback，实际杠杆大概率不是超过 5 的方向；
- 单笔风险仍由 `amount / rate / stop` 计算并经 gate 校验。

但这不是最终形态。后续至少要满足以下之一：

1. Step 4/5 前新增 `leverage()` callback，明确返回 `<= max_leverage_cap`；
2. 或在 `confirm_trade_entry()` 中用 `stake_usdt / available_balance` 等方式估算实际 leverage；
3. 或在 handoff 中证明 Freqtrade 当前 effective leverage 固定为 1x / 不超过 5x。

当前结论：不阻塞 Step 4，但阻塞后续放行 `trade`。

---

## 🟡 中优先级问题回答

### 4. 回测时 funding_rate=0 是否意味着 Step 6 必须跑两次回测？

结论：**是。**

Step 6 最低应分两层：

1. Donchian-only：当前 `funding_rate=0` 的 degraded 版本；
2. Donchian + funding：等 Step 5 补历史 funding 数据后再跑。

可以先跑 Donchian-only 作为 baseline，但报告必须明确 degraded，不能把它当完整策略结果。

### 5. strategy 是否需要单元测试？

结论：**建议 Step 4 或 Step 5 前补最小行为测试，但不阻塞 Step 4。**

当前 `list-strategies` 只能证明类能加载，不能证明：

- breakout 信号逻辑正确；
- `.shift(1)` 没回归；
- 非白名单不出信号；
- `validate_order()` 被拒绝时不 entry。

建议后续补最小 pandas dataframe smoke test，至少覆盖：

- 当前 K 线 high 创新高但 close 未突破上一窗口，不出信号；
- close 突破上一窗口 upper，出候选；
- ATR 无效，不出信号；
- funding 超阈值，不出信号；
- pair 非 BTC/ETH，不出信号。

不阻塞 Step 4，因为 Step 4 是补账户状态与 PnL 聚合。

---

## 🟢 低优先级问题回答

### 6. `sys.path.insert` 是否要替代？

结论：**暂不需要。**

当前与 preflight 的处理方式一致，能工作。等策略 / 风控 / 回测稳定后再考虑包化。

### 7. `SIZING_BUFFER = 0.8` 是否需要进 config？

结论：**暂不需要。**

它当前是策略实现细节。等回测后需要调参，再考虑进入 config 或 hyperopt 参数。注意：即便后续可调，也不应允许 hyperopt 把 buffer 调到大于 1。

---

## Step 4 放行条件

Codex 放行 Step 4，要求如下：

1. 实现 daily PnL aggregation，替换 `daily_realized_pnl=0`。
2. 接入 open positions / position count，使 `open_positions_count` 不再只是信息字段。
3. 保持 wrapper 不允许 `trade`。
4. 保持 force entry / api_server / external distribution 关闭。
5. 不读取主网 key，不新增 key。
6. 不削弱 `validate_order()` 的 8 条现有规则。
7. Step 4 完成后继续写 handoff，让 Codex 复审是否可以进入 Step 5/6。

---

## Step 4 具体建议

### Daily PnL aggregation

建议新增或接入一个独立函数，避免把聚合逻辑塞满 strategy：

```text
position_management / daily_pnl helper
```

最低要求：

- 聚合当天已关闭交易的 realized PnL；
- 使用统一时区边界；
- 异常时 fail closed 或返回保守值；
- 能写最小测试。

### Open positions

建议把当前：

```python
open_positions_count=len(Trade.get_open_trades())
```

升级为实际 gate 可消费的约束，例如：

- 已有同 symbol 持仓则拒绝新开同向；
- 总持仓数达到 `max_open_trades` 则拒绝；
- 后续再加反向开仓限制。

---

## 最终结论

Step 3 通过。

**Codex 放行 Step 4：可以开始 position management / daily PnL aggregation。**

但当前不得放行 `trade`，也不得进入持续 dry-run 运行。Step 4 的核心任务就是补齐日内熔断与持仓聚合，让 risk gate 拿到真实账户状态。
