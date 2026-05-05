# Day 5 · Step 4 v2 Hardening Handoff

**类型**：补充 handoff（针对 Step 4 codex_review 的 hardening patch）
**日期**：2026-05-05
**作者**：Claude Code
**对应提交**：`de695a2 wanglin: harden Step 4 per Codex review (Step 4 v2)`
**关联 review**：`2026-05-05_day5_main_trend_step4_codex_review.md`
**前置 handoff**：`2026-05-05_day5_main_trend_step4_handoff.md`

---

## 本轮目标

按 Codex Step 4 review 的"Step 6 阻塞条件"补 3 项硬化。Codex 已放行 Step 5（数据下载）但**阻塞 Step 6 回测**直到这些修完。我选择**先做 v2 hardening 再开 Step 5**，让 codebase 保持干净，避免后面回头再修。

| Codex 阻塞条件 | 实施 |
|---|---|
| 🔴 1. `aggregate_daily_realized_pnl(now=current_time)` | ✅ |
| 🔴 2. Trade 查询失败 → fail closed（拒绝入场） | ✅ |
| 🔴 3. v1 禁止同 symbol 反向开仓 | ✅ Rule 9 加严 |
| 🟡 4. 多重违规含 Rule 9/10 的回归测试 | ✅ 新增 test 21b |

## 改动文件

```
修改：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/risk_control.py             (+17/-? 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/test_risk_control.py        (+41 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/main_trend_strategy.py (+25/-? 行)

未动：
  position_management/  (该模块已支持 now 参数，无需改)
  scripts/              (preflight + wrapper 不变)
  config/               (不变)
```

## 三处关键改动

### 1. Rule 9 加严（risk_control.py）

```python
# Step 4 (loose):
if pos.symbol == order.symbol and pos.side == order.side:
    failures.append(f"已有 {order.symbol} {order.side} 持仓，v1 不允许同向加仓")

# Step 4 v2 (strict):
if pos.symbol == order.symbol:
    failures.append(f"已有 {order.symbol} {pos.side} 持仓，v1 不允许同 symbol 再开仓（无论方向）")
```

含义：v1 是单方向趋势策略，**绝不允许同币种同时持仓**——既不允许金字塔加仓，也不允许反向对冲。后续支持 hedge 必须单独走 review。

### 2. Strategy 传 current_time（main_trend_strategy.py）

```python
# Before:
daily_pnl = aggregate_daily_realized_pnl(trade_records)
# → wall clock UTC，回测时"今天"永远是 2026-05-05，
#   历史 trade 的 close_date 都早于此 → daily PnL 永远 = 0
#   → 日内熔断在回测中等于失效

# After:
daily_pnl = aggregate_daily_realized_pnl(trade_records, now=current_time)
# → backtest-aware：回测到 2022-06-15 时，"今天"就是 2022-06-15
#   日内熔断在回测中真实生效
```

### 3. Strategy fail-closed（main_trend_strategy.py）

```python
# Before (fail open):
try:
    all_trades = Trade.get_trades_proxy()
except Exception as e:
    logger.warning(...)
    all_trades = []  # 继续，daily_pnl 会被算成 0

# After (fail closed):
try:
    all_trades = Trade.get_trades_proxy()
except Exception as e:
    logger.error(f"...无法计算日 PnL → 拒绝入场（fail closed）")
    return False  # 直接拒绝，不冒"看不见风险就当没有风险"的险
```

`Trade.get_open_trades()` 同理。

## 验证

| 测试 | 结果 |
|---|---|
| risk_control 单测 | ✅ 29/29（含 1 个新增多重违规） |
| position_management 单测 | ✅ 14/14（无变化） |
| preflight 集成检查 | ✅ 21/21（无变化） |
| freqtrade list-strategies | ✅ MainTrendStrategy Status OK |

## 是否涉及真实交易

**否**。本次修改全部加强护栏：
- Rule 9 比 Step 4 更严
- Trade 查询失败从 fail-open 改为 fail-closed
- 回测时间正确传递

未引入任何下单路径。

## 是否涉及外部分发

