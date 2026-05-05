# Day 5 · Step 4 Handoff · Position Management + Daily PnL Aggregation

**类型**：handoff（Codex 七步走的第 4 步落地）
**日期**：2026-05-05
**作者**：Claude Code
**对应提交**：`4e1ede0 wanglin: position management + daily PnL aggregation (Day 5 step 4)`
**关联 review**：`2026-05-05_day5_main_trend_step3_codex_review.md`（含 Step 4 spec）
**前置 handoff**：`2026-05-05_day5_main_trend_step3_handoff.md`

---

## 本轮目标

按 Codex Step 4 spec 把 Step 3 留下的 degraded 字段（`daily_realized_pnl=0` + `open_positions_count` 信息字段）补成真实值，并让 `validate_order()` gate 真正消费这些信息。完成后日内熔断、同向加仓限制、最大并发持仓数三道护栏才真正生效。

## Codex 7 条放行条件 · 实施情况

| # | 条件 | 状态 |
|---|---|---|
| 1 | Daily PnL aggregation 替换 daily_realized_pnl=0 | ✅ 用 `aggregate_daily_realized_pnl()` |
| 2 | open_positions / position count 真正被 gate 消费 | ✅ Rule 9 + Rule 10 上线 |
| 3 | wrapper 仍不允许 trade | ✅ 未动 wrapper |
| 4 | force entry / api_server / external distribution 关闭 | ✅ 未动 config |
| 5 | 不读主网 key，不新增 key | ✅ |
| 6 | 不削弱 validate_order 已有 8 条规则 | ✅ 全保留，仅加 2 条 |
| 7 | Step 4 完成写 handoff | ✅ 本文件 |

## 改动文件

```
新增：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/position_management/__init__.py        (28 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/position_management/daily_pnl.py       (83 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/position_management/position_state.py  (45 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/position_management/test_position_management.py  (179 行)

修改：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/__init__.py                       (+2 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/risk_control.py                   (+44 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/test_risk_control.py              (+100 行 / -18 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/main_trend_strategy.py      (+41 行 / -1 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py  (+14 行)

不动：
  config/freqtrade_main_dryrun.json   （max_open_trades=2 已在 Step 1 就位）
  scripts/run_main_trend_dryrun.sh    （wrapper / 白名单 / env 检查未动）
  strategies/__init__.py
```

## 关键设计点

### 1. risk_control 升级（不破坏 Step 3 行为）

新增 `OpenPosition(symbol, side)` 数据类。

`AccountState` 字段调整：
```python
# Step 3:
open_positions_count: int = 0   # 信息字段

# Step 4:
open_positions: tuple[OpenPosition, ...] = ()
@property
def open_positions_count(self) -> int:
    return len(self.open_positions)
```
向后兼容：count 仍可读，新增 positions 容器供 gate 消费。

`RiskLimits.max_open_trades` 新字段，从 config `max_open_trades` 读（已存在，值 2）；硬上限校验 `ABSOLUTE_MAX_OPEN_TRADES = 5`。

新增 2 条 gate 规则：

```
Rule 9: 同 symbol 同 side 已有持仓 → 拒绝（v1 不允许同向加仓 / 金字塔）
Rule 10: open_positions_count >= max_open_trades → 拒绝
```

注：v1 反向开仓**不限制**（已有 BTC short 时仍允许开 BTC long），如果 Codex 觉得需要也禁止，可后续单独 patch。

### 2. position_management 包

两个 helper，纯计算 / 无副作用 / fail closed：

`aggregate_daily_realized_pnl(trades, now=UTC)`：
- 接受 `Iterable[TradeRecord]`，TradeRecord 是最小 dataclass（pair / is_open / close_date / close_profit_abs）
- 返回今天（UTC 0:00 起）已平仓订单的 realized PnL 之和
- 跳过：is_open=True / close_date=None / close_profit_abs=None / 昨天关的 / 未来时间戳异常

