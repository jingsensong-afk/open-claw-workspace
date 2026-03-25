# 每日投研机会雷达工作流 V2（完整 Skill 层优化版）

更新时间：2026-03-17

## 一、目标
在原有投研雷达基础上，将**原本已匹配任务的基础 Skill**与**后续新增 Skill**统一纳入同一工作流，围绕“更高质量完成投研任务”进行重组，而不是用新增 Skill 替代原有 Skill。

该工作流用于：
- 发现重大事件与热点事件
- 跟踪叙事扩散与舆情变化
- 验证资金流向与市场结构
- 补充预测市场与钱包行为证据
- 输出可交易机会、观察清单、风险提示

## 二、设计原则
1. 新增 Skill 是增强，不是替代
2. 所有匹配任务的 Skill 应先并入完整工作流，再按任务重排顺序
3. 先形成完整证据链，再在实战中优胜劣汰
4. 工作流优化目标永远是：更高质量完成任务，而不是追求“主力 Skill”概念本身

## 三、CoinOS 新增 Skill 接入规则（2026-03-17 生效）

### 3.1 接入定位
- CoinOS 作为“新增 Skill 层”并入现有体系，定位为**补强源**，不是替代源。
- 当前阶段仅用于投研数据增强，**不进入交易执行链路**。

### 3.2 本阶段启用范围
- 启用：`aicoin-market`（行情/结构/新闻/快讯/项目线索）、`aicoin-hyperliquid`（HL 大户/清算/OI/交易员行为）
- 条件启用：`aicoin-freqtrade`（仅策略研究与回测框架参考，不部署实盘）
- 禁用：`aicoin-trading`（不开仓、不平仓、不做任何交易执行）

### 3.3 调用优先级（并入后重组）
- 市场结构层：`funding-rate-scanner`、`hyperliquid` 为主；CoinOS 对应能力作为并行复核与缺口补位。
- 信息发现层：`opennews-mcp`、`opentwitter-mcp` 为主；`aicoin-market` 的 news/newsflash/twitter 作为交叉验证源。
- 输出口径：若主源与补强源冲突，必须在结论中标注“冲突点 + 当前采用口径 + 待验证项”。

### 3.4 质量验收（每日雷达）
新增 Skill 接入后，按以下三项评估是否提升任务完成质量：
1. 证据覆盖率（事件/舆情/结构/资金/预测市场）
2. 事件→标的映射速度（是否更快形成观察池）
3. 触发/失效条件清晰度（是否可执行、可复核）

## 四、当前纳入工作流的 Skill

### A. 信息发现层
1. `opennews-mcp`
- 用途：新闻、快讯、热点、事件源发现

2. `opentwitter-mcp`
- 用途：X / Twitter 舆情、KOL、扩散路径、话题热度

3. `summarize`
- 用途：对长文、链接、资料做快速提炼

4. `Agent Browser`
- 用途：补抓 JS 渲染页面、特殊网页、结构化抓取失败时的浏览器补位

### B. 市场结构层
5. `funding-rate-scanner`
- 用途：Funding 极值、费率异常、潜在挤压机会

6. `hyperliquid`
- 用途：quote / funding / OI / volume / book 等市场结构数据

### C. 预测市场层
7. `polymarket-api`
- 用途：预测市场只读查询、相关事件市场搜索

8. `polymarket-analysis`
- 用途：市场分析补充、事件概率解释

9. `polymarket-wallet-xray`
- 用途：重点钱包画像、行为结构、是否存在 edge

10. `polyedge`
- 用途：预测市场间相关性、错价与偏差分析

### D. 链上与大额资金层
11. `crypto-whale-monitor`
- 用途：鲸鱼钱包、大额异动、链上资金线索

### E. 情绪辅助层
12. `market-sentiment-pulse`
- 用途：轻量情绪辅助，仅作参考，不独立下结论

## 四、11:00 主报告执行顺序

### 第一步：新闻 / 热点发现
优先调用：
- `opennews-mcp`
- `summarize`
- `Agent Browser`（必要时）

输出：
1. 今日新增重大事件
2. 今日新增热点事件
3. 事件类型（宏观 / 政策 / 加密 / AI / 地缘 / 公司 / 产业链）

### 第二步：舆情与叙事扩散
优先调用：
- `opentwitter-mcp`
- `summarize`

输出：
1. X 上是否形成扩散
2. 哪些 KOL / 账号在推动叙事
3. 叙事当前处于：起势 / 扩散 / 高热 / 分歧

### 第三步：市场结构与资金面验证
优先调用：
- `funding-rate-scanner`
- `hyperliquid`

输出：
1. Funding 是否异常
2. OI 是否抬升/回落
3. 量能是否放大
4. 是否存在挤空 / 挤多结构
5. 核心资产（BTC/ETH）市场状态

### 第四步：预测市场验证
优先调用：
- `polymarket-api`
- `polymarket-analysis`
- `polymarket-wallet-xray`
- `polyedge`

输出：
1. 是否存在对应事件市场
2. 概率是否显著变化
3. 是否存在预测市场错价/edge
4. 是否有重点钱包在提前行动

