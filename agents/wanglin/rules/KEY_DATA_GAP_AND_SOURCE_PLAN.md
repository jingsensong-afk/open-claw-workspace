# 王林｜关键数据缺口与补链计划

更新时间：2026-04-07

## 当前最关键的数据缺口
1. 清算热图 / 未平仓集中区缺口明显
2. 宏观流动性链未形成固定抓取链路

## 已确认可接入、需尽快固化进主报告的维度
### OI（未平仓量）
- 主参考：Binance USDⓈ-M
- 交叉验证：OKX
- 补充：Hyperliquid
- 现阶段判断：已具备明确来源，不再属于“无来源缺口”，当前任务是固化为 BTC/ETH 主报告后台默认取数链。

### Funding（资金费率）
- 主参考：Binance USDⓈ-M
- 交叉验证：OKX
- 补充：Hyperliquid
- 现阶段判断：已具备明确来源，不再属于“无来源缺口”，当前任务是固化为 BTC/ETH 主报告后台默认取数链。

## 目标
把主报告从“结构恢复版”升级成“稳定 9 维版”。

## 补链优先级
### P1：流动性链
- 清算热图
- 未平仓集中区
- 当前优先来源：AiCoin
- 当前辅助来源：Hyperliquid 清算 / 大额仓位相关公开数据
- 当前目标：先确认是否具备稳定权限与稳定取数链，再决定是否正式纳入主报告第8维

### P2：宏观链
- 美债收益率
- DXY
- 美股指数
- 期货贵金属走势
- 资金流数据
- 当前执行顺序：先补“风险偏好层”，再补“crypto资金流层”

### P3：杠杆与拥挤链优化
- OI
- Funding
- 多空持仓比
- 当前状态：已具备明确来源，后续重点是优化字段口径与报告表达，而非从零补链

## 执行原则
1. 没有稳定数据源前，不得把对应维度写成已完整分析。
2. 缺关键维度时，主报告必须降级表达。
3. 数据源一旦跑通，优先固化到王林规则或模板里。

## 方案B（稳定优先）接入清单
### 第8维：清算热图 / 未平仓集中区
- 主来源：CoinGlass API
- 基础信息：
  - 当前推荐版本：CoinGlass API V4
  - 基础地址：`https://open-api.coinglass.com`
- 目标字段：
  - liquidation heatmap
  - aggregate liquidation heatmap
  - 关键清算密集区
  - 更可能先被扫的一侧
- 接入前置条件：
  - 注册 CoinGlass 账号
  - 获取可用 API Key / 对应授权
  - 确认第8维所需端点是否已在当前套餐开放
- 当前角色：作为第8维主补链方向，优先级最高

### 第9维：宏观流动性
#### 风险偏好层
- 主来源：Trading Economics
- 基础地址：`https://api.tradingeconomics.com`
- 目标字段：
  - DXY
  - 美债收益率
  - 美股指数
  - 黄金
  - 原油
- 接入前置条件：
  - 注册 Trading Economics 账号
  - 获取 API Key
  - 确认使用 query 参数 `?c=API_KEY` 或 `Authorization` header 方式调用

#### crypto资金流层
- 稳定币主来源：DefiLlama Stablecoins
- ETF主来源：BTCETFData
- 目标字段：
  - 稳定币总市值 / 变化 / 净流入流出
  - BTC ETF净流 / 持仓变化
  - 后续再补 ETH ETF流
- DefiLlama 已确认可直接走免费公共 API（`https://api.llama.fi`），优先使用：
  - `/stablecoins`
  - `/stablecoincharts/all`
  - `/stablecoinchains`
- BTCETFData 当前已确认网页层可稳定抓到：ticker / holdings / daily change / as-of date；若后续确认 JSON 入口，再切为 JSON 优先

## 落地顺序
1. CoinGlass API（先解决第8维）
2. Trading Economics（先补第9维风险偏好层）
3. DefiLlama Stablecoins（补第9维 crypto资金流层第一部分）
4. BTCETFData（补第9维 crypto资金流层第二部分）

## 当前阶段判断
- 模板与规则约束已明显加强
- OI / Funding 已进入固化阶段
- 真正决定能否过线的，接下来主要是第8维与第9维的数据链补齐
- 当前最优执行路线：按方案B（稳定优先）逐步接入 CoinGlass / Trading Economics / DefiLlama Stablecoins / BTCETFData