`extract_open_positions(trades)`：
- 接受任何具有 pair / is_open / is_short 字段的对象（duck typing；Freqtrade Trade 原生兼容）
- 返回 `tuple[OpenPosition, ...]`
- 跳过：is_open=False / 字段缺失

### 3. 策略集成

`confirm_trade_entry` 关键改动：
```python
# Step 3:
account = AccountState(
    ...
    daily_realized_pnl=Decimal("0"),                  # ← degraded
    open_positions_count=len(Trade.get_open_trades()),
)

# Step 4:
all_trades = Trade.get_trades_proxy()                  # closed + open
trade_records = [TradeRecord(...) for t in all_trades]
daily_pnl = aggregate_daily_realized_pnl(trade_records)

open_trades = Trade.get_open_trades()
open_positions = extract_open_positions(open_trades)

account = AccountState(
    ...
    daily_realized_pnl=daily_pnl,                       # ← 真实值
    open_positions=open_positions,                      # ← 真实持仓
)
```

两个 Trade 查询都包了 try/except，失败时 fail closed 到保守值（PnL=0、positions=()）+ warning log。

## 是否涉及真实交易

**否**。本轮**加强**了风控护栏（多了 2 条 gate 规则 + 真实日 PnL），未引入任何下单路径。

## 是否涉及外部分发

**否**。

## 是否涉及 API Key / token / secret

**否**。position_management 不读凭证；策略仍只通过 wrapper 注入的 env 走 Freqtrade 内部认证。

## 已知风险

### 设计层

1. **反向开仓未禁止**
   - 当前 Rule 9 只挡同向加仓（已有 BTC long 不允许新开 BTC long）
   - 反向开仓（已有 BTC long 时开 BTC short）当前**允许**
   - Codex Step 3 review 提到这是后续 step 才加的限制，所以 v1 不阻塞
   - 如果实盘期间出现"系统自己对冲"行为，可立刻补 Rule 11

2. **`Trade.get_trades_proxy()` 行为**
   - Freqtrade 文档显示这个方法在 backtest 和 live/dry-run 下行为有差异
   - 回测时返回 in-memory list（含已平仓 + 未平仓的当次回测产物）
   - dry-run/live 时从 SQLite 读
   - 当前实现两种 runmode 都能用，但**没在回测里实测过**（Step 6 才会跑）
   - 缓解：异常时 fail closed = 0，最坏情况是日 PnL 永远 = 0（回退到 Step 3 行为），不会放大风险

3. **`close_profit_abs` 的语义**
   - 假设这是 Freqtrade 在已平仓 trade 上记录的 USDT 等 stake_currency 计价的绝对盈亏
   - 包不包手续费需要 Step 6 回测后核实
   - 如果实际是"扣手续费前的毛盈亏"，日内熔断会比预期晚触发

4. **时区边界**
   - 用 UTC 0:00 作为"今天"边界
   - Binance 服务器是 UTC，Freqtrade 内部也是 UTC，一致
   - 用户在中国（UTC+8），从用户视角"今天"和"昨天"会有 8 小时偏移
   - v1 用 UTC 是合理的（量化系统不应跟人时区走），但需要在最终汇报里明确

### 工程层

5. **position_management 的 `OpenPosition` 从 risk 包导入**
   - 略反直觉：position_management 应该是"上游产出 OpenPosition 喂给 risk gate"
   - 但 OpenPosition 的"形状"由 risk gate 定义（gate 决定要什么字段）
   - 所以 position_state.py 反向 import risk → OpenPosition
   - 这是单向依赖（risk 不依赖 position_management），可以接受

6. **Strategy 仍未做单元测试**
   - Codex Step 3 review 已说"不阻塞 Step 4"
   - 当前依靠 freqtrade list-strategies 做加载性测试
   - 真实行为验证留给 Step 6 回测

### 接入层

7. **Freqtrade `Trade.get_trades_proxy` 在 dry-run 但 SQLite 还没初始化时**
   - 启动早期 SQLite 表可能未初始化
   - 当前 try/except 会捕获，fail closed 到空列表
   - 但意味着启动头几个小时 daily PnL 永远 = 0（直到第一笔订单产生 + 数据库就位）
   - 不影响功能，但在 Step 6 回测期间日 PnL 应该能立刻可用

