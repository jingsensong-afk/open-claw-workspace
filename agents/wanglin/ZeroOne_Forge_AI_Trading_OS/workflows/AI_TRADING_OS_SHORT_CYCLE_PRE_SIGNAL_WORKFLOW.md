# 王林｜AI交易OS 短周期前置信号工作流

1. 抓取 15m / 1h 放量异动
2. 抓取 OI / Funding 快速变化
3. 合并为 pre-signal 数据源
4. 写入 processed market signals
5. 重建 watch / candidate / execution pools
6. 标记为 short_cycle_pre_signal 供后续验证
