# 投研交易 Skill 正式基线 V1

更新时间：2026-03-29

## 一、系统全部 Skill（当前主仓库）
1. agent-browser
2. binance-pro
3. crypto-whale-monitor
4. etherscan
5. finance-radar
6. find-skills
7. funding-rate-scanner
8. github
9. hyperliquid
10. hyperliquid-trading
11. is-token-safe
12. lancedb-memory
13. market-sentiment-pulse
14. mobula
15. notion
16. obsidian
17. opennews-mcp
18. opentwitter-mcp
19. _paused_proactive-agent
20. _paused_self-improving-agent
21. polyedge
22. polymarket-analysis
23. polymarket-api
24. polymarket-wallet-xray
25. prediction-market-aggregator
26. qmd-memory
27. summarize
28. tencentcloud-lighthouse-skill
29. tencent-docs
30. weather
31. xint-rs
32. aicoin-account
33. aicoin-freqtrade
34. aicoin-hyperliquid
35. aicoin-market
36. aicoin-trading
37. okx-cex-market

## 二、投研交易相关 Skill 全量
1. aicoin-account
2. aicoin-freqtrade
3. aicoin-hyperliquid
4. aicoin-market
5. aicoin-trading
6. agent-browser
7. binance-pro
8. crypto-whale-monitor
9. etherscan
10. finance-radar
11. funding-rate-scanner
12. hyperliquid
13. hyperliquid-trading
14. is-token-safe
15. lancedb-memory
16. market-sentiment-pulse
17. mobula
18. okx-cex-market
19. opennews-mcp
20. opentwitter-mcp
21. polyedge
22. polymarket-analysis
23. polymarket-api
24. polymarket-wallet-xray
25. prediction-market-aggregator
26. qmd-memory
27. xint-rs

## 三、当前正式主干核心（建议长期保留）
1. aicoin-hyperliquid
2. aicoin-market
3. binance-pro
4. crypto-whale-monitor
5. etherscan
6. funding-rate-scanner
7. hyperliquid
8. market-sentiment-pulse
9. opennews-mcp
10. opentwitter-mcp
11. polyedge
12. polymarket-analysis
13. polymarket-api
14. polymarket-wallet-xray
15. xint-rs

## 四、保留观察
1. aicoin-account
2. aicoin-freqtrade
3. aicoin-trading
4. agent-browser
5. finance-radar
6. hyperliquid-trading
7. is-token-safe
8. lancedb-memory
9. mobula
10. okx-cex-market
11. prediction-market-aggregator
12. qmd-memory

## 五、本轮已处理
- 已删除重复 Skill：whale-alert、whale-tracker、whale-watch
- 已同步王林仓库 skills 与主仓库一致

## 六、升级状态说明
- 已核对本地已安装版本信息。
- 未执行批量升级；ClawHub 批量 update 在检查阶段遇到 registry/slug 问题（例如 tavily-search not found），因此本轮先不做自动升级。
- 当前建议：后续单独做一次“逐项可升级性核查”，不要直接全量 update。
