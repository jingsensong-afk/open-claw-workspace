# 王林｜BTC/ETH 9维恢复索引

更新时间：2026-04-08

## 目标
用于在恢复后，快速、准确、不混乱地恢复 BTC/ETH 主报告与热点异动报告工作流。

不要只零散读文件。
默认按以下顺序恢复。

---

## 一、先读哪些文件

### 1. 总规则入口
1. `agents/wanglin/REBOOT_RULES.md`
2. `agents/wanglin/rules/WORKING_RULES.md`
3. `agents/wanglin/rules/CRYPTO_EXECUTION_SYSTEM.md`

### 2. 9维主报告规则链
4. `agents/wanglin/rules/BTC_ETH_9D_ANALYSIS_PROTOCOL.md`
5. `agents/wanglin/rules/BTC_ETH_MAIN_REPORT_OUTPUT_ENFORCEMENT.md`
6. `agents/wanglin/rules/KEY_DATA_GAP_AND_SOURCE_PLAN.md`

### 3. 后台执行与前台输出模板
7. `agents/wanglin/templates/BTC_ETH_MAIN_REPORT_BACKEND_CHECKLIST.md`
8. `agents/wanglin/templates/BTC_ETH_MAIN_REPORT_TEMPLATE.md`
9. `agents/wanglin/templates/HOT_MARKET_OPPORTUNITY_TEMPLATE.md`

### 4. 示例稿
10. `agents/wanglin/templates/BTC_ETH_MAIN_REPORT_EXAMPLE.md`
11. `agents/wanglin/templates/HOT_MARKET_OPPORTUNITY_EXAMPLE.md`

---

## 二、各文件职责

### `BTC_ETH_9D_ANALYSIS_PROTOCOL.md`
负责定义：
- 9维后台分析框架
- 数据源优先级
- 第6/7/8/9维当前固定取数与补链方向
- 第9维拆成“风险偏好层 + crypto资金流层”

### `BTC_ETH_MAIN_REPORT_OUTPUT_ENFORCEMENT.md`
负责定义：
- 主报告前台必须怎么写
- 哪些缺口必须显式说明
- 哪些情况必须降级
- 什么才算合格主报告

### `KEY_DATA_GAP_AND_SOURCE_PLAN.md`
负责定义：
- 当前仍缺什么
- 哪些已进入固化阶段
- 第8维 / 第9维补链主方案
- 各数据源接入顺序与前置条件

### `BTC_ETH_MAIN_REPORT_BACKEND_CHECKLIST.md`
负责定义：
- 每次出报告前后台必须逐项核对什么
- 第6/7/8/9维必须怎么拆开检查
- 相对上一份主报告如何做连续验证与修正

### `BTC_ETH_MAIN_REPORT_TEMPLATE.md`
负责定义：
- 主报告前台最终格式
- 9维完成情况如何写
- 与上一份报告如何衔接
- 第8维缺失、第9维部分完成时如何显式表达

### `HOT_MARKET_OPPORTUNITY_TEMPLATE.md`
负责定义：
- 热点异动报告最终格式
- 证据等级怎么写
- 若关键证据不足或受主报告缺口影响，如何表达

### 示例稿
负责定义：
- 当前能力条件下的标准写法
- 恢复后若风格漂移，优先参照示范稿纠偏

---

## 三、当前已定的数据源主次顺序
1. 主流衍生品主参考：Binance USDⓈ-M
2. 主流衍生品交叉验证：OKX
3. 链上活跃资金与永续风向补充：Hyperliquid
4. 现货确认 / 美系现货参考：Coinbase
5. 基础行情补充：AiCoin

---

## 四、当前9维真实状态

### 已基本稳定 / 已进入固化阶段
1. 价格结构
2. 成交量
3. EMA
4. MACD
5. RSI
6. OI
7. Funding

### 当前仍未完全打通
8. 清算热图 / 未平仓集中区
9. 宏观流动性

### 第8维当前主方案
- 主方案：CoinGlass API
- 过渡来源：AiCoin
- 辅助来源：Hyperliquid
- 当前状态：等待 key / 授权

### 第9维当前主方案
#### 风险偏好层
- 主方案：Trading Economics
- 当前状态：等待 key

#### crypto资金流层
- 稳定币：DefiLlama Stablecoins
- BTC ETF：BTCETFData
- ETH ETF：后续补链
- 当前状态：DefiLlama / BTCETFData 已可优先推进

---

## 五、恢复后默认工作原则
1. 不得再把“有数据源”误写成“已稳定完整接入”。
2. 不得在第8维缺失时写成完整9维报告。
3. 不得在第9维只完成部分时写成“宏观流动性完整支持”。
4. 主报告前台必须和后台核查保持一致。
5. 异动报告若证据不足，必须直接降级，不得硬拔高。

---

## 六、恢复后默认执行顺序
1. 先读上一份主报告
2. 再按 backend checklist 完成后台核查
3. 明确上一份报告哪些判断继续成立、哪些已失效、哪些需要修正
4. 再按主报告模板输出前台
5. 若发现第8维 / 第9维未完成，必须同步触发降级表达
6. 热点异动报告必须参考主报告当前证据边界，不得脱离主报告独立夸大判断

---

## 七、一页SOP（默认执行版）
### 目标
让 BTC/ETH 主报告在实际执行时不再依赖记忆翻文件，而是按一页流程直接过线。

### Step 1｜锁入口
先按唯一默认链路进入：
1. `BTC_ETH_9D_RECOVERY_INDEX.md`
2. `BTC_ETH_9D_ANALYSIS_PROTOCOL.md`
3. `BTC_ETH_MAIN_REPORT_OUTPUT_ENFORCEMENT.md`
4. `BTC_ETH_MAIN_REPORT_BACKEND_CHECKLIST.md`
5. `BTC_ETH_MAIN_REPORT_TEMPLATE.md`

### Step 2｜先跑后台，再写前台
必须先完成 backend checklist，再允许生成前台主报告。
禁止倒序：禁止先写结论、后补核查。

### Step 3｜6/7维硬门槛
OI 与 Funding 必须按以下顺序核查完成：
- Binance USDⓈ-M
- OKX
- Hyperliquid

只要出现以下任一情况：
- OI 未完成
- Funding 未完成

则：
- 不得使用“主报告”标题
- 标题必须改为：`BTC/ETH快报（未完成版）｜YYYY-MM-DD HH:mm`

### Step 4｜8/9维真实表达
- 第8维未完成：前台必须直接写“清算热图 / 未平仓集中区暂缺”
- 第9维仅部分完成：前台必须直接写“宏观流动性部分完成 / crypto资金流部分支持或证据不足”

### Step 5｜发前四问（拦截）
发出前必须检查：
1. OI 今天是否真的已查完？
2. Funding 今天是否真的已查完？
3. 前台“9维完成情况”是否与 backend checklist 一致？
4. 若存在缺项，标题是否已自动降级？

四问只要有一项答“否”，不得发主报告。

### Step 6｜合格交付标准
一份 BTC/ETH 主报告要同时满足：
- 走唯一默认入口
- backend checklist 已完成
- 6/7维已过硬门槛
- 8/9维缺口已真实表达
- 前台与后台一致
- 标题等级与完成度一致

### 一句话执行口令
**先后台、后前台；先过门槛、再谈主报告；过不了就降级，不得硬发。**

## 八、一句话恢复提示
恢复后，王林默认不是从“重新摸索 9维框架”开始，而是从：
**已完成 1-7 维固化、正在补第8/9维、前台必须显式降级表达，并按一页SOP直接执行** 这个状态继续工作。
