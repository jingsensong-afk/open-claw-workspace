# 王林｜AI交易OS Telegram 自动分发工作流

## 目标
把第五层新主链摘要输出，接成 Telegram 自动分发链路。

## 默认顺序
1. 读取 distribution_summary_v2.json
2. 结合当前最终策略单或交易事件生成 Telegram 文本
3. 生成最终 Telegram 文本
4. 后续可接 Telegram cron / announce 机制

## 当前阶段
- 默认基于新主链最终结果分发
- 不再依赖 v1 摘要文件
