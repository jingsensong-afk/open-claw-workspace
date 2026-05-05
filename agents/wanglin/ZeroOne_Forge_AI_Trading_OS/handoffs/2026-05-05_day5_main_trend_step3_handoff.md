# Day 5 · Step 3 Handoff · MainTrendStrategy v1

**类型**：handoff（Codex 七步走的第 3 步落地）
**日期**：2026-05-05
**作者**：Claude Code
**对应提交**：`10659a2 wanglin: add MainTrendStrategy v1 (Day 5 step 3)`
**关联 review**：`2026-05-05_day5_main_trend_step2_codex_review.md`（含 Step 3 spec）
**前置 handoff**：`2026-05-05_day5_main_trend_step2_handoff.md`

---

## 本轮目标

按 Codex Step 3 spec 实现 `MainTrendStrategy v1`——双系统主系统的第一版业务策略。
核心是把"信号生成 → 仓位计算 → 风控 gate → 真实下单"这条主线接通，**且策略不能绕过风控**。

## Codex 8 条放行条件 · 实施情况

| # | 条件 | 状态 |
|---|---|---|
| 1 | strategies/main_trend_strategy.py 必须显式 import 并调用 validate_order() | ✅ 第 333 行 |
| 2 | 策略不得绕过 risk_control.py 自己决定下单 | ✅ confirm_trade_entry 是唯一下单路径 |
| 3 | validate_order 拒绝 → 策略不得产生 entry 信号 | ✅ 拒绝时 return False，Freqtrade 取消订单 |
| 4 | v1 仍只做 BTC/ETH，仍只做多头 | ✅ can_short=False + ALLOWED_SYMBOLS 双重检查 |
| 5 | trade 子命令仍不得加入 wrapper 白名单 | ✅ 未改 wrapper |
| 6 | 不开 Telegram / webhook / external distribution | ✅ config 未动 |
| 7 | 不读主网 key | ✅ 未引入新凭证文件读取 |
| 8 | sizing 必须给 fee/slippage 留 buffer，不打满 1% | ✅ SIZING_BUFFER=0.8 实际只用 0.8% |

## 改动文件

```
新增：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/__init__.py        (10 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/main_trend_strategy.py  (380 行)

未改动（Step 1/2 资产保持原样）：
  config/freqtrade_main_dryrun.json
  scripts/preflight_freqtrade_main_dryrun.py
  scripts/run_main_trend_dryrun.sh
  risk/__init__.py
  risk/risk_control.py
  risk/test_risk_control.py
```

## 4 段结构（按 Codex spec）

```
1. indicators (populate_indicators)
   ├─ donchian_upper = high.rolling(20).max().shift(1)   ← .shift(1) 防 lookahead
   ├─ donchian_lower = low.rolling(20).min().shift(1)
   ├─ atr = TR.rolling(14).mean()
   └─ funding_rate（live/dry-run 实时拉，回测 degraded 为 0）

2. signal intent (populate_entry_trend)
   ├─ pair 必须 in ALLOWED_SYMBOLS（BTC/USDT:USDT, ETH/USDT:USDT）
   ├─ breakout = close > donchian_upper
   ├─ funding_ok = funding_rate ≤ +0.05%
   ├─ atr_valid = atr 不为空且 > 0
   └─ enter_long = 1（只生成多头候选，never short）

3. risk approval
   ├─ custom_stake_amount: R 单位仓位 = (equity × 0.01 × 0.8) / stop_distance_pct
   └─ confirm_trade_entry:
        ├─ 重新算 stop_loss_price = entry − 2×ATR
        ├─ 构造 ProposedOrder + AccountState
        ├─ decision = validate_order(proposed, account, risk_limits)
        ├─ if not decision.approved: return False  ← 阻止下单
        └─ else: return True，订单进入交易所

4. custom_stoploss
   └─ ATR-based dynamic stop = max(2×ATR/entry_rate, 5%)
```

## 验证记录

