# 王林｜MARKET OS 来源刷新工作流

## 目标
按固定顺序刷新来源，并重建 pools。

## 刷新顺序
1. Binance ranks
2. Binance futures snapshots
3. Binance Square 热门页 / 指定账号
4. X 指定账号 / 指定主题
5. 统一写入 processed
6. 重建 watch / candidate / execution pools

## 默认要求
- 每次刷新都要保留 raw 数据
- 不覆盖历史来源说明
- pool 只是当前快照，不替代 raw/processed

## 当前阶段
当前属于“半自动接入阶段”：
- Binance 公开接口可直接刷新
- Binance Square / X 仍需浏览器/结构化提取辅助
