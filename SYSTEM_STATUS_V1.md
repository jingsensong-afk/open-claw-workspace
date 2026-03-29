# 可用系统清单 V1（更新版）

更新时间：2026-03-29

## 一、已装 Skill 清单

### A. 信息采集层
1. `opennews-mcp`
- 用途：全网加密新闻搜索、AI评分、交易信号
- 当前状态：已安装，已联通
- 验证情况：HTTP 200 已验证
- 备注：依赖 6551 token

2. `opentwitter-mcp`
- 用途：X / Twitter 用户、推文、搜索、KOL 监控
- 当前状态：已安装，已联通
- 验证情况：HTTP 200 已验证
- 备注：依赖 6551 token

3. `xint-rs`
- 用途：X 舆情搜索、趋势、报告、监控
- 当前状态：已安装
- 验证情况：已安装，未深入实战验证
- 备注：需要 `X_BEARER_TOKEN`

### B. 市场 / 链上 / 预测市场 / 情绪层
4. `etherscan`
- 用途：EVM 链上基础查询
- 当前状态：已安装
- 验证情况：基础可用
- 备注：更偏基础链上查询

5. `polymarket-api`
- 用途：Polymarket 市场只读查询
- 当前状态：已安装，可用
- 验证情况：脚本已跑通
- 备注：已纳入主力工作流

6. `polymarket-analysis`
- 用途：Polymarket 市场分析（不执行）
- 当前状态：已安装，可用
- 验证情况：脚本已跑通
- 备注：偏分析型，非执行型

7. `funding-rate-scanner`
- 用途：Funding 扫描与极端费率发现
- 当前状态：已安装，可用
- 验证情况：已跑通
- 备注：已纳入主力工作流

8. `hyperliquid`
- 用途：只读 Hyperliquid 市场数据（quote / funding / OI / book / volume）
- 当前状态：已安装，可用
- 验证情况：已跑通
- 备注：已纳入主力工作流

9. `polymarket-wallet-xray`
- 用途：Polymarket 钱包画像分析
- 当前状态：已安装，可用
- 验证情况：已跑通
- 备注：已纳入主力工作流

10. `polyedge`
- 用途：预测市场相关性 / 错价分析
- 当前状态：已安装，可用
- 验证情况：已跑通
- 备注：已纳入主力工作流

11. `crypto-whale-monitor`
- 用途：鲸鱼钱包监控
- 当前状态：已安装，可用
- 验证情况：已跑通
- 备注：已纳入主力工作流

12. `market-sentiment-pulse`
- 用途：市场情绪辅助判断
- 当前状态：已安装，可用（轻量版）
- 验证情况：已跑通
- 备注：已纳入主力工作流，但只作辅助参考

13. `is-token-safe`
- 用途：token 安全性 / scam 风险评估
- 当前状态：已安装，可用
- 验证情况：补依赖后已跑通
- 备注：偏辅助型

14. `mobula`
- 用途：token / wallet / market intelligence 一体化
- 当前状态：已安装，但未接入
- 验证情况：缺 `MOBULA_API_KEY`
- 备注：后续可补齐

### C. 记忆 / 复盘层
15. `qmd-memory`
- 用途：本地混合检索、记忆搜索
- 当前状态：已安装，可用
- 验证情况：已验证
- 备注：当前 CPU 模式

16. `lancedb-memory`
- 用途：长期结构化记忆存储
- 当前状态：已安装并修复
- 验证情况：已验证
- 备注：第三方代码已本地修补

## 二、系统内置可直接使用能力
1. `summarize`
- 用途：长文 / URL / PDF 总结
- 状态：可用

2. `Agent Browser`
- 用途：JS 渲染网页、SPA 抓取、自动化浏览
- 状态：可用

## 三、当前主力可用 Skill
### 已纳入工作流主力组
- funding-rate-scanner
- hyperliquid
- polymarket-wallet-xray
- polyedge
- crypto-whale-monitor
- market-sentiment-pulse

### 其他已可用能力
- opennews-mcp
- opentwitter-mcp
- polymarket-api
- polymarket-analysis
- qmd-memory
- lancedb-memory
- summarize
- Agent Browser
- is-token-safe
- etherscan

## 四、已安装但当前不纳入主力的
- xint-rs（待更深验证）
- finance-radar（待完整验证，且有费用/API依赖）
- mobula（缺 key）
- prediction-market-aggregator（参考资料型）
- binance-pro（观察组）
- hyperliquid-trading（观察组）
- whale-watch（观察组）
- whale-tracker（观察组）
- whale-alert（观察组）

## 五、当前不可用 / 尚未补齐的关键能力
1. 标准清算热图 / 流动性热区专用数据源
- 当前未接入 Coinglass
- 已有替代方案模块 V1

2. 完整“市场是否相信”自动验证闭环
- 当前已落地 V1
- 仍需后续增强数据源与自动联动

3. mobula 一体化能力
- 缺 API key

## 六、当前系统工作状态
### 已能工作
- 新闻监控
- X 舆情监控
- Funding / OI / quote / book 读取
- 预测市场查询与相关性分析
- 预测市场钱包画像
- 鲸鱼监控
- 记忆检索与复盘
- 浏览器抓取补位
- 长文总结

### 已接入《每日投研机会雷达》工作流的 6 个主力 Skill
- funding-rate-scanner
- hyperliquid
- polymarket-wallet-xray
- polyedge
- crypto-whale-monitor
- market-sentiment-pulse

## 七、当前结论
- 系统已从“基础可运行版”升级到“有主力工作流版”
- 每日 11:00 / 15:30 雷达已具备主力 Skill 支撑
- 下一步重点不再是广泛安装，而是：
  1. 实战验证
  2. 淘汰观察组取舍
  3. 补外部 key（如 mobula）
  4. 持续升级模块与工作流
