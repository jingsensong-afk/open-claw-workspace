# Day 5 · Step 1 Hardening Handoff · 安全门加固

**类型**：补充 handoff（针对 Codex review 的 hardening patch）
**日期**：2026-05-05
**作者**：Claude Code
**对应提交**：`fcfbab4 wanglin: harden Step 1 per Codex review (env / whitelist / strict field checks)`
**关联 review**：`2026-05-05_day5_main_trend_step1_codex_review.md`
**前置 handoff**：`2026-05-05_day5_main_trend_step1_handoff.md`

---

## 本轮目标

按 Codex review 的 6 项硬化清单（3 项 🔴 + 2 项 🟡 + 1 项额外）做补丁，让 Step 1 真正闭环。完成后 Codex 才同意进入 Step 2（risk gate）。

| Codex 要求 | 实施情况 |
|---|---|
| 🔴 wrapper 拒绝预置 `FREQTRADE__*` 环境变量 | ✅ 完成（采用 Codex 推荐的"发现就拒绝"严格模式） |
| 🔴 wrapper 子命令白名单 | ✅ 完成（trade/hyperopt 拒绝，list-* / show-config / download-data / backtesting 允许） |
| 🔴 preflight 严格校验 telegram.token/chat_id 为空 | ✅ 完成 |
| 🟡 preflight 严格校验 api_server 字段为 placeholder | ✅ 完成（listen_ip / openapi / username / password / jwt_secret） |
| 🟡 preflight 扫描禁止的外部分发字段 | ✅ 完成（webhook/discord/slack/binance_square/x_distribution） |
| 🟡 删除 config 里的 `user_data_dir` | ✅ 完成（wrapper `--userdir` 绝对路径为唯一来源） |

🟢 低优先级（Codex 标为 acceptable / 可后续清理）这次没动，留作后续小清理。

## 改动文件

```
修改：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/run_main_trend_dryrun.sh   (+37 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py  (+80 行 / -11 行)
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/config/freqtrade_main_dryrun.json  (-1 行 + 注释)
```

## 运行命令

跟之前一样：
```bash
# 单独跑 preflight
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py

# 完整 wrapper（含子命令白名单）
bash agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/run_main_trend_dryrun.sh \
  <show-config|download-data|backtesting|list-strategies|list-data|list-pairs|list-markets|list-timeframes|test-pairlist> ...
```

## 产出文件

无新增数据产物。仅代码改动。

## 是否涉及真实交易

**否**。本次加固加强了"绝不允许触发真实交易"的护栏：
- 三层防护（config + preflight + wrapper）的边界都更紧
- 即使外部 shell 设了 `FREQTRADE__DRY_RUN=false`，wrapper 现在会拒绝启动
- 即使有人想跑 `trade`，wrapper 现在会拒绝

## 是否涉及外部分发

**否**。加固反向加强了"绝不允许外部分发"——preflight 现在会扫描 webhook/discord/slack/binance_square/x_distribution 字段，任何启用配置都会被拒绝。

## 是否涉及 API Key / token / secret

**是 · 但只是加强保护，未新增 key**。

- 沿用既有 `agents/wanglin/.binance_futures_api.testnet.json`
- 新增检查：telegram.token 必须为空字符串（防止"留着 token 等未来误开"）
- 新增检查：api_server.password 必须是 placeholder（同理）

## 已知风险

### 低风险

1. **wrapper 子命令白名单是固定列表**
   - 如果 Codex 觉得需要加新命令（如 `convert-data`），需要改 wrapper
   - 不是问题，Step 2/3/5 时按需扩

2. **`unset` vs "拒绝"的策略选择**
   - 我采用了 Codex 推荐的"发现就拒绝"严格模式
   - 如果未来某些 CI 环境必须预置 `FREQTRADE__*`，需要在那个环境单独豁免
   - v1 现阶段没这个需求

