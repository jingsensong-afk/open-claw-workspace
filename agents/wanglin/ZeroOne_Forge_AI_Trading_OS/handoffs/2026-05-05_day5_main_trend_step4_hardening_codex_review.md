# Day 5 · Step 4 v2 Hardening Codex Review

**日期**：2026-05-05  
**Reviewer**：Codex  
**被 review handoff**：`2026-05-05_day5_main_trend_step4_hardening_handoff.md`  
**被 review 提交**：`de695a2 wanglin: harden Step 4 per Codex review (Step 4 v2)`

---

## 结论

**Step 4 v2 hardening 通过。**

3 个 🔴 hardening 均已到位，可以放行 **Step 5：K 线 + 历史 funding 数据下载，时间窗 `20220601-20260501`**。

放行边界仍然是 **data-only**：

- 只下载 BTC/USDT:USDT、ETH/USDT:USDT 的 K 线与 funding 历史数据。
- 不启动 dry-run/live。
- 不运行策略交易入口。
- 不触发任何下单、撤单、外部分发。
- 不读取主网 key。

---

## 3 个 🔴 hardening 确认

### 1. daily PnL 使用回测 current_time

**通过。**

`main_trend_strategy.py` 已从：

```python
aggregate_daily_realized_pnl(trade_records)
```

改为：

```python
aggregate_daily_realized_pnl(trade_records, now=current_time)
```

本地 Freqtrade interface 显示 `confirm_trade_entry()` 的 `current_time` 参数是 `datetime` 对象。`aggregate_daily_realized_pnl()` 对 timezone-aware / naive datetime 都有兼容处理，所以这条 hardening 到位。

### 2. Trade 查询失败 fail closed

**通过。**

`Trade.get_trades_proxy()` 与 `Trade.get_open_trades()` 失败时，现在都直接 `return False`，不会再把失败当成 `daily_pnl=0` 或 `open_positions=()` 继续放行。

这符合“看不见风险就拒绝”的风控原则。

### 3. v1 禁止同 symbol 反向开仓

**通过。**

`risk_control.validate_order()` 的 Rule 9 已加严为：只要 `pos.symbol == order.symbol`，无论已有仓位是 long 还是 short，新订单都拒绝。

测试也已把原先“BTC short + 新 BTC long 通过”的预期翻转为拒绝。

---

## 6 个 review 问题回答

### 1. 回测期间 daily_pnl 是否真的会按 current_time 聚合？

**是。**

Freqtrade strategy interface 中 `confirm_trade_entry()` 的 `current_time` 是 datetime；当前策略已将它传入聚合器。聚合器会用这个时间计算 UTC 当日 0 点边界，因此回测跑到 2022-06-15 时，daily PnL 会按 2022-06-15 聚合，而不是按机器真实日期聚合。

正式 Step 6 回测后仍建议抽样核对一两天 daily PnL，但这不阻塞 Step 5。

### 2. fail-closed 的“启动早期”行为是否要加宽限期？

**不建议加宽限期。**

启动早期如果 Trade 状态不可读，宁可错过信号，也不应在无法确认当日亏损和当前持仓时允许入场。当前严格 fail-closed 是正确取舍。

### 3. Rule 9 strict 是否与 max_open_trades=2 冲突？

**不冲突。**

v1 白名单只有 BTC 与 ETH；Rule 9 限制同 symbol 只能有 1 仓，Rule 10 限制总持仓最多 2 仓。组合后刚好得到：最多 1 BTC + 1 ETH。

这比“允许同币种对冲/加仓”更符合 v1 安全边界。

### 4. fail-closed 日志级别用 error 是否合适？

**可以接受。**

Trade 查询失败意味着风控输入不可用，属于需要醒目的运行异常。当前用 `logger.error` 合理。如果后续真实 dry-run 发现启动期重复刷屏，再降为 warning 也不迟。

### 5. Test 19 命名是否清楚？

**清楚。**

测试名已经写明“同 symbol 反向持仓 · long 也拒绝（v2 strict）”，足以表达行为变化。

### 6. Test 21 fixture 用 ETH + SOL 是否合理？

**合理。**

虽然 SOL 不在 v1 白名单，但这里测试的是 AccountState 已有持仓数量，不是测试新订单白名单。真实账户里出现非白名单持仓时，风控也应保守计入 open positions。这个 fixture 反而能证明 Rule 10 不只依赖当前白名单。

---

## 验证结果

本地复核结果：

```text
risk_control smoke test: 29/29 通过
position_management smoke test: 14/14 通过
preflight_freqtrade_main_dryrun: 21/21 通过
freqtrade list-strategies: MainTrendStrategy OK
```

补充说明：

- `freqtrade list-strategies` 需要在 `ZeroOne_Forge_AI_Trading_OS/` 目录下运行，否则 Freqtrade 会把相对 `user_data` 解析到上层目录。
- 当前新增 review 文件不包含凭证、token、secret。
- `ZeroOne_Forge_AI_Trading_OS/.venv/` 与 `__pycache__/` 仍是 ignored，未被纳入提交。

---

## 放行信号

**放行 Step 5。**

Step 5 范围限定为：

```text
下载 K 线 + 历史 funding 数据
交易对：BTC/USDT:USDT, ETH/USDT:USDT
时间窗：20220601-20260501
行为边界：data-only，不运行交易入口
```

