# 龙皓晨主线文件总索引 V1

更新时间：2026-04-08

## 一、用途
本索引用于把龙皓晨当前有效主线文件、规则文件、交付文件、历史归档文件分层整理清楚，避免恢复后出现“文件都在但不知道先读什么、哪些还有效、哪些只是历史归档”的问题。

---

## 二、默认读取优先级（恢复后严格按此顺序）
### 第一层：身份与边界
1. `IDENTITY.md`
2. `USER.md`
3. `REBOOT_RULES.md`
4. `MEMORY.md`
5. `agents/longhaochen/README.md`
6. `agents/longhaochen/RESTORE_MANIFEST_V1.md`

### 第二层：当前主线机制
1. `ROLE_LONGHAOCHEN_V2.md`
2. `WORKFLOW_DAILY_RADAR_V3.md`
3. `OUTPUT_MECHANISM_V2.md`
4. `DAILY_REVIEW_MECHANISM_V1.md`
5. `EVENT_JUDGMENT_LOGIC_V1.md`
6. `PREDICTION_MARKET_EXECUTION_V1.md`
7. `TEAM_TRADING_COLLAB_MECHANISM_V1.md`
8. `WORKING_SYSTEM_V1.md`

### 第三层：协作与分区机制
1. `AGENT_PARTITION_PLAN.md`
2. `PARTITION_EXECUTION_RULES.md`
3. `WANGLIN_COLLAB_RESULTS_V1.md`
4. `SYSTEM_STATUS_V1.md`

### 第四层：辅助参考（非默认主线入口）
1. `CASEBOOK_ZEROONE_RESEARCH_TRADING_V1.md`
2. `SKILL_BASELINE_TRADING_V1.md`
3. `GROWTH_PANEL.md`
4. `TELEGRAM_GROUP_ONBOARDING.md`
5. `CREDENTIALS_INTEGRATION_SPEC_V1.md`

---

## 三、当前有效文件（默认有效层）
### A. 身份 / 边界 / 恢复入口
- `IDENTITY.md`
- `USER.md`
- `REBOOT_RULES.md`
- `MEMORY.md`
- `agents/longhaochen/README.md`
- `agents/longhaochen/RESTORE_MANIFEST_V1.md`

### B. 主线职责与工作流
- `ROLE_LONGHAOCHEN_V2.md`
- `WORKFLOW_DAILY_RADAR_V3.md`
- `OUTPUT_MECHANISM_V2.md`
- `DAILY_REVIEW_MECHANISM_V1.md`
- `EVENT_JUDGMENT_LOGIC_V1.md`
- `PREDICTION_MARKET_EXECUTION_V1.md`
- `TEAM_TRADING_COLLAB_MECHANISM_V1.md`
- `WORKING_SYSTEM_V1.md`

### C. 协作 / 分区 / 系统治理
- `AGENT_PARTITION_PLAN.md`
- `PARTITION_EXECUTION_RULES.md`
- `SYSTEM_STATUS_V1.md`
- `WANGLIN_COLLAB_RESULTS_V1.md`

---

## 四、自动任务与交付链路对应关系
### 1. 11:00 每日主报告
- cron: `zov-main-daily-report-v4`
- 主规则：`WORKFLOW_DAILY_RADAR_V3.md`
- 输出机制：`OUTPUT_MECHANISM_V2.md`
- 角色职责：`ROLE_LONGHAOCHEN_V2.md`
- 事件判断：`EVENT_JUDGMENT_LOGIC_V1.md`

### 2. 14:00 每日预测市场分析
- cron: `zov-main-prediction-report-v2`
- 主规则：`OUTPUT_MECHANISM_V2.md`
- 协作机制：`TEAM_TRADING_COLLAB_MECHANISM_V1.md`
- 预测市场机制：`PREDICTION_MARKET_EXECUTION_V1.md`

### 3. 22:30 日终复盘
- cron: `zov-main-daily-review-v1`
- 主规则：`DAILY_REVIEW_MECHANISM_V1.md`
- 协作机制：`TEAM_TRADING_COLLAB_MECHANISM_V1.md`

### 验收标准（统一）
- 触发成功
- 内容生成成功
- Telegram 真正送达成功

---

## 五、明确废弃或降级的旧主线
### 已废弃主输出逻辑
- 固定 `15:30` 增量补丁
- 旧版雷达 V1 / V2 作为默认主线入口

### 仅归档保留，不再作为默认工作入口
- `archive/2026-04-upgrade/WORKFLOW_DAILY_RADAR_V1.md`
- `archive/2026-04-upgrade/WORKFLOW_DAILY_RADAR_V2.md`
- `archive/2026-04-upgrade/WORKING_SYSTEM_V1.md`
- `archive/obsolete-pre-2026-04/` 下旧主线执行记录与旧 radar 数据

---

## 六、恢复后最容易误读的文件
### 可保留但不应当作默认入口
- `CASEBOOK_ZEROONE_RESEARCH_TRADING_V1.md`
- `SKILL_BASELINE_TRADING_V1.md`
- `GROWTH_PANEL.md`
- 历史 memory / archived radar 数据

这些文件可用于：
- 历史审计
- 方法论参考
- 技能演化参考

但不应用于替代当前 4 月主线机制文件。

---

## 七、恢复后最小检查清单
1. 身份文件是否正确
2. 边界规则是否正确
3. 4 月主线文件是否齐全
4. 3 条主干 cron 是否存在
5. delivery 是否配置正确
6. 至少一条任务是否成功送达
7. GitHub push 是否正常
8. 是否与王林串线

---

## 八、一句话使用方式
恢复后不要“全仓库平均阅读”，而是：
**先读身份边界层，再读当前主线机制层，再核对自动任务层，最后才按需查看协作层与历史归档层。**
