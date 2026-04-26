# 王林｜AI交易OS 来源接入计划

更新时间：2026-04-24

## 目标
把当前“人工提取 + 公开接口”阶段，逐步升级为“可重复执行的半自动来源接入”。

---

## 当前来源状态
### 已接入
- Binance 24h 涨幅榜
- Binance 24h 跌幅榜
- Binance 24h 成交额榜
- Binance Futures funding snapshot
- Binance Futures open interest snapshot
- Binance Square 研究样本（结构化录入）
- X / AI交易访谈主题样本（结构化录入）

### 未完成
- Binance Square 热门页持续抓取
- Binance Square 指定账号持续抓取
- X 指定账号 / 指定主题持续抓取
- 更完整的 futures 异动层（OI变化率、Funding排序、成交额异动）

---

## 第一优先级来源
### 1. Binance Square
目标：
- 热门帖子
- 指定账号帖子
- 看涨 / 看跌标签
- 实盘交易组件
- 互动量
- 提及币种

接入方式：
- Browser 抓取优先
- 抓到后统一转成 market_signal

### 2. X / Twitter
目标：
- 指定账号
- 指定主题
- 热门叙事词
- 提及币种
- 互动量

接入方式：
- Browser / 现有 skill / API 三选一
- 当前阶段优先可持续抓取，不强求最优实现路径

### 3. Binance Futures 异动层
目标：
- Funding 排序
- OI 排序
- 成交额异常
- 新币 / 热门币优先监控

接入方式：
- 公开接口优先

---

## 统一接入原则
1. 先能持续抓，再追求优雅。
2. 先保证结构化落盘，再追求高复杂分析。
3. 来源层不直接下结论，只负责提供标准化信号。
4. 所有来源统一写入：
   - `raw/`
   - `processed/`
   - `pools/`

---

## 下一阶段动作
1. 增加 Binance Square 热门页抓取入口
2. 增加 Binance Square 指定账号抓取入口
3. 增加 X 指定账号 / 主题抓取入口
4. 增加 Binance Futures 异动抓取入口
5. 重建 candidate / execution pool


## X 主线当前已落地的结构
- 指定账号入口：`raw/x_account_targets_v1.json`
- 指定主题入口：`raw/x_topic_targets_v1.json`
- 热门叙事：`raw/x_hot_narratives_v1.json`
- 提及增速：`raw/x_mention_velocity_v1.json`
- 关键币种扩散：`raw/x_key_symbol_diffusion_v1.json`


## 信息流层验证字段（已纳入）
- `source_confidence`：来源可信度
- `signal_quality`：信号质量
- `last_verified_at`：最近验证时间


## 真实抓取替代进展
- 已新增 `raw/binance_square_real_fetch_v1.json`
- 已新增 `raw/x_real_fetch_v1.json`
- 当前已开始下调 seed 权重、上调 real_fetch 权重
