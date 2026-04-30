# 双实例硬隔离执行清单 V1

更新时间：2026-04-30

## 目标
在同一台服务器、同一仓库下，让龙皓晨与王林从**运行层**真正独立，避免 restart / status / config / gateway / delivery 串线。

---

## 一、最终目标态

### 龙皓晨实例
- Service：`openclaw-longhaochen-gateway.service`
- OpenClaw Home：`/root/.openclaw`
- Gateway Port：`16720`
- Workspace：`/root/.openclaw/workspace`

### 王林实例
- Service：`openclaw-wanglin-gateway.service`
- OpenClaw Home：`/root/.openclaw-wanglin`
- Gateway Port：`16721`
- Workspace：`/root/.openclaw-wanglin/.openclaw/workspace`

---

## 二、当前已做到的
- 文件分区已成立：`agents/longhaochen/` 与 `agents/wanglin/`
- 规则边界已成立：龙皓晨不默认读王林，王林不默认读龙皓晨
- GitHub 备份分区已成立
- 龙皓晨主线 cron 规则已固化
- 王林区未备份内容已补充 commit + push

---

## 三、当前未做到的（本次必须解决）
- 仍共用 `openclaw-gateway.service`
- 仍共用同一个 gateway port
- CLI / service config 解析未稳定落到各自实例
- `gateway status` / `restart` 仍可能看错对象或打错对象

---

## 四、最短执行顺序

### Step 1：冻结当前状态
- 暂不继续对王林做临时重启/重装试错
- 先保持龙皓晨主线可用
- 保证两边当前分区文件已备份

### Step 2：创建双 service 目标
目标：不再使用同一个 `openclaw-gateway.service`

应创建：
- `openclaw-longhaochen-gateway.service`
- `openclaw-wanglin-gateway.service`

### Step 3：绑定独立 Home 与端口
龙皓晨：
- `OPENCLAW_HOME=/root/.openclaw`
- `OPENCLAW_GATEWAY_PORT=16720`

王林：
- `OPENCLAW_HOME=/root/.openclaw-wanglin`
- `OPENCLAW_GATEWAY_PORT=16721`
- `NODE_OPTIONS=--dns-result-order=ipv4first`

### Step 4：分别启动与验收
#### 龙皓晨验收标准
- `Config (service): /root/.openclaw/openclaw.json`
- `Listening: 127.0.0.1:16720`
- `RPC probe: ok`

#### 王林验收标准
- `Config (service): /root/.openclaw-wanglin/.openclaw/openclaw.json`
- `Listening: 127.0.0.1:16721`
- `RPC probe: ok`

### Step 5：升级 OpenClaw 程序本体
在完成运行层硬隔离后，再统一升级 OpenClaw 到最新版本。

---

## 五、升级前禁止事项
- 禁止继续用同一个 `openclaw-gateway.service` 去判断两个实例
- 禁止继续让王林与龙皓晨共用同一个 gateway 端口
- 禁止在未完成双 service 隔离前，直接把“实例不稳定”归因于 prompt / memory / 会话重

---

## 六、一句话结论
这次先做的不是“升级版本”，而是：
**先把龙皓晨与王林做成真正双实例硬隔离，再升级。**
