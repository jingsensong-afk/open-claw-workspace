# 王林｜AI交易OS 第一阶段建设方案

更新时间：2026-04-24

## 第一阶段范围
只做两层：
1. 信息流层
2. 候选池层

目标不是直接自动下单，先把“信息 → 候选标的 → 可执行输入”跑通。

---

## 一、第一阶段目标
完成以下 4 件事：
- 自动抓取外部信息源
- 统一转成结构化数据
- 自动生成观察池 / 候选池 / 可执行池
- 为后续主报告、异动报告、执行层提供标准输入

---

## 二、第一阶段最小架构

### 1. 信息流层（Sources）
负责抓原始信息，不做最终交易判断。

首批信息源：
- Binance Square（广场）
- X / Twitter
- Exchange Ranks（交易所榜单）

建议抓取目标：
- 热门帖子
- 提及币种
- 看涨 / 看跌情绪
- 互动量
- 涨跌幅榜
- 热门榜
- 新币榜
- OI / Funding / 成交额异动（后续可扩）

### 2. 候选池层（Pools）
负责把原始信息转成可观察、可排序、可执行的标的池。

输出 3 层：
- Watch Pool（观察池）
- Candidate Pool（候选池）
- Execution Pool（可执行池）

---

## 三、目录结构

建议固定新增：

- `agents/wanglin/data/market_os_stage1/raw/`
- `agents/wanglin/data/market_os_stage1/processed/`
- `agents/wanglin/data/market_os_stage1/pools/`
- `agents/wanglin/workflows/`
- `agents/wanglin/schemas/`

说明：
- `raw/`：原始抓取结果
- `processed/`：标准化后的结构化结果
- `pools/`：观察池 / 候选池 / 可执行池
- `workflows/`：阶段工作流说明
- `schemas/`：字段结构定义

---

## 四、第一阶段文件清单

### 规则 / 方案
- `rules/AI_TRADING_OS_STAGE1_PLAN.md`

### Workflow
- `workflows/MARKET_OS_STAGE1_WORKFLOW.md`

### Schema
- `schemas/market_signal.schema.json`
- `schemas/pool_item.schema.json`

### Pools
- `data/market_os_stage1/pools/watch_pool.json`
- `data/market_os_stage1/pools/candidate_pool.json`
- `data/market_os_stage1/pools/execution_pool.json`

---

## 五、第一阶段统一字段（核心）

### A. 原始市场信号字段
- `source`：来源（binance_square / x / binance_rank / okx_rank ...）
- `source_type`：来源类型（post / rank / signal / trend）
- `symbol`：币种
- `quote`：计价币（USDT）
- `narrative`：叙事标签
- `sentiment`：bullish / bearish / neutral
- `engagement_score`：互动强度
- `velocity_score`：热度增速
- `price_change_pct`：价格变化
- `volume_score`：成交活跃度
- `oi_change_pct`：OI变化（可空）
- `funding_rate`：Funding（可空）
- `timestamp`
- `raw_ref`：原始数据引用

### B. 池子字段
- `symbol`
- `narrative_score`
- `sentiment_score`
- `attention_score`
- `liquidity_score`
- `volatility_score`
- `execution_score`
- `risk_level`
- `status`：watch / candidate / executable
- `reason`
- `invalid_condition`
- `updated_at`

---

## 六、第一阶段默认工作流
1. 抓取原始信息源
2. 落盘 raw 数据
3. 做统一标准化
4. 写入 processed
5. 更新 watch pool
6. 对 watch pool 打分生成 candidate pool
7. 按执行标准筛出 execution pool
8. 后续主报告 / 异动报告从 pool 读取输入

---

## 七、当前实现状态
- 规则层：未落地 → 本文件开始落地
- schema 层：未落地
- pool 层：未落地
- source 抓取层：未落地为统一机制
- 与主报告联动：未接通

---

## 八、第一阶段验收标准
第一阶段完成，至少满足：
1. 有清晰目录结构
2. 有统一 schema
3. 有 3 个标准池文件
4. 能把至少 2 类外部来源写入观察池
5. 候选池有基础评分逻辑
6. 可执行池有最小筛选标准
7. 后续可被主报告 / 异动报告直接调用

---

## 九、边界
第一阶段不做：
- 实盘自动下单
- 自动发帖
- 完整量化策略回测
- 高复杂度多因子模型

第一阶段只解决：
**信息抓取 → 候选标的生成 → 可执行输入标准化**
