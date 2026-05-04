# Day 5 Pre-Review · MainTrendStrategy v1

**类型**：pre_review（动手前预审，等待 Codex 反馈和景森确认）
**日期**：2026-05-05（计划日期）
**作者**：Claude Code
**状态**：📝 待 Codex review · 待景森确认 · 暂未实施

---

## 本轮目标

实现 **MainTrendStrategy v1**——双系统架构中"Main 主系统"的第一版策略，专注 BTC/ETH 等主流币的中频趋势捕捉。这是把王林 OS 第四层"执行层"从"能下单"升级到"能根据策略思考下单"的关键一步。

### 策略核心逻辑（v1）

```
每根小时 K 线收盘时：

[1] 信号层（Donchian 突破）
    - 上轨 = 过去 N 根小时 K 线最高价（默认 N=20）
    - 下轨 = 过去 N 根小时 K 线最低价
    - 收盘价突破上轨 → 多头信号
    - 收盘价跌破下轨 → 空头信号

[2] 过滤层（资金费率反拥挤）
    - 多头信号时：funding rate ≤ +0.05% 才放行
    - 空头信号时：funding rate ≥ -0.05% 才放行

[3] 风控层（强制约束，策略不可绕过）
    - 单笔风险 ≤ 1% 总资金
    - 日内累计亏损 ≥ 3% 触发熔断停盘
    - 杠杆 ≤ 5x
    - 必带止损（初始 = 通道下轨 或 2×ATR，取较紧）
    - 移动止损（trailing = 3×ATR）

[4] 仓位计算
    position_size = (account_balance × risk_pct) / stop_loss_distance_pct
    若计算结果违反杠杆上限 → 取较小值

[5] 执行
    通过 Freqtrade 框架触发实际下单（dry-run 阶段不真下）
```

### 标的范围

- BTC/USDT:USDT (USDⓈ-M Futures)
- ETH/USDT:USDT (USDⓈ-M Futures)
- ⚠️ **不**适用于山寨 / 新币 / 热点币（那部分留给 Week 2 的 ExperimentalAltStrategy）

---

## 预计改动文件

```
新增（拟）：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/__init__.py
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/main_trend_strategy.py
    └── 实现 IStrategy 子类，含 populate_indicators / populate_entry_trend / populate_exit_trend / custom_stoploss
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/__init__.py
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/risk_control.py
    └── 独立风控模块（被 strategy 调用，policy 不可绕过）
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/config/freqtrade_main_dryrun.json
    └── Freqtrade 配置（dry_run=true, exchange=binance, sandbox=true 指向 testnet）
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/handoffs/2026-05-05_day5_main_trend_handoff.md
    └── 实施完成后的最终交接

可能新增：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/strategies/_indicators.py
    └── Donchian 通道、ATR、funding rate fetcher 等可复用工具

可能修改：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/README.md
    └── 入口索引补一个 strategies/ 章节

不动：
  既有 rules/ workflows/ schemas/ templates/ 全部保持原样
  既有 scripts/ 中的 testnet 测试脚本保持原样
```

---

## 预计运行命令

```bash
# 1. 历史回测（验证策略期望）
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/freqtrade backtesting \
  --strategy MainTrendStrategy \
  --config agents/wanglin/ZeroOne_Forge_AI_Trading_OS/config/freqtrade_main_dryrun.json \
  --timerange 20240101-20251231

# 2. 测试网 dry-run（验证执行链路）
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/freqtrade trade \
  --strategy MainTrendStrategy \
  --config agents/wanglin/ZeroOne_Forge_AI_Trading_OS/config/freqtrade_main_dryrun.json
```

---

## 预计产出文件

- `data/market_os_stage1/calibration_layer/main_trend_backtest_<ts>.json`
  - 回测报告（夏普、最大回撤、胜率、单笔最大亏损、单笔最大盈利、连续亏损次数）
- 终端 / Freqtrade 自带数据库的 dry-run 交易记录

---

## 是否涉及真实交易

**否**。

- 配置文件硬编码 `dry_run: true`
- 配置文件 exchange `sandbox: true`（testnet）
- 历史回测仅用历史 K 线数据，不发任何下单请求
- ⚠️ 但需要 Codex 在 review 时**双重确认配置文件中没有任何会导致真实下单的字段**

---

## 是否涉及外部分发

**否**。Freqtrade 内置 Telegram / Webhook 通知，但 v1 默认全部关闭。如果未来要开 Telegram 通知，会单独走 handoff 流程。

---

## 是否涉及 API Key / token / secret

**是 · 但只是复用**。沿用 Day 4 已建立的 `agents/wanglin/.binance_futures_api.testnet.json`，**不新增任何 key**。Freqtrade 配置中 key 不会硬编码，而是通过环境变量或读取既有 JSON。

---

## 已知风险

### 设计层

1. **突破策略本质胜率低**（35-45% 经验值）。如果回测显示在 BTC/ETH 2024-2025 时段无法做出正期望，**需要回到设计阶段调整**，不能强行进入实盘评估。
2. **资金费率 ±0.05% 阈值是经验值**，未在 BTC/ETH 历史 funding rate 分布上验证。可能太松（拥挤侧仍能开仓）或太紧（错过大趋势启动早期）。
3. **风控数值（1% / 3% / 5x）对 10 万美金的具体行为未模拟**。需要回测确认日 3% 熔断在历史最差日内是否被频繁触发（频繁熔断 = 策略不稳定）。
4. **多空对称性问题**：突破策略经典做法是双向（多空对称），但 Codex 可能建议 v1 先只做多头（因为 BTC/ETH 长期趋势向上，做空赔率不对称）。**需要明确决定**。

