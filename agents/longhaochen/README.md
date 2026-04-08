# 龙皓晨分区说明

## 默认入口
龙皓晨默认工作入口：
- 顶层主系统入口
- `shared/`
- `agents/longhaochen/`

## 分区边界
- 不默认读取 `agents/wanglin/`
- 仅在协作所需的调度、检查执行、整合复盘场景下，按需查看王林分区
- 不将王林的 cron、执行逻辑、执行记录、分区记忆混为龙皓晨默认上下文

## 当前主线机制（以 2026-04-01 及之后版本为准）
1. `ROLE_LONGHAOCHEN_V2.md`
2. `WORKFLOW_DAILY_RADAR_V3.md`
3. `OUTPUT_MECHANISM_V2.md`
4. `DAILY_REVIEW_MECHANISM_V1.md`
5. `EVENT_JUDGMENT_LOGIC_V1.md`
6. `PREDICTION_MARKET_EXECUTION_V1.md`
7. `TEAM_TRADING_COLLAB_MECHANISM_V1.md`

## 自动任务主干
- 11:00 每日主报告
- 14:00 每日预测市场分析
- 22:30 日终复盘（简版）

## 验收规则
凡自动化链路任务，默认采用“三层验收法”：
1. 触发成功
2. 内容生成成功
3. Telegram 真正送达成功

## 恢复参考
恢复时优先查看：
- `agents/longhaochen/RESTORE_MANIFEST_V1.md`
- `REBOOT_RULES.md`
- `MEMORY.md`
