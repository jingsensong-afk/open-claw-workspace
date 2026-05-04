# Day 4 Handoff · Testnet 最小下单闭环

**类型**：retrospective handoff（追溯式交接，本轮工作发生在 Codex 协作框架建立之前）
**日期**：2026-05-04
**作者**：Claude Code
**对应提交**：`edfdbad wanglin: add testnet min order test script (10U DOGE long/close round trip)`

---

## 7 字段交接

### 本轮目标

补全王林 OS 第四层"执行层"的 hello-world 测试网最小下单闭环。把执行层从"只有 markdown 规则 + 一个 mainnet 连通性脚本"提升为"可用的、有 base_url 安全护栏的、能完成开仓 / 平仓 / 写回报告的真实代码"。

### 改动文件

**新增（已 commit）**：

```
agents/wanglin/.binance_futures_api.testnet.json.example
  - 测试网凭证 JSON 模板（含中文使用说明），可入仓
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/binance_testnet_connectivity_check.py
  - 只读连通性检查（查余额 + 查账户信息）
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/binance_testnet_min_order_test.py
  - 写路径下单测试（开多 → 等 N 秒 → 平仓 → 写报告）
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1/execution_layer/binance_testnet_min_order_2026-05-04T06-42-06Z.json
  - 首次成功 round trip 的执行层报告
```

**新增（gitignored，本地 only）**：

```
agents/wanglin/.binance_futures_api.testnet.json
  - 真实测试网 key（景森本地填入，Claude 全程未接触明文）
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/
  - Python 3.12 虚拟环境（freqtrade 2026.4 + ccxt 4.5.51 等）
```

**修改**：

```
.gitignore
  - 新增 testnet 凭证模式
  - 新增 .venv 路径（已挪入王林专区）
  - 新增 SQLite 数据库模式
```

### 运行命令

```bash
cd /Users/asen/Documents/code/open-claw-workspace
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \
    agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/binance_testnet_connectivity_check.py
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \
    agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/binance_testnet_min_order_test.py
```

### 产出文件

- `data/market_os_stage1/execution_layer/binance_testnet_min_order_2026-05-04T06-42-06Z.json`
  - 含订单 ID、avgPrice、executedQty、手续费、毛 PnL 完整链路记录
- 终端打印每步状态（Key 长度、头尾 4 字符、各步 HTTP 状态、最终成交价）

实测结果：
- 开仓 90 DOGE @ 0.11228（订单 ID 801385518，FILLED）
- 平仓 90 DOGE @ 0.11227（订单 ID 801385677，FILLED）
- 毛 PnL: -0.0009 USDT（仅滑点）
- 手续费 ~0.008 USDT
- 账户净变化 5000 → 4999.991

### 是否涉及真实交易

**否**。base_url 硬校验必须包含 "testnet" 关键字，否则脚本 `raise RuntimeError` 拒绝执行。所有调用都打到 `https://testnet.binancefuture.com`。

### 是否涉及外部分发

**否**。无任何 Telegram / Binance Square / X 调用。

### 是否涉及 API Key / token / secret

**是**。具体处理方式：

- 凭证文件 `agents/wanglin/.binance_futures_api.testnet.json` 在 .gitignore 排除
- 模板 `.example` 入仓，含中文使用说明
- 脚本 `load_credentials()` 函数从 JSON 读 key，**Claude 全程未接触明文**——脚本只输出 key 长度（应 64）+ 头尾 4 字符（用于人眼核对）
- ⚠️ 注：景森曾在早期对话中粘贴过测试网 key 一次，已作废 + 重新生成。**Codex 在 review 时建议把"曾出现在聊天"的 key 视同泄露**

### 已知风险

1. **签名调用模式与主网同构**：脚本签名逻辑、URL 构造、HMAC 算法与主网完全相同，唯一区别是 `base_url`。如果 .testnet.json 被人为篡改 base_url，URL 校验会拦下，但若关键字检查不严（如出现 "uat-testnet" 之类），可能被绕过。
2. **wait_for_fill 5 秒超时**：测试网市价单延迟若超过 5 秒，函数返回最后状态而非 FILLED。调用方对 `status == "FILLED"` 的判断可能误报。
3. **失败 open 后 close 也失败的窄窗口**：脚本仅打印 ⚠️ 提示，不会自动重试或自动平仓——遗留未平仓位需人工去测试网手动处理。
4. **测试网 `?symbol=` 过滤参数不可靠**：在 `/fapi/v1/exchangeInfo` 上加 `?symbol=DOGEUSDT` 可能返回错误的交易对规则。脚本已改为拉全部 + 客户端过滤来规避。
5. **DOGE 测试网精度与主网不同**：测试网 DOGEUSDT step=1（整数下单），主网 step=0.0001。代码用 `MARKET_LOT_SIZE` 过滤器自适应，但**未在主流币（BTC/ETH）上验证过精度行为**。

### 建议 Codex 检查点

1. **base_url 关键字检查强度**：当前用 `"testnet" in url.lower()`。是否需要更严格的白名单（精确匹配 `https://testnet.binancefuture.com`）？
2. **是否对 testnet 脚本也加 `--i-understand-testnet` 形式的硬阻断**——与主网风格统一，养成每次执行前显式确认的习惯。
3. **wait_for_fill 兜底逻辑**：超时后是否应该 raise 而不是返回最后状态？或加重试机制？
4. **执行层 JSON 命名规范**：当前 `binance_testnet_min_order_<ts>.json` 与既有 `binance_futures_live_min_test_precision_fixed_*.json` 风格不一致，是否需要统一？
5. **未平仓位的 fail-safe**：开多成功但平仓失败时，是否应该立即触发"自动重试 N 次平仓"或"调用 closeAll 端点"作为兜底？

---

## 上下文备注

本轮工作发生在 Codex 协作框架（commit `7ea8a82`）建立之前，因此没有走"pre_review → codex_review → handoff"的标准三步流程。这份 handoff 是**追溯式补写**，目的是：

- 让 Codex 能在不读完整聊天历史的情况下理解 Day 4 完成了什么
- 建立未来所有 handoff 的格式模板
- 标记建议的安全审查点供后续完善

**Day 5 起将走完整 pre_review → codex_review → 实施 → handoff 流程**。