### 工程层

5. **Freqtrade 默认风控可能与我们的硬约束冲突**。例如 Freqtrade 自带的 `stoploss` 是固定百分比，与我们基于 ATR 的动态止损可能冲突。需要明确覆盖优先级——硬风控模块应高于 Freqtrade 默认。
6. **多策略并行时全局风控聚合不明**：日 3% 熔断是单策略级还是账户级？如果未来 Main + Experimental 同时跑，账户级聚合需要单独实现。
7. **Funding rate 数据获取**：Freqtrade 不原生支持 funding rate 作为指标。需要在 `populate_indicators` 中通过 ccxt 或自定义 HTTP 调用拉取。回测时还需要历史 funding rate 数据（Binance 提供 `/fapi/v1/fundingRate` 历史接口，需要确认数据完整性）。
8. **DOGE 测试网精度问题已暴露**（Day 4 见）。BTC/ETH 不应有同类问题（precision 高、流动性大），但仍需在 v1 第一次下单前**显式查询 MARKET_LOT_SIZE** 确认。
9. **Hyperopt 参数搜索如果加入**，可能会"优化"掉硬风控参数。需要白名单：哪些参数可以让 Hyperopt 调（如 Donchian 周期），哪些**绝对不能**（单笔 1% / 杠杆 5x）。

### 合规层

10. **dry-run 也会调用 Binance API（行情接口）**，虽然不动真钱但有真实流量。需要确保配置文件中 `dry_run: true` 不能被命令行参数覆盖（或至少有明显警告）。
11. **回测样本期偏好**：2024-2025 是 BTC ETF 牛市行情，趋势策略天然好看。**Codex 应建议在回测中纳入 2022 熊市段** 验证抗回撤能力。

### 数据层

12. **K 线历史数据下载**：Freqtrade 自带 `freqtrade download-data` 命令，但需要确认数据来源（Binance USDⓈ-M futures 而非现货）和时间区间完整性。
13. **数据质量**：跳空 / 停盘 / 深度等异常需要在回测时过滤或标记，否则结果不可信。

---

## 建议 Codex 检查点

按重要性排序：

### 🔴 高优先级（涉及风控 / 安全）

1. **强制风控的实现位置**：写在 strategy 文件里（容易被未来开发者覆盖）还是独立 `risk_control.py` 模块（更安全但需要 strategy 调用）？**建议后者**，并要求 Codex 确认 strategy 必须显式 import + 调用风控函数才能下单。
2. **leverage cap 的多层实现**：Strategy 配置 vs Freqtrade config vs Binance 端预设。**建议三层都设置，最严的生效**。Codex 是否同意此原则？
3. **必带止损的强制性**：Freqtrade 是否有原生强制止损选项？还是要在 `custom_stoploss` 里硬编码"无止损 = 拒绝下单"？
4. **`dry_run: true` 不可被覆盖**：Codex 建议如何防止命令行 `--dry-run false` 误用？是否需要 wrapper 脚本预检？

### 🟡 中优先级（涉及策略正确性）

5. **R 单位仓位计算公式**：
   ```
   position_size = (account_balance × risk_pct) / stop_loss_distance_pct
   ```
   是否正确？需要考虑滑点 buffer 吗？
6. **日 3% 熔断的聚合层级**：单策略 vs 账户级——v1 先做单策略级 OK 吗？账户级留 Week 3 多策略并行时再加？
7. **多空对称性**：v1 是否做空？如果只做多，需要在策略文件 docstring 里明确标注。
8. **回测样本必须包含 2022 熊市**：建议时间范围 `20220101-20251231` 而不是 `20240101-20251231`。

### 🟢 低优先级（涉及工程细节）

9. **Funding rate 抓取实现**：在 strategy 内联调用还是独立 fetcher 模块？
10. **回测数据下载命令** 是否在 handoff 中写明，方便 Codex 复现？
11. **是否需要 Pre-flight 检查脚本**：开始 dry-run 前自动验证 base_url=testnet + dry_run=True + leverage<=5x，缺一项就拒绝启动？

---

## 决策待定（需要景森拍板）

在动手前希望景森确认以下设计选择：

- **A. 多空双向 vs 仅多头**：v1 是否做空？
  - 倾向：v1 仅做多（BTC/ETH 长期向上偏置，做空赔率不对称）。Week 3 评估后再决定是否加做空。
- **B. 回测时间范围**：
  - 倾向：`20220601-20260501`（含 LUNA 崩盘 / FTX 暴雷 / 2024 ETF 大涨 / 2025 各类波动）。
- **C. Donchian 周期**：
  - 倾向：起步 20，hyperopt 时在 [10, 15, 20, 30, 50] 中搜索。
- **D. 资金费率阈值**：
  - 倾向：起步 ±0.05%，hyperopt 时在 [0.02%, 0.05%, 0.10%] 中搜索。
- **E. 是否启用 Telegram 通知（dry-run 阶段）**：
  - 倾向：启用（养成监控习惯），通知发到景森私人 Telegram bot。如果暂无 bot，先关闭，等 bot 配好再开。

---

## 不动业务代码

本文件**只是设计预审**——动手前的方案。不会触发任何代码改动。等待：

1. Codex 写 `2026-05-05_day5_main_trend_codex_review.md` 提反馈
2. 景森回答上述 5 个决策问题（A-E）
3. 两者都到位后，Claude 才开始实施

期间如果 Codex 发现严重风险或景森的决策与预审有大出入，**Pre-review 文件可能 v2 重写**，整个流程重新走一遍。
