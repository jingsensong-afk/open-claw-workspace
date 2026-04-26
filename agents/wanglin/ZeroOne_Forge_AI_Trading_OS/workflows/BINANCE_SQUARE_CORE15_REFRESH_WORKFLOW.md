# 王林｜Binance Square Core15 刷新工作流

## 目标
让 Core15 从账号名单变成持续内容输入层。

## 默认顺序
1. 读取 Core15 名单
2. 获取最近有效帖子
3. 过滤无效帖子
4. 转成 market_signal
5. 写入 processed
6. 刷新 watch / candidate / execution pools

## 当前阶段
- 先半自动结构化刷新
- 后续升级为持续抓取
