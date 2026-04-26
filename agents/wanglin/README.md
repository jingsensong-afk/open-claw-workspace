# 王林分区说明

角色：投研交易组加密交易执行员

本分区用于沉淀：
- 加密执行日志
- 执行策略
- 执行规则
- 加密交易复盘
- 只属于王林执行线的模板与报告

默认读取：
- shared/
- agents/wanglin/

默认写入：
- agents/wanglin/

## 当前分区结构

### 1. 规则层（rules/）
- `CRYPTO_EXECUTION_SYSTEM.md`：执行总规则、数据源优先级、主报告生成流程
- `BTC_ETH_9D_ANALYSIS_PROTOCOL.md`：BTC/ETH 主报告 9维后台协议
- `BTC_ETH_MAIN_REPORT_OUTPUT_ENFORCEMENT.md`：主报告前台硬约束与降级规则
- `KEY_DATA_GAP_AND_SOURCE_PLAN.md`：当前关键缺口、补链路线、数据源接入顺序
- `BTC_ETH_9D_RECOVERY_INDEX.md`：恢复总索引，恢复时优先用来串联全链路
- `WORKING_RULES.md`：分区工作边界与备份规则

### 2. 模板层（templates/）
#### 主报告链
- `BTC_ETH_MAIN_REPORT_BACKEND_CHECKLIST.md`：后台核查清单
- `BTC_ETH_MAIN_REPORT_TEMPLATE.md`：前台主报告模板
- `BTC_ETH_MAIN_REPORT_EXAMPLE.md`：主报告标准示范稿

#### 热点异动链
- `HOT_MARKET_OPPORTUNITY_TEMPLATE.md`：异动报告模板
- `HOT_MARKET_OPPORTUNITY_EXAMPLE.md`：异动报告示范稿

#### 执行与复盘链
- `CRYPTO_EXECUTION_TEMPLATE.md`
- `CRYPTO_EXECUTION_LOG_TEMPLATE.md`
- `END_OF_DAY_REVIEW_TEMPLATE.md`
- `EXECUTION_LOG_TEMPLATE_V2.md`

## 当前恢复入口
### A. 王林分区总入口（传统执行链）
若目标是恢复 BTC/ETH 主报告、异动报告、传统加密执行链，默认先读：
1. `REBOOT_RULES.md`
2. `rules/BTC_ETH_9D_RECOVERY_INDEX.md`
3. 再按恢复索引继续读其余规则 / 模板 / 示例稿

### B. AI交易OS 子系统入口
若目标是恢复 ZeroOne Forge AI交易OS，默认改走：
1. `ZeroOne_Forge_AI_Trading_OS/README.md`
2. `ZeroOne_Forge_AI_Trading_OS/RECOVERY_INDEX.json`
3. 再按其中 recovery_read_order 继续恢复

说明：
- `agents/wanglin/README.md` 是王林分区总入口。
- `ZeroOne_Forge_AI_Trading_OS/` 是王林分区下的 AI交易OS 子系统入口。
- 两者不是冲突关系，而是总入口与子系统入口的关系。

## BTC/ETH 主报告唯一默认执行入口（硬规则）
以后 BTC/ETH 主报告只能按以下唯一链路执行：
1. `rules/BTC_ETH_9D_RECOVERY_INDEX.md`
2. `rules/BTC_ETH_9D_ANALYSIS_PROTOCOL.md`
3. `rules/BTC_ETH_MAIN_REPORT_OUTPUT_ENFORCEMENT.md`
4. `templates/BTC_ETH_MAIN_REPORT_BACKEND_CHECKLIST.md`
5. `templates/BTC_ETH_MAIN_REPORT_TEMPLATE.md`

禁止事项：
- 禁止跳过恢复索引直接套旧稿
- 禁止绕开 backend checklist 直接写前台
- 禁止把历史示范稿、旧习惯、临时发挥当作默认入口
- 禁止在未经过 6/7 维硬门槛核查前输出“主报告”标题

## 当前专属模板
- `agents/wanglin/templates/CRYPTO_EXECUTION_TEMPLATE.md`
- `agents/wanglin/templates/CRYPTO_EXECUTION_LOG_TEMPLATE.md`

说明：
王林与龙皓晨共享 shared 层，但除共享层外，其他沉淀必须分区，避免恢复与执行混乱。
从 2026-03-27 起，王林正式按专属分区工作。
