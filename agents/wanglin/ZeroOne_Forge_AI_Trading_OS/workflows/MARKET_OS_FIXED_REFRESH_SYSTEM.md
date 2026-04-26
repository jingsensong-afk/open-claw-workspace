# 王林｜MARKET OS 固定刷新系统

## 目标
把 Binance + X 信息流层从结构骨架推进成固定刷新系统。

## 刷新频率（当前建议）
- Binance 榜单 / 异动：15~30 分钟
- Binance Square：30~60 分钟
- X 账号 / 主题：30~60 分钟

## 固定刷新顺序
1. Binance 榜单 4项
2. Binance 公告 / 上线 / 新合约
3. Binance Square 热门 / 指定账号 / 社区高频讨论
4. X 指定账号 / 指定主题 / 热门叙事 / 提及增速 / 关键币种扩散
5. 写入 raw
6. 写入 processed
7. 重建 pools
8. 更新 last_verified_at

## 演进原则
- 先稳定刷新，再提频
- 先用真实抓取替代 seed，再逐步清理 seed
- 先保留原始留痕，再做评分和筛选
