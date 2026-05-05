# Day 5 · Step 4 Codex Review · Position Management + Daily PnL

**日期**：2026-05-05  
**Reviewer**：Codex  
**被 review handoff**：`2026-05-05_day5_main_trend_step4_handoff.md`  
**被 review 提交**：`4e1ede0 wanglin: position management + daily PnL aggregation (Day 5 step 4)`

---

## 结论

**Step 4 基础实现通过，但不是完整交易放行。**

可以放行 **Step 5：K 线 + 历史 funding 数据下载，时间窗 `20220601-20260501`**。理由是 Step 5 只做数据下载，不应触发策略下单、回测下单模拟、dry-run 下单或任何主网行为。

但在进入 **Step 6 回测** 或任何可能调用 `confirm_trade_entry()` 的执行路径前，建议先做 **Step 4 v2 hardening**，至少修复：

1. 回测时间必须使用模拟当前时间，而不是 wall clock。
2. Trade 查询失败必须拒绝入场，而不是按 `daily_pnl=0 / open_positions=()` 继续。
3. v1 是否禁止同 symbol 反向持仓需要明确；我建议 v1 禁止。

---

## 3 个 🔴 高优先级问题

### 1. 反向开仓在 v1 是否真的不需要禁止？

**结论：不建议保留当前行为。**

当前 `risk_control.validate_order()` 的 Rule 9 只拒绝同 symbol 同 side 加仓：

```python
if pos.symbol == order.symbol and pos.side == order.side:
    reject
```

所以已有 `BTC/USDT:USDT short` 时，新开 `BTC/USDT:USDT long` 会通过；现有测试也明确把这个行为当成通过。

严格看，`MainTrendStrategy` v1 当前只做 long，策略自身不会主动开 short；但如果账户里已有人工 short、历史残留 short、或未来模块接入 short，当前 gate 会允许同币种反向开仓。这对 v1 “不对冲、不加仓、单方向趋势策略”的安全边界不够清晰。

**建议 Step 4 v2 加 Rule 11：同 symbol 已有任意 side 持仓，新订单一律拒绝。**  
如果未来要支持对冲或反手，应单独设计 position mode、close-before-open 逻辑和测试，而不是让 v1 默认通过。

对 Step 5 的影响：**不阻塞数据下载**。  
对 Step 6/交易入口的影响：**建议先修复再回测/运行策略**。

### 2. `close_profit_abs` 是否含手续费？

**结论：本地 Freqtrade 源码显示包含手续费。**

在当前项目隔离环境的 Freqtrade 源码中，`Trade.calculate_profit()` 注释明确说明利润计算包含 fees；`recalc_trade_from_orders()` 在关闭交易分支也有注释说明 fees 已经属于 `close_profit_abs` 的一部分。

因此 Step 4 直接聚合 `close_profit_abs` 作为已实现绝对盈亏是合理的，不需要额外手动扣 fee。手动再扣一次反而可能重复扣费。

保留建议：Step 6 回测输出后，用回测报告中的 daily profit / trade profit 抽样核对一次，确认版本行为与本地源码一致。

### 3. `Trade.get_trades_proxy()` 在回测中的语义，以及 now 参数问题

**结论：`get_trades_proxy()` 可用于回测，但当前 `now=None` 调用会导致 daily PnL 在回测中失真。**

本地 Freqtrade 源码显示：

- live / dry-run：`Trade.get_trades_proxy()` 走数据库查询。
- backtest：`Trade.get_trades_proxy()` 走 `LocalTrade.bt_trades` / `bt_trades_open` 内存列表。

所以“能不能拿到回测交易列表”这点基本通过。

但 Step 4 当前在策略里调用：

```python
daily_pnl = aggregate_daily_realized_pnl(trade_records)
```

`aggregate_daily_realized_pnl()` 在 `now is None` 时使用 `datetime.now(UTC)`。回测一次会跑很多历史日期，如果用真实机器时间作为“今天”，历史 trade 的 `close_date` 大概率都早于真实今天 0 点，于是 daily PnL 会长期为 0，日内熔断在回测里等于失效。

**建议 Step 4 v2：由 `confirm_trade_entry(..., current_time, ...)` 把 Freqtrade 传入的 `current_time` 继续传给聚合器：**

```python
daily_pnl = aggregate_daily_realized_pnl(trade_records, now=current_time)
```

同时建议测试覆盖“回测日期为 2022-06-02，真实机器日期为 2026-05-05 时，当日 PnL 仍按 2022-06-02 聚合”。

对 Step 5 的影响：**不阻塞数据下载**。  
对 Step 6 的影响：**阻塞回测可信度，建议先修复再跑正式回测**。

---

## 额外中优先级发现

### Trade 查询失败目前是 fail open，不是 fail closed

当前 `main_trend_strategy.py` 中：

- `Trade.get_trades_proxy()` 失败后设为 `all_trades = []`，导致 `daily_pnl = 0`。
- `Trade.get_open_trades()` 失败后设为 `open_trades = []`，导致 `open_positions = ()`。

这会让风控在无法读取历史亏损/当前持仓时继续评估新订单，实际语义是“看不见风险就当没有风险”，不符合 fail closed。

建议 Step 4 v2 改为：

- 任一 Trade 查询失败，`confirm_trade_entry()` 直接 `return False`。
- log 使用 error/warning 均可，但行为必须拒绝入场。

### 多重违规测试可以再补 Rule 9/10

现有 Rule 9 / Rule 10 的单独测试已经覆盖；建议再补一个多重违规场景，确认同一笔订单同时触发原有规则和持仓规则时，`reasons` 会完整返回，避免未来改动把 failures 提前 return。

---

## 验证结果

本地验证：

```text
risk_control smoke test: 28/28 通过
position_management smoke test: 14/14 通过
preflight_freqtrade_main_dryrun: 21/21 通过（使用项目 .venv Python）
```

环境备注：

- 系统 `python3` 能跑纯本地 smoke tests。
- preflight 脚本使用了较新的类型语法，需要项目 `.venv` 的 Python 运行。

---

## 放行边界

**放行 Step 5：**

- 仅下载 K 线与历史 funding 数据。
- 时间窗：`20220601-20260501`。
- 不运行策略。
- 不启动 dry-run/live。
- 不读取主网 key。
- 不触发任何订单、撤单、外部分发。

**暂不放行 Step 6：**

在 Step 6 正式回测前，建议先完成 Step 4 v2 hardening：

1. `aggregate_daily_realized_pnl(..., now=current_time)`。
2. Trade 查询异常直接拒绝入场。
3. 明确并最好禁止 v1 同 symbol 反向持仓。

