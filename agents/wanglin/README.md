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
若目标是恢复 BTC/ETH 主报告与异动报告工作流，默认先读：
1. `REBOOT_RULES.md`
2. `rules/BTC_ETH_9D_RECOVERY_INDEX.md`
3. 再按恢复索引继续读其余规则 / 模板 / 示例稿

## 当前专属模板
- `agents/wanglin/templates/CRYPTO_EXECUTION_TEMPLATE.md`
- `agents/wanglin/templates/CRYPTO_EXECUTION_LOG_TEMPLATE.md`

说明：
王林与龙皓晨共享 shared 层，但除共享层外，其他沉淀必须分区，避免恢复与执行混乱。
从 2026-03-27 起，王林正式按专属分区工作。
