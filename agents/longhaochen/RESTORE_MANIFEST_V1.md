# 龙皓晨恢复清单 V1

更新时间：2026-04-08

## 一、用途
本文件用于在 GitHub 备份恢复后，快速、精准地恢复龙皓晨主实例的身份、边界、主线机制、自动任务与交付标准，避免恢复后出现“能运行但规则漂移、任务缺口、交付失真”的问题。

---

## 二、恢复目标
恢复后必须达到以下状态：
1. 龙皓晨身份正确
2. 读取/写入边界正确
3. 4 月新版主线文档齐全
4. 主实例 3 条主干 cron 正常存在
5. 每条 cron 满足“三层验收法”：触发成功 / 内容生成成功 / Telegram 真正送达成功
6. 不与王林实例串线
7. 关键有效变更可正常 commit + push 到 GitHub

---

## 三、龙皓晨默认工作入口
### 默认读取
- 顶层主系统入口
- `shared/`
- `agents/longhaochen/`

### 默认写入
- 顶层主系统入口
- `shared/`
- `agents/longhaochen/`

### 明确禁止
- 不默认读取 `agents/wanglin/`
- 不将王林的 cron、执行逻辑、执行记录、分区记忆混为龙皓晨默认上下文
- 仅在协作所需的调度、检查执行、整合复盘场景下，按需查看王林分区

---

## 四、恢复时必须优先确认的核心文件
### A. 身份与边界层
1. `IDENTITY.md`
2. `USER.md`
3. `REBOOT_RULES.md`
4. `MEMORY.md`
5. `agents/longhaochen/REBOOT_RULES.md`
6. `agents/longhaochen/README.md`

### B. 4 月新版主线机制层
1. `ROLE_LONGHAOCHEN_V2.md`
2. `WORKFLOW_DAILY_RADAR_V3.md`
3. `OUTPUT_MECHANISM_V2.md`
4. `DAILY_REVIEW_MECHANISM_V1.md`
5. `EVENT_JUDGMENT_LOGIC_V1.md`
6. `PREDICTION_MARKET_EXECUTION_V1.md`
7. `TEAM_TRADING_COLLAB_MECHANISM_V1.md`
8. `WORKING_SYSTEM_V1.md`

### C. 系统协作与分区层
1. `AGENT_PARTITION_PLAN.md`
2. `PARTITION_EXECUTION_RULES.md`
3. `SYSTEM_STATUS_V1.md`

---

## 五、当前有效主线（以 2026-04-01 及之后版本为准）
### 固定主输出
1. **11:00 每日主报告**
2. **14:00 每日预测市场分析**
3. **22:30 日终复盘（简版）**

### 已废弃旧主线
- 固定 `15:30` 增量补丁

### 额外规则
- 若遇重大突发事件，可单独输出异常提示
- 主报告必须先完成事件判断，未完成不得进入正文

---

## 六、主实例当前 3 条主干 cron（恢复后必须核对）
### 1. `zov-main-daily-report-v4`
- 时间：11:00 Asia/Shanghai
- 任务：每日主报告
- 当前要求：按 V3 + 4 月新版机制直接产出可发送成稿
- 投递：Telegram 当前私聊窗口 `telegram:7570144264`

### 2. `zov-main-prediction-report-v2`
- 时间：14:00 Asia/Shanghai
- 任务：每日预测市场分析
- 当前要求：按新版预测市场机制直接产出可发送成稿
- 投递：Telegram 当前私聊窗口 `telegram:7570144264`

### 3. `zov-main-daily-review-v1`
- 时间：22:30 Asia/Shanghai
- 任务：日终复盘（简版）
- 当前要求：按新版复盘机制直接产出可发送成稿
- 投递：Telegram 当前私聊窗口 `telegram:7570144264`

---

## 七、完成标准（恢复后必须按此验收）
任何龙皓晨自动化任务，默认都按“三层验收法”验收：
1. **任务触发成功**
2. **内容生成成功**
3. **目标渠道真正送达成功**

只有三层都通过，才算完整恢复或完整交付。

---

## 八、恢复后最容易出错的点
1. 只恢复 cron，不恢复 delivery
2. 只恢复文件，不恢复发送链路
3. 只看到 isolated session 生成内容，就误判为“任务已完成”
4. 恢复后边界漂移，错误读取王林分区
5. 使用名字而非真实 Telegram target / chat_id 发送，导致最后一跳失败

---

## 九、旧文件与归档策略
### 当前有效
- 顶层 4 月主线文档
- `agents/longhaochen/` 当前入口文件

### 已归档旧主线
- `archive/2026-04-upgrade/WORKFLOW_DAILY_RADAR_V1.md`
- `archive/2026-04-upgrade/WORKFLOW_DAILY_RADAR_V2.md`
- `archive/2026-04-upgrade/WORKING_SYSTEM_V1.md`
- `archive/obsolete-pre-2026-04/` 下的旧执行记录与旧 radar 数据

恢复时，默认以“当前有效层”为准；历史归档只用于审计、回看与复盘，不作为默认工作入口。

---

## 十、GitHub 备份治理
### 默认规则
- 关键有效变更完成后立即 `commit + push`
- 不实时全量同步所有噪音信息
- 仅同步有明确更新价值的有效变更

### 恢复后必须确认
1. remote 已连接
2. SSH / 写权限正常
3. 本地与远端可正常 push

---

## 十一、恢复后最小检查顺序
1. 确认身份文件正确
2. 确认边界规则正确
3. 确认 4 月主线核心文档齐全
4. 确认 3 条主干 cron 存在
5. 确认 cron delivery 正确
6. 手工验证至少 1 条任务送达
7. 确认 GitHub push 正常
8. 确认不与王林串线

---

## 十二、一句话恢复原则
龙皓晨恢复，不是把文件拉回来就算完成；而是要恢复到：
**身份正确、边界正确、主线正确、自动任务正确、交付送达正确、GitHub 可备份、且不与王林串线。**