3. **stake_amount: "unlimited" 仍然在 config**
   - Codex 的"额外发现 C"指出这个会在 Step 2/3 后变成实际下单规模来源的风险
   - 当前 Step 1 不消费它（freqtrade 只在 trade 时用，trade 已被白名单拦下）
   - Step 2 写 risk gate 时必须由 R 单位计算覆盖它

### 中等风险（Step 2 必须解决）

4. **三个风控字段（max_leverage_cap / risk_per_trade_pct / daily_loss_halt_pct）目前只是 config 数据**
   - Codex 已标 🟡 "Step 2 必须读这三个字段做实际约束"
   - 写 risk_control.py 时**必须从 config 读**，不能在代码里另写默认值

## 建议 Codex 检查点

### 🔴 高（关于本次 hardening 是否够 / 有遗漏）

1. **wrapper 的子命令白名单**：
   - 是否漏了应该允许的命令？目前列出 9 个：show-config, download-data, backtesting, list-strategies, list-data, list-pairs, list-markets, list-timeframes, test-pairlist
   - Step 1 阶段还有别的合理只读命令该加吗？

2. **preflight 的外部分发字段扫描覆盖度**：
   - 当前扫描 5 个 top-level 字段（webhook, discord, slack, binance_square, x_distribution）
   - Freqtrade 是否还有其他外部连接字段值得扫？比如 `notification`、`reporters` 之类
   - 嵌套字段（如 `external_message_consumer.producers[*].url`）扫到位了吗？

3. **api_server 的"placeholder 字符串"硬编码**：
   - preflight 写死了 `username=="disabled"` 和 `password=="disabled-not-used"`
   - 如果未来想换 placeholder（比如统一改成 `"REJECTED"`），要同时改 config + preflight
   - 是否值得抽成常量供两处共享读取？

### 🟡 中（关于 Step 2 启动条件）

4. **risk_control.py 应该读 config 的哪三个字段**：
   - 我的方案是直接 `json.load(config_path)["max_leverage_cap"]`
   - Codex 是否建议封装一个 `load_risk_limits(config_path) -> RiskLimits` 函数，避免散落？

5. **Step 2 完成的"通过条件"**：
   - Codex review 提到 Step 2 完成时 preflight 应新增检查（risk_control.py 存在 / 可 import / 关键函数存在）
   - 这意味着 Step 2 不仅写 `risk/risk_control.py`，还要回头改 preflight 加新检查
   - 确认这个理解对吗？

### 🟢 低

6. **bot_name 是否要按 Codex 建议改为 `ZeroOne_Forge_MainTrend_DryRun`**（用下划线分组而不是驼峰）

---

## 测试覆盖

总计 **30 个测试场景全过**：

```
正向：
  preflight 17/17 项检查通过（valid hardened config）
  smoke test：show-config 走完 wrapper 全链路（preflight + 凭证注入 + freqtrade）

反向（preflight 层）：
  原 14 个 + 新 8 个 = 22 个违规场景全部被拒绝
  ├─ telegram 留有真实 token/chat_id（2 个）
  ├─ api_server 监听 0.0.0.0 / 开 OpenAPI / username/password 非 placeholder（3 个）
  └─ config 出现 webhook/discord/binance_square 等外部分发字段（3 个）

反向（wrapper 层）：
  缺少子命令 → 退出 2
  trade 子命令 → 白名单拦下，退出 2
  预置 FREQTRADE__DRY_RUN=false → 环境变量检查拦下，退出 2
```

## 等待信号

- ⏳ Codex 对本 hardening handoff 的反馈
- ⏳ 如果通过 → 景森给 go 进入 Step 2（写 `risk/risk_control.py`）
- ⏳ 如果 Codex 还有补充 → 修完再走一轮

进入 Step 2 前，preflight 当前的 17 项 + wrapper 的 2 道护栏（env 检查 + 白名单）都不应该被弱化。Step 2 只能加新检查，不能减老检查。
