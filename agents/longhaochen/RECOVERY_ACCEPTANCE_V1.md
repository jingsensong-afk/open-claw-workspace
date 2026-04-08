# 龙皓晨恢复后验收手册 V1

更新时间：2026-04-08

## 一、用途
本手册用于在龙皓晨主实例从 GitHub / 本地备份恢复后，快速判断当前状态是：
- 仅文件恢复
- 基础运行恢复
- 主线任务恢复
- 交付链路恢复
- GitHub 备份链路恢复
- 完整恢复

避免再次出现“看起来恢复了，其实只恢复到一半”的误判。

---

## 二、验收原则
恢复不是单点判断，而要分层验收：
1. 身份层
2. 边界层
3. 文件层
4. 任务层
5. 交付层
6. 备份层

只有全部通过，才算完整恢复。

---

## 三、第一层：身份验收
### 检查目标
确认当前实例确实是龙皓晨，而不是空壳、初始实例、或混入其他身份。

### 必查文件
- `IDENTITY.md`
- `USER.md`
- `REBOOT_RULES.md`
- `MEMORY.md`

### 合格标准
- 身份是龙皓晨
- 用户是景森
- 龙皓晨职责是组长 / 总调度 / 总裁决
- 没有恢复成早期“总助”口径

---

## 四、第二层：边界验收
### 检查目标
确认龙皓晨不与王林串线。

### 必查文件
- `REBOOT_RULES.md`
- `USER.md`
- `MEMORY.md`
- `agents/longhaochen/README.md`

### 合格标准
- 默认读取：顶层主系统入口 + `shared/` + `agents/longhaochen/`
- 不默认读取 `agents/wanglin/`
- 仅在调度 / 检查执行 / 整合复盘时按需查看王林分区
- 不把王林的 cron、执行逻辑、执行记录、分区记忆混入龙皓晨默认上下文

---

## 五、第三层：文件验收
### 检查目标
确认 4 月新版主线文档齐全，且旧主线没有误当默认入口。

### 必查文件
- `ROLE_LONGHAOCHEN_V2.md`
- `WORKFLOW_DAILY_RADAR_V3.md`
- `OUTPUT_MECHANISM_V2.md`
- `DAILY_REVIEW_MECHANISM_V1.md`
- `EVENT_JUDGMENT_LOGIC_V1.md`
- `PREDICTION_MARKET_EXECUTION_V1.md`
- `TEAM_TRADING_COLLAB_MECHANISM_V1.md`
- `WORKING_SYSTEM_V1.md`

### 合格标准
- 以上文件齐全可读
- 默认主线是 4 月版本
- 固定 `15:30` 增量补丁不再作为默认主线
- 历史 V1/V2 / 旧执行记录仅在 archive 层保留

---

## 六、第四层：任务验收
### 检查目标
确认龙皓晨 3 条主干 cron 存在且配置正确。

### 必查任务
1. `zov-main-daily-report-v4`
2. `zov-main-prediction-report-v2`
3. `zov-main-daily-review-v1`

### 合格标准
- 任务存在
- 时间正确（11:00 / 14:00 / 22:30）
- payload 与当前主线机制一致
- delivery 已配置
- 投递目标正确

---

## 七、第五层：交付验收
### 检查目标
确认任务不是“只跑了”，而是“真的送达了”。

### 三层验收法
1. **触发成功**
2. **内容生成成功**
3. **Telegram 真正送达成功**

### 合格标准
- `lastRunStatus = ok`
- `lastDeliveryStatus = delivered`
- 目标聊天窗口实际收到消息

### 不合格但容易误判的情况
- 只看到 isolated session 里生成了内容
- cron 显示执行了，但 `lastDeliveryStatus = not-requested`
- 目标 chat_id / target 写错，最后一跳失败

---

## 八、第六层：GitHub 备份验收
### 检查目标
确认恢复后关键有效变更可正常备份到 GitHub。

### 必查项
- remote 是否存在
- SSH 认证是否正常
- push 是否正常

### 合格标准
- 本地可 `commit`
- 可正常 `push` 到 GitHub
- 远端 HEAD 可更新

---

## 九、完整恢复的判定标准
只有当以下 6 项都通过时，才算龙皓晨完整恢复：
1. 身份正确
2. 边界正确
3. 4 月主线文件正确
4. 3 条主干 cron 正确
5. Telegram 真实送达成功
6. GitHub 备份成功

---

## 十、恢复时最常见的假恢复
### 假恢复 1：文件回来了
但：
- cron 没恢复
- delivery 没恢复

### 假恢复 2：任务会触发
但：
- 不会送达
- `lastDeliveryStatus` 不是 `delivered`

### 假恢复 3：能聊天
但：
- 控制面没恢复
- cron / pairing / gateway 不能自管

### 假恢复 4：分区存在
但：
- 读取边界漂移
- 和王林串线

---

## 十一、推荐验收顺序
1. 看身份
2. 看边界
3. 看主线文件
4. 看 cron
5. 看 delivery
6. 手工验证 1 次真实送达
7. 看 GitHub push

---

## 十二、一句话验收结论
龙皓晨恢复完成，不是“能说话、能跑 cron”就够了，而是要同时满足：
**身份对、边界对、主线对、任务对、送达对、备份对。**
