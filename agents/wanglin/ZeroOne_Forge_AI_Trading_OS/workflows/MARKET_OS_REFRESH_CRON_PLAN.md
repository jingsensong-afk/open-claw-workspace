# 王林｜MARKET OS 刷新 Cron 方案

## 目标
让 Binance + X 信息流层按固定节奏刷新。

## 建议 cron
1. `market-os-ranks-refresh`
   - 周期：每 15 分钟
   - 作用：刷新 Binance 榜单 / 异动层

2. `market-os-square-refresh`
   - 周期：每 30 分钟
   - 作用：刷新 Binance Square 层

3. `market-os-x-refresh`
   - 周期：每 30 分钟
   - 作用：刷新 X 层

4. `market-os-full-refresh`
   - 周期：每 60 分钟
   - 作用：统一刷新 raw → processed → pools

## 当前落地状态
- 已生成刷新脚本：`scripts/refresh_market_os_stage1.sh`
- 下一步可直接接入 cron 调度


## Full-chain refresh
- 已新增脚本：`scripts/refresh_market_os_full_chain.sh`
- 该脚本会依次刷新 1-6 层，形成真正的 full-chain refresh。