### 第五步：鲸鱼与链上大额资金验证
优先调用：
- `crypto-whale-monitor`

输出：
1. 是否有大额地址异动
2. 是否出现与事件相关的新线索
3. 是否支持或反驳前述判断

### 第六步：情绪辅助修正
优先调用：
- `market-sentiment-pulse`

输出：
1. 情绪偏多 / 偏空 / 中性
2. 是否与市场结构一致

## 五、15:30 补充报告执行顺序
1. `opennews-mcp`：补抓新增新闻 / 快讯 / 产业催化
2. `opentwitter-mcp`：观察叙事是否继续扩散或转弱
3. `funding-rate-scanner`：查看 funding 是否出现新异动
4. `hyperliquid`：OI / volume / funding / book 是否有显著变化
5. `polymarket-api` / `polymarket-analysis`：事件市场概率是否变化
6. `polymarket-wallet-xray` / `polyedge`：预测市场钱包与错价是否出现新增线索
7. `crypto-whale-monitor`：是否出现新的大额资金行为
8. `market-sentiment-pulse`：情绪补充参考
9. `summarize` / `Agent Browser`：需要时用于补资料

## 六、标准输出结构
1. 今日新增重大事件 / 热点事件
2. 叙事扩散情况
3. 新闻 / 宏观触发响应（如出现异常波动，自动调用《modules/NEWS_MACRO_TRIGGER_RESPONSE_V1.md》）
4. 市场是否相信（价格 / 量能 / OI / funding / 预测市场 / 钱包行为）
5. 资金流向判断
6. 跨市场联动判断（遇到宏观/商品/多市场共振场景，自动调用《modules/CROSS_MARKET_LINKAGE_MONITOR_V1.md》）
7. 链上 / 鲸鱼 / 现货资金验证（遇到高波动资产上涨/下跌真实性判断，自动调用《modules/ONCHAIN_WHALE_SPOT_FLOW_VALIDATION_V1.md》）
8. 清算热图 / 流动性热区 / 短周期拐点预警（遇到高波动资产异动，自动调用《modules/LIQUIDITY_HEATMAP_ALT_V1.md》与《modules/SHORT_TERM_TURNING_POINT_ALERT_RULES_V1.md》）
9. OI + 多空持仓比完整验证（自动调用《modules/OI_LONGSHORT_RATIO_VALIDATION_V1.md》）
10. Funding / 情绪 / 恐慌贪婪统一面板（自动调用《modules/FUNDING_SENTIMENT_FEAR_GREED_PANEL_V1.md》）
11. 产业瓶颈 / 价格错配（如适用；凡涉及产业链、供需错配、稀缺资源、价格重估、预期差的主题，必须自动调用《modules/INDUSTRY_BOTTLENECK_MISPRICING_V1.md》）
12. Token / 地址 / 热门信息一体化验证（自动调用《modules/TOKEN_ADDRESS_HOTINFO_INTEGRATION_V1.md》）
13. 加密市场：主交易标的 / 高弹性标的 / 观察标的
14. 美股市场：主交易标的 / 高弹性标的 / 观察标的
15. 港股市场：主交易标的 / 高弹性标的 / 观察标的
16. 大宗商品：主交易标的 / 观察标的
17. 预测市场：主交易标的 / 观察标的
18. 触发条件
19. 失效条件（默认内嵌《modules/INVALIDATION_FIRST_MECHANISM_V1.md》）
20. 当前主导变量 / 最强信号 / 次强信号 / 被降级信号（默认内嵌《modules/MULTI_SIGNAL_PRIORITY_AGGREGATION_V1.md》）
21. 当前置信度（高 / 中 / 低；默认内嵌《modules/CONFIDENCE_GRADING_AND_OUTPUT_V1.md》）
22. 时间维度分层（短线 / 日内 / 波段 / 中线；默认内嵌《modules/TIMEFRAME_LAYERING_MECHANISM_V1.md》）
23. 风险提示

## 七、使用要求
1. 不能只因新增 Skill 存在，就忽略原本已匹配任务的基础 Skill
2. 不能只做方向判断，必须尽量落到具体标的
3. 不能只给概念，必须尽量给出数据支撑与条件判断
4. 若某个 Skill 当前不可用，应记录并用相邻能力补位，而不是直接让整层消失
5. 面对实盘问题，默认优先遵守《modules/REALTIME_MARKET_ANALYSIS_FIRST_V1.md》
6. 回答前先判断主场景，并按《modules/SCENARIO_BASED_ANALYSIS_ROUTING_V1.md》选择分流路径
7. “市场是否相信”验证默认按《modules/MARKET_BELIEF_HOURLY_RESPONSE_CHAIN_V1.md》优先提供小时级状态（当轮任务可用时）

## 八、当前结论
《每日投研机会雷达工作流 V2》代表的是：
- 基础 Skill 层 + 新增 Skill 层 的统一编组
- 在完整能力之上做任务导向的工作流优化
- 后续再通过实战进行优胜劣汰

这才符合 ZeroOne Venture 的系统沉淀路径。