```
✅ freqtrade list-strategies (via wrapper)
   MainTrendStrategy · Status OK · main_trend_strategy.py
   → 证明 Freqtrade 能找到、能解析、能加载本策略类
   → 同时证明 wrapper 子命令白名单 + 凭证注入 + preflight 全部正常

✅ preflight 20/20 通过
   3 项 risk gate 集成检查仍 OK，未因 Step 3 引入回归

✅ risk_control 22/22 单元测试通过
   未碰 risk 模块代码，行为不变

✅ Python import smoke
   类属性匹配设计：
   - INTERFACE_VERSION = 3
   - timeframe = 1h
   - can_short = False
   - DONCHIAN_PERIOD = 20
   - ALLOWED_SYMBOLS = ['BTC/USDT:USDT', 'ETH/USDT:USDT']
   - SIZING_BUFFER = 0.8
```

## 是否涉及真实交易

**否**。三层防护未弱化，且新增 4 道闸：

1. wrapper trade 子命令仍被白名单拦下
2. config dry_run=true 未改
3. preflight 20/20 仍校验所有安全约束
4. **新增**：strategy 内 confirm_trade_entry 强制 validate_order，risk gate 拒绝时直接 return False
5. **新增**：strategy 内 ALLOWED_SYMBOLS 在 populate_entry_trend 与 confirm_trade_entry 双重防御
6. **新增**：side != "long" 在 confirm_trade_entry 直接拒绝
7. **新增**：bot_start 阶段如果 load_risk_limits 失败直接 raise，策略不启动

## 是否涉及外部分发

**否**。策略不调用任何分发 API。logger 只写 Freqtrade 自己的日志通道（本地文件 + 控制台）。

## 是否涉及 API Key / token / secret

**否**。策略代码不读凭证文件。Freqtrade 通过 wrapper 注入的 env 变量自己处理交易所认证，与策略隔离。

## 已知风险

### 设计层（degraded 字段）

1. **`daily_realized_pnl` 在 confirm_trade_entry 中暂为 0**
   - Freqtrade 没有原生 API 给"今天累计已实现盈亏"
   - 需要 Step 4 自己写聚合逻辑（查询当日已平仓 trades，求和 close_profit_abs）
   - 当前影响：日内熔断检查永远不触发（因为 daily_realized_pnl=0 永远不会触及 -3%）
   - 缓解：Freqtrade 自带 `max_open_trades=2` 限制并发，且单笔 1% 风险预算控制了灾难放大

2. **`open_positions_count` 用了 `Trade.get_open_trades()` 但**：
   - 只用于信息展示，risk gate 当前没消费这个字段
   - Step 4 可以加"持仓数 ≥ N 拒绝新开仓"规则

3. **`funding_rate` 在回测时为 0（degraded）**
   - 回测时 dp.runmode 不是 live/dry_run，所以 `dataframe['funding_rate'] = 0`
   - 这意味着 Step 6 回测**只验证 Donchian-only 版本**
   - Codex 在 Step 0 review 已要求"Donchian only 与 Donchian+funding 双版本回测"
   - Step 5 数据下载阶段需要把历史 funding rate 也下下来再补这部分

4. **`leverage` 在 ProposedOrder 中保守取 config.max_leverage_cap = 5**
   - 实际杠杆应该由 Freqtrade 根据 stake_amount + balance 算出来
   - 但 Step 3 没法在 confirm_trade_entry 拿到 Freqtrade 真实计算的杠杆
   - 当前传 5 给 risk gate 等于"按最大允许杠杆校验"，gate 总能通过 leverage ≤ 5 这条
   - 但这意味着我们没在策略层验证"实际杠杆"，依赖 Freqtrade 内部
   - 需要 Codex 评估这个折中是否可接受

### 工程层

5. **`sys.path.insert` 在策略文件顶部**
   - strategies/main_trend_strategy.py 第 47-49 行手动加 wanglin OS 根到 sys.path
   - 让 `from risk import ...` 能 work
   - 与 preflight 内部的 sys.path 操作一样，都是临时方案
   - 长期清理需要把 wanglin OS 包化（pyproject.toml）

