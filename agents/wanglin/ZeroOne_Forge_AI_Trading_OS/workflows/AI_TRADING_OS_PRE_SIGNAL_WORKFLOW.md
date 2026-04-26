# 王林｜AI交易OS 前置信号层工作流

## 默认顺序
1. 收集早期讨论 / 轻度异动 / 新币边缘信号
2. 标记为 pre_signal
3. 写入 processed
4. 优先进入 watch pool
5. 后续由更多共振决定是否升 candidate / execution