**否**。

## 是否涉及 API Key / token / secret

**否**。

## 已知风险

### 行为变更（不是 bug，但需要 Codex 确认）

1. **Test 19 测试预期翻转**
   - Step 4：BTC long when have BTC short → PASS
   - Step 4 v2：同上 → REJECT
   - 任何依赖旧行为的代码（目前没有）会受影响
   - Strategy v1 只做 long，不会主动触发这条，但人工或 force_entry（已禁用）会

2. **fail-closed 可能导致策略在 Freqtrade 启动早期"啥也不做"**
   - 启动头几秒 Trade 数据库可能未完全初始化
   - 当前实现会拒绝所有入场直到查询成功
   - 这是正确行为（保守优先），但意味着回测刚开始的几个 K 线可能错过信号
   - Codex 是否认为这是可接受的代价？

### 设计层（继承自 Step 4，未在 v2 解决）

3. **`leverage` 字段仍传 5（max cap）给 gate**
   - Codex Step 3 review 说"Step 4 / 后续必须改成真实计算"
   - v2 没动这个，因为 Codex Step 4 review 没把它列为 v2 阻塞条件
   - 进入 Step 6 前是否要补？

4. **strategy 单元测试仍未加**
   - Codex Step 3 review 说"建议 Step 4/5 前补"，但不阻塞
   - 当前依赖 list-strategies + 集成测试

## 建议 Codex 检查点

按重要性排序：

### 🔴 高（关于 v2 是否够进 Step 6 / Step 5）

1. **回测期间 daily_pnl 是否真的会按 current_time 聚合**
   - 我读过 Freqtrade `confirm_trade_entry` 文档，confirm_trade_entry 收到 current_time 是 `pd.Timestamp` 或 `datetime`
   - `aggregate_daily_realized_pnl` 接受 `Optional[datetime]`，应该兼容
   - 但**没有真跑过回测**验证。建议 Codex 在 review 时简单确认 Freqtrade 的 current_time 传值类型

2. **fail-closed 的"启动早期"行为**
   - 是否需要加宽限期：启动后头 N 秒允许 Trade 查询失败 fail-open，超过 N 秒后 fail-closed？
   - 还是当前严格行为更安全？

3. **Rule 9 strict 是否会与 max_open_trades=2 在某些场景下冲突**
   - 同 symbol 不允许加仓 + 不允许对冲 → 单 symbol 最多 1 仓
   - 总持仓数 ≤ 2 → 系统总能开 2 个不同 symbol 的仓
   - v1 白名单只有 BTC + ETH，所以最多 1 BTC + 1 ETH，正好对齐 max_open_trades=2
   - 后续如果加白名单（SOL 等），需要重新评估

### 🟡 中

4. **fail-closed 的日志级别**
   - 当前 Trade 查询失败 → `logger.error`
   - 是否需要降为 warning（避免每次启动都报 error 噪音）？

### 🟢 低

5. **Test 19 命名是否清楚反映 v2 行为变化**
6. **Test 21 fixture 用 ETH+SOL（SOL 不在白名单）的合理性**

---

## 等待信号

- ⏳ Codex 对 v2 hardening handoff 的快速 review（应该是确认性 review，非阻塞性）
- ⏳ 如果 v2 通过 → 景森给 go 进入 **Step 5：数据下载**
  - K 线 + 历史 funding，时间窗 `20220601-20260501`
  - 目标：BTC/USDT:USDT + ETH/USDT:USDT 两个交易对
  - 工具：freqtrade download-data 子命令（已在 wrapper 白名单）
  - 数据将存到 `user_data/data/binance/` 下（gitignore 已排除）

进入 Step 5 前的最终状态快照：
- preflight 21 项 + wrapper 2 道护栏 + risk gate **10 条规则（Rule 9 加严）**
- 64 项单元/集成测试全过（risk 29 + position 14 + preflight 21）
- Strategy fail-closed on Trade query failure
- Strategy backtest-aware（current_time 正确传递）
- 全部 dry-run + testnet，未触发任何真实交易、外部分发、新凭证
