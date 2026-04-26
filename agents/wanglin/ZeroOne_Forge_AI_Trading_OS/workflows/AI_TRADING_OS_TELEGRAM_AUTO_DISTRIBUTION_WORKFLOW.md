# 王林｜AI交易OS Telegram 自动分发工作流

## 目标
把第五层摘要输出，接成 Telegram 自动分发链路。

## 默认顺序
1. 读取 distribution_summary_v1.json
2. 读取 telegram_distribution_text_v1.txt
3. 生成最终 Telegram 文本
4. 后续可接 Telegram cron / announce 机制

## 当前阶段
- 先完成可分发文本
- 后续再正式接自动发送
