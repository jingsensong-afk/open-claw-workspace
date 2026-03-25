# ZeroOne Venture 第一版可工作系统 V1

更新时间：2026-03-12

## 一、系统目标
围绕重大事件与热点事件/话题，形成一套可持续运行的投研交易工作系统：
- 收集信息
- 分析逻辑
- 验证市场是否相信
- 识别资金流向
- 输出跨市场交易机会
- 持续复盘升级

## 二、当前已具备的底座
### 1. 安全层
- OpenClaw 已升级到较新版本
- tool policy 已收敛
- 基础安全检查已完成

### 2. 记忆层
- `MEMORY.md`：长期记忆
- `memory/YYYY-MM-DD.md`：每日记录
- `qmd-memory`：本地检索记忆
- `lancedb-memory`：结构化长期记忆

### 3. 身份与协作层
- 身份：ZeroOne Venture 首席投研交易官
- 协作原则：时效优先、主动汇报、遇问题及时探讨
- Skill 原则：不臃肿、不重叠

## 三、当前已落地模板
1. `templates/INVESTMENT_RESEARCH_FRAMEWORK_V1.md`
2. `templates/EVENT_ANALYSIS_TEMPLATE_V1.md`
3. `templates/HOT_EVENT_MAPPING_POOL_TEMPLATE_V1.md`
4. `templates/CRYPTO_9D_SCORECARD_V1.md`
5. `templates/DAILY_OPPORTUNITY_RADAR_V1.md`

## 四、当前已落地模块 / 工作流
1. `WORKFLOW_DAILY_RADAR_V1.md`
- 每日投研机会雷达工作流（6个主力 Skill 接入版）

2. `modules/LIQUIDITY_HEATMAP_ALT_V1.md`
- 清算热图 / 流动性热区替代分析模块 V1

3. `modules/MARKET_BELIEF_VALIDATION_CHAIN_V1.md`
- 市场是否相信自动验证链 V1

## 五、当前可用主力 Skill
### 信息采集 / 舆情
- `opennews-mcp`
- `opentwitter-mcp`
- `xint-rs`

### 记忆 / 检索
- `qmd-memory`
- `lancedb-memory`

### 链上 / 市场 / 预测市场 / 情绪
- `etherscan`
- `polymarket-api`
- `polymarket-analysis`
- `funding-rate-scanner`
- `hyperliquid`
- `polymarket-wallet-xray`
- `polyedge`
- `crypto-whale-monitor`
- `market-sentiment-pulse`

### 辅助能力
- `summarize`
- `Agent Browser`
- `is-token-safe`

## 六、每日运行方式（V1）
### 11:00 主报告
按 `WORKFLOW_DAILY_RADAR_V1.md` 执行：
1. 新闻 / 热点
2. X 舆情
3. Funding / OI / book
4. 预测市场钱包与相关性
5. 鲸鱼监控
6. 情绪辅助
7. 输出资金流向、可交易标的、观察机会、风险提示

### 15:30 补充报告
- 跟踪当日新增重大事件与市场变化
- 补充新的交易机会 / 观察机会

### 逾期任务
- 默认不持续汇报
- 一旦出现逾期任务，启用 2 小时进展汇报机制

## 七、当前 cron 结构
### 常开
- `zov-rule-daily-1100`
- `zov-rule-daily-1530`
- `growth-panel:v1-review`

### 按需开启
- `zov-overdue-progress-2h`

## 八、当前可工作系统的实际边界
### 已能工作
- 日报框架已成型
- 关键模板已成型
- 关键工作流已成型
- 一批主力 Skill 已可调用
- 记忆、复盘、定时机制已建立

### 仍在后续升级中的部分
- `mobula` 未接入（缺 API key）
- 清算热图仍为替代方案，不是标准热图
- 市场是否相信验证链为 V1，仍需继续增强
- 部分技能仍需在实战中验证长期价值并做淘汰

## 九、当前结论
这一版系统已经满足“第一版可工作系统”的定义：
- 有模板
- 有工作流
- 有定时机制
- 有可用 Skill
- 有记忆与复盘能力
- 可以从明日开始按 11:00 / 15:30 节奏持续运行

后续重点不再是“从零搭建”，而是：
1. 用起来
2. 在实战中验证
3. 淘汰低价值部分
4. 逐步升级成 ZeroOne Venture 独家的实战投研交易系统
