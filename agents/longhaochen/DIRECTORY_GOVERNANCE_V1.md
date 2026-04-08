# 龙皓晨目录治理清单 V1

更新时间：2026-04-08

## 一、用途
本清单用于明确龙皓晨主线相关文件在仓库中的层级位置、保留理由与后续整理方向，避免顶层文件持续膨胀、主线文件与参考文件混杂，影响恢复精度与工作连续性。

---

## 二、顶层保留原则
只有满足以下任一条件的文件，才应长期保留在顶层：
1. 属于龙皓晨主实例默认入口
2. 属于主线核心机制文件
3. 属于全局分区/系统治理文件
4. 恢复时必须第一批读取

不满足以上条件的文件，应优先考虑：
- 转入 `agents/longhaochen/`
- 转入 `shared/`
- 转入 `archive/`

---

## 三、当前顶层文件分层判断
### A. 必须保留在顶层（默认入口层）
1. `IDENTITY.md`
2. `USER.md`
3. `REBOOT_RULES.md`
4. `MEMORY.md`
5. `SOUL.md`
6. `TOOLS.md`
7. `AGENTS.md`

### B. 暂时保留在顶层（当前主线机制层）
1. `ROLE_LONGHAOCHEN_V2.md`
2. `WORKFLOW_DAILY_RADAR_V3.md`
3. `OUTPUT_MECHANISM_V2.md`
4. `DAILY_REVIEW_MECHANISM_V1.md`
5. `EVENT_JUDGMENT_LOGIC_V1.md`
6. `PREDICTION_MARKET_EXECUTION_V1.md`
7. `TEAM_TRADING_COLLAB_MECHANISM_V1.md`
8. `WORKING_SYSTEM_V1.md`

### C. 暂时保留在顶层（全局治理 / 分区协作层）
1. `AGENT_PARTITION_PLAN.md`
2. `PARTITION_EXECUTION_RULES.md`
3. `SYSTEM_STATUS_V1.md`
4. `WANGLIN_COLLAB_RESULTS_V1.md`

### D. 非主线核心，后续应考虑下沉或归档
1. `CASEBOOK_ZEROONE_RESEARCH_TRADING_V1.md`
2. `SKILL_BASELINE_TRADING_V1.md`
3. `GROWTH_PANEL.md`
4. `TELEGRAM_GROUP_ONBOARDING.md`
5. `CREDENTIALS_INTEGRATION_SPEC_V1.md`

说明：这些文件仍有参考价值，但不应持续与主线核心文件混在同一层级作为默认入口。

---

## 四、建议的后续目录治理方向
### 第一优先级：维持当前主线稳定，不立即搬迁核心机制文件
原因：
- 当前 cron、恢复手册、规则引用都已对齐到现有路径
- 立即搬迁容易破坏恢复链路与引用稳定性

### 第二优先级：把“参考型文件”逐步从顶层下沉
建议目标：
- `agents/longhaochen/references/`
- 或 `archive/reference/`

候选文件：
- `CASEBOOK_ZEROONE_RESEARCH_TRADING_V1.md`
- `SKILL_BASELINE_TRADING_V1.md`
- `GROWTH_PANEL.md`
- `TELEGRAM_GROUP_ONBOARDING.md`
- `CREDENTIALS_INTEGRATION_SPEC_V1.md`

### 第三优先级：形成“顶层最小主线集”
目标状态：
- 顶层只保留默认入口、主线机制、全局治理文件
- 参考材料、案例材料、扩展说明逐步下沉

---

## 五、当前不建议立即移动的文件
以下文件虽然理论上可进一步目录化，但当前不建议立刻移动：
1. `WORKFLOW_DAILY_RADAR_V3.md`
2. `OUTPUT_MECHANISM_V2.md`
3. `DAILY_REVIEW_MECHANISM_V1.md`
4. `EVENT_JUDGMENT_LOGIC_V1.md`
5. `ROLE_LONGHAOCHEN_V2.md`
6. `PREDICTION_MARKET_EXECUTION_V1.md`
7. `TEAM_TRADING_COLLAB_MECHANISM_V1.md`

原因：
- 它们已是当前恢复与运行链路的主锚点
- 先保证“恢复精准与路径稳定”，再考虑更深度的结构化迁移

---

## 六、当前推荐的实际使用方式
### 默认主线工作时
优先读取：
- 顶层入口文件
- 顶层主线机制文件
- `agents/longhaochen/` 下恢复与索引文件

### 历史回看 / 方法论补充时
按需读取：
- 顶层参考型文件
- `archive/` 下旧主线与历史记录

---

## 七、一句话治理结论
当前最优策略不是“立刻大搬家”，而是：
**先用恢复清单 + 文件索引把主线钉稳，再逐步把非核心参考文件从顶层下沉，最终形成更干净的顶层最小主线集。**