## 建议 Codex 检查点

按重要性排序：

### 🔴 高（涉及风控正确性）

1. **反向开仓在 v1 是否真的不需要禁止**
   - 当前 Rule 9 只挡同向加仓
   - 实盘期间如果触发"持有 BTC long 时风控允许新开 BTC short"——是当前 design 还是 bug？
   - Codex 之前说"反向开仓限制"留 Step 4+，是不是其实想说"v1 也禁止"？

2. **`close_profit_abs` 是否含手续费**
   - 影响日内熔断是否准确触发
   - 需要查 Freqtrade 文档 / 源码确认
   - 如果是毛盈亏，需要在 aggregate 时减去 fee

3. **`Trade.get_trades_proxy()` 在回测中的语义**
   - 回测一次跑很多天，"今天"边界是回测的当前模拟时间还是 wall clock？
   - 当前 `aggregate_daily_realized_pnl(now=None)` 用 `datetime.now(UTC)`，wall clock
   - 回测期间这意味着所有"过去"trade 都不算"今天"，daily PnL 永远 = 0
   - **是否需要改为接收 `now` 参数，由调用方传入回测当前时间？**

### 🟡 中（涉及覆盖度）

4. **新 gate 规则的回归测试覆盖**
   - Rule 9 / Rule 10 已加 4 个测试场景
   - 是否需要补"多重违规中包含 Rule 9/10"的测试

5. **strategy 的 confirm_trade_entry try/except 包得太宽**
   - 当前 `Trade.get_trades_proxy()` 失败 → fail closed = 空列表 = daily PnL = 0
   - 严格来说，"无法读取 Trade 历史"应该 fail closed = **拒绝下单**，而不是当作"今天没亏损"
   - 当前实现某种意义是 fail open（虽然有 warning log）
   - **是否应该改为：Trade 查询失败 → confirm_trade_entry 直接 return False？**

### 🟢 低

6. **TradeRecord vs Freqtrade Trade 的 duck typing 一致性**
   - 现在 strategy 在内部把 Trade 转成 TradeRecord
   - 是否应该让 aggregate_daily_realized_pnl 直接接受 Trade（duck typing），省一层转换
   - Trade vs TradeRecord 字段名一致（pair/is_open/close_date/close_profit_abs）

7. **OpenPosition 的位置（risk vs position_management）**

---

## 测试覆盖（累计）

```
risk_control 单测                    28/28 ✅
  └─ 含 Step 4 新增 4 个 (Rule 9/10) + 3 个 (max_open_trades 配置)
position_management 单测            14/14 ✅
  └─ daily_pnl 8 + position_state 6
preflight 集成检查                   21/21 ✅
  └─ Step 4 新增 max_open_trades 校验
freqtrade list-strategies            OK ✅
  └─ MainTrendStrategy 仍可加载
wrapper 端到端                       未跑（无变化）

总场景：63 项
```

## 等待信号

- ⏳ Codex 对 Step 4 handoff 的 review，重点是 🔴 3 项
- ⏳ 如果 🔴 项 1（反向开仓）/ 🔴 项 3（now 参数）需要立刻补，**Step 4 v2 patch**
- ⏳ 如果 🔴 都通过，景森给 go 进入 **Step 5**（数据下载）
   - Codex 此前提示 Step 5 下载 K 线 + 历史 funding，时间窗 `20220601-20260501`
   - Step 5 后才能跑 Step 6 回测的 Donchian + funding 双版本

进入 Step 5 前的状态快照：
- preflight 21 项 + wrapper 2 道护栏 + risk gate 10 条规则 + strategy 4 段结构 + position_management 2 个 helpers
- 全部 dry-run + testnet，未触发任何真实交易、外部分发、新凭证
- 累计单测 / 集成测试：63 项全过
