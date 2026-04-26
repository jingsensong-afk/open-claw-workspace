# 王林｜Binance Square 指定账号抓取工作流

## 默认顺序
1. 读取指定账号清单
2. 提取最近有效帖子
3. 过滤无效内容
4. 标准化为 market_signal
5. 写入 processed
6. 重建 watch / candidate / execution pool

## 当前阶段
- 先做半自动结构化抓取
- 后续再升级到持续刷新