6. **策略未做单元测试**
   - 与 risk_control 不同，strategy 类直接依赖 Freqtrade 框架，单元测试需要 mock 大量 IStrategy 上下文
   - 当前用 `freqtrade list-strategies` 做"加载性测试"
   - 真实行为测试要等 Step 6 回测才能跑

### 接入层

7. **没有 fee/slippage 显式建模**
   - Codex Step 2 review 已确认这个 v1 通过 sizing buffer 处理是 OK 的
   - 但 SIZING_BUFFER=0.8 是直觉值，不是基于实际 BTC/ETH testnet fee+slippage 数据
   - Step 6 回测后可以反算实际 fee+slippage，再调 buffer

## 建议 Codex 检查点

按重要性排序：

### 🔴 高（关于 risk gate 是否真的不可绕过）

1. **strategy 是否真的"不可能"绕过 risk gate**
   - 当前 confirm_trade_entry 是 Freqtrade 在下单前调用的最后一道关
   - 但 Freqtrade 还有一些"边角下单路径"（如 force_entry / API 触发）
   - 当前 config 已 `force_entry_enable: false` 且 api_server 关闭，所以理论上没绕过路径
   - **请 Codex 确认 Freqtrade 是否还有其他可能跳过 confirm_trade_entry 的下单路径**

2. **`daily_realized_pnl=0` 是否削弱了风控**
   - Codex Step 0 review 强调"日内熔断 3%"是关键风控
   - 当前实现这一条永远不触发（因为字段是 0）
   - 当前 Step 3 没补，留 Step 4 处理
   - **是否可接受 v1 在没有日内熔断真正生效的情况下进入 Step 5/6 回测？**
   - 还是必须立刻在 Step 3 v2 patch 里补完日内 PnL 聚合？

3. **`leverage` 字段传 5（最大允许）给 gate 是否合规**
   - 我们其实没在策略层算实际杠杆，gate 校验等同于"我假设杠杆是 5x，请审批"
   - 这意味着 gate 永远不会因 leverage > 5 拒绝（除非有人改 config 把 cap 改高）
   - **是否需要在 Step 3 中真实计算 leverage = stake_usdt / available_balance？**
   - 还是接受这个保守的"按上限报"做法？

### 🟡 中（关于 v1 完整性）

4. **回测时 funding_rate=0 是否意味着 Step 6 必须跑两次回测**
   - 第一次：Donchian only（funding_rate=0 即此情况）
   - 第二次：Donchian + funding（需要历史 funding 数据，Step 5 才有）
   - **是 Step 5 之前不允许进入 Step 6？还是 Step 6 可以先跑 Donchian-only 报告，再 Step 7 补 funding 版本？**

5. **strategy 是否需要单元测试**
   - 当前只有"加载性测试"（list-strategies）+ "类属性核对"
   - **是否需要 Step 4 之前为 strategy 写最小行为单元测试？**
   - 还是依赖 Step 6 回测产物作为行为验证？

### 🟢 低（关于工程清理）

6. **`sys.path.insert` 在 strategy 顶部是否需要替代方案**
7. **`SIZING_BUFFER = 0.8` 是否需要进 config**

---

## 等待信号

- ⏳ Codex 对 Step 3 handoff 的 review，重点是 🔴 3 项
- ⏳ 如果 🔴 项 1（绕过路径）/ 🔴 项 2（daily PnL）需要立刻补，**Step 3 v2 patch**
- ⏳ 如果 🔴 都通过，景森给 go 进入 **Step 4**（Codex review 中提到 Step 4 是 position management / 当日 PnL 聚合 / open_positions_count 接入）

进入 Step 4 前的状态快照：
- preflight 20 项 + wrapper 2 道护栏 + risk gate 8 条规则 + strategy 4 段结构
- 总测试覆盖：22 个 risk 单测 + 3 个 preflight 集成 + 1 个 freqtrade 加载测试 = 26 项
- 全部 dry-run + testnet，未触发任何真实交易、外部分发、新凭证
