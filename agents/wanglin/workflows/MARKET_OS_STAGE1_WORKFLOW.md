# 王林｜MARKET OS 第一阶段工作流

## 目标
把外部市场信息统一转成观察池、候选池、可执行池。

## 工作流
1. Sources
   - Binance Square
   - X / Twitter
   - Exchange Ranks

2. Raw Storage
   - 原始抓取结果进入 `data/market_os_stage1/raw/`

3. Normalize
   - 标准化进入 `data/market_os_stage1/processed/`

4. Pool Builder
   - 生成 `watch_pool.json`
   - 生成 `candidate_pool.json`
   - 生成 `execution_pool.json`

5. Downstream
   - 主报告
   - 热点异动报告
   - 后续执行层

## 默认顺序
先抓取，再标准化，再入观察池，再排序成候选池，再筛到可执行池。

## 当前阶段要求
- 先把结构搭好
- 再逐步接具体来源
- 不追求一开始就全自动实盘
