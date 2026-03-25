# Telegram 工作群接入说明

更新时间：2026-03-13

## 当前状态
- Telegram 渠道正常
- `channels.telegram.groupPolicy = "allowlist"`
- 当前未配置 `groupAllowFrom` / `allowFrom`
- 因此：未放行的 Telegram 群消息会被静默丢弃

## 已选方案
- 保持 `allowlist` 模式
- 后续仅放行 ZeroOne Venture 指定工作群

## 用户下一步需要做的事
1. 创建 Telegram 工作群
2. 将当前 OpenClaw 对应的 Telegram 机器人/账号拉入群
3. 在群里发送一条消息，便于后续确认群 ID 或进行收发测试

## 我后续需要做的事
1. 获取目标群 ID
2. 将该群 ID 加入 `channels.telegram.groupAllowFrom`
3. 重载/重启相关服务（如需要）
4. 做群内收发验证

## 备注
- 推荐只放行正式工作群，不改成全局 `open`
- 这样更安全，也更符合 ZeroOne Venture 后续群协作方式
