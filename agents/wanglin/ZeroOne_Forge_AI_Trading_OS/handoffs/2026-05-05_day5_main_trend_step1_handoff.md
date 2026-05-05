# Day 5 · Step 1 Handoff · Config + Preflight + Wrapper

**类型**：partial handoff（Codex 七步走的第 1 步落地，business strategy 代码尚未编写）
**日期**：2026-05-05
**作者**：Claude Code
**对应提交**：`fb44ffd wanglin: add freqtrade dry-run config + preflight gate + wrapper (Day 5 step 1)`
**Pre-review**：`2026-05-05_day5_main_trend_pre_review.md`
**Codex review**：`2026-05-05_day5_main_trend_codex_review.md`

---

## 本轮目标

按 Codex review 提出的硬化顺序，落地"启动安全门"层：先把"机器可校验的 dry-run 启动检查 + 凭证安全注入 + freqtrade 调用"这条骨架打通，**严格不写策略业务代码**——这条骨架不稳，后面的 risk gate / strategy / 回测都是沙上盖楼。

具体覆盖 Codex 建议的：

- ✅ 启动 preflight（机器可校验，缺一退出，不依赖人眼盯）
- ✅ 不直接裸跑 `freqtrade trade`，提供 wrapper 强制走 preflight
- ✅ 凭证不硬编码到 config，运行时 env 注入
- ✅ pair 白名单只 BTC/ETH 永续
- ✅ leverage / 单笔风险 / 日熔断的硬上限固定在 config + preflight 双重校验
- ⏭ 风控 gate（Step 2 才做）
- ⏭ 策略文件（Step 3 才做）
- ⏭ 回测 + 数据下载（Step 5-6 才做）

## 改动文件

```
新增：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/config/freqtrade_main_dryrun.json
    98 行 · Freqtrade 主配置
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py
    333 行 · 16 项硬安全检查，纯 Python stdlib，零外部依赖
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/run_main_trend_dryrun.sh
    104 行 · bash wrapper（chmod +x），preflight → 凭证注入 → exec freqtrade
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/user_data/.gitkeep
    Freqtrade workspace 占位

修改：
  .gitignore
    + agents/wanglin/ZeroOne_Forge_AI_Trading_OS/user_data/*
    + !agents/wanglin/ZeroOne_Forge_AI_Trading_OS/user_data/.gitkeep
```

## 运行命令

**Preflight 单独跑**（任何时候都可以，只读，不调外部）：
```bash
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py
```
返回 0 = 全过；返回 2 = 至少一项失败（详细原因写到 stderr）。

**完整 wrapper 跑**（preflight + 凭证注入 + freqtrade 调用）：
```bash
bash agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/run_main_trend_dryrun.sh \
  <freqtrade-subcommand> [其他参数]
```

例：
- `bash ...run_main_trend_dryrun.sh show-config` —— 只读，验证 freqtrade 能解析配置
- `bash ...run_main_trend_dryrun.sh download-data --timerange 20220601-20260501` —— Step 5 用
- `bash ...run_main_trend_dryrun.sh backtesting` —— Step 6 用
- `bash ...run_main_trend_dryrun.sh trade` —— Step 8 才允许跑（人工确认后）

## 产出文件

- 终端打印 preflight 16 项检查结果
- 终端打印凭证注入摘要（仅 length + head/tail 4 字符，不打印 key 内容）
- 终端打印 freqtrade 子命令的输出
- `user_data/` 下 freqtrade 运行时产物（logs / 下载的 K 线 / 回测结果）—— 全部 gitignore，不入仓

## 是否涉及真实交易

**否**。三层防护：

1. config `dry_run: true` + `exchange.sandbox: true`
2. preflight 严格校验上述两项必须 `=== true`，任何其他值都拒绝启动
3. wrapper 通过 `set -euo pipefail` 保证 preflight 失败立即退出，不会到 freqtrade 调用阶段

verified：smoke test 跑 `show-config` 时 freqtrade 输出明确显示 `"dry_run": true, "sandbox": true`。

## 是否涉及外部分发

**否**。

- `telegram.enabled: false`（token / chat_id 留空字符串作为防御深度）
- `api_server.enabled: false`（HTTP API 不开）
- 配置中没有 webhook、external_message_consumer、binance_square、x、discord 任何外部分发字段

preflight 显式校验前两项必须 disabled。

## 是否涉及 API Key / token / secret

**是 · 但只是复用 + 增强**。

- **无新增 key**：沿用 Day 4 已建的 `agents/wanglin/.binance_futures_api.testnet.json`
- **不硬编码到 config**：`exchange.key` 和 `exchange.secret` 在 config 里都是空字符串
- **运行时 env 注入**：wrapper 用 venv 自带的 Python 解析 JSON，导出 `FREQTRADE__EXCHANGE__KEY` 和 `FREQTRADE__EXCHANGE__SECRET`，仅在 freqtrade 子进程的 env 中存在
- **不打印明文**：wrapper 只打印 key 长度（应 64）+ 头尾 4 字符（核对用），不会出现在终端、日志或 git
- **freqtrade 自动 redact**：smoke test 的 `show-config` 输出确认 freqtrade 把 password 字段显示为 `"REDACTED"`（虽然我们的字段是 disabled-not-used，但 redaction 行为已验证）

## 已知风险

### 低风险（已知，已护栏）

1. **freqtrade 配置 schema 强制 telegram.token / chat_id 字段**
   - 我们填了空字符串以满足 schema，preflight 未额外校验这些字段必须为空
   - 如果未来有人同时把 telegram.enabled 改成 true 并填入真实 token，preflight 会拦下 enabled 但不会拦下 token
   - **建议 Codex 检查**：preflight 是否需要追加 "如果 telegram.enabled 为 true 直接拒绝（无论 token 内容）"

2. **wrapper 透传 freqtrade 子命令完全不限制**
   - 当前 wrapper `exec "$VENV_FREQTRADE" "$@" --config ... --userdir ...`
   - 任何 freqtrade 子命令都能跑，包括 `trade`（实盘 dry-run）
   - 配合 config 的 `dry_run: true` 是安全的，但如果有人 wrapper 之外手动 export `FREQTRADE__DRY_RUN=false`，会绕开
   - **建议 Codex 检查**：是否在 wrapper 里加一行 `unset FREQTRADE__DRY_RUN FREQTRADE__EXCHANGE__SANDBOX` 来防止 env 篡改

### 中等风险（设计选择，需要确认）

3. **`max_leverage_cap` / `risk_per_trade_pct` / `daily_loss_halt_pct` 三个值在 config 里**
   - 这是为了让 preflight 能校验它们。但 freqtrade 本身**不消费**这三个字段（它们是我们自定义的 OS 层概念）
   - 真正消费它们的是 Step 2 的 `risk/risk_control.py`（还没写）
   - **当前位置在 config 里只是数据，不是约束**——Step 2 写完风控 gate，需要从 config 读这三个值
   - 如果 Step 2 写完后这三个字段失去校验意义，**preflight 应该改成同时校验"`risk_control.py` 是否存在并能 import"**

4. **MainTrendStrategy 还不存在**
   - config 里 `"strategy": "MainTrendStrategy"`，preflight 校验通过
   - 但运行 `freqtrade trade` / `backtesting` 时会因为找不到策略类报错
   - 这是**预期行为**——Step 1 的目的就是骨架先稳，业务代码 Step 3 再填
   - 当前 wrapper 跑 `show-config` 等不依赖策略的子命令是 OK 的

### 工程小坑（已发现并修复，记录便于追溯）

5. **path resolution 踩过的坑（已修）**
   - 第一次 mkdir 时 cwd 不在仓库根，导致目录建在 `/Users/asen/Documents/code/agents/wanglin/`（错位）
   - 第一次 wrapper 没 cd，freqtrade 找不到 user_data
   - 修复：wrapper 显式 `cd "$REPO_ROOT"` + freqtrade `--userdir <绝对路径>` 双保险
   - 错位目录已删除

6. **freqtrade schema 对 disabled 块仍要求字段**
   - telegram / api_server 即使 enabled=false 也要 token / username 等字段
   - 当前用空字符串 / "disabled-not-used" 填充，schema 验证通过
   - **未来 freqtrade 升级可能改 schema**，需要在 README 里提醒

## 建议 Codex 检查点

按重要性排序：

### 🔴 高（涉及安全门）

1. **wrapper 是否需要 unset 危险 env 变量**
   - 用户可能在 shell 里 `export FREQTRADE__DRY_RUN=false` 后再跑 wrapper
   - 当前 wrapper 没有 unset，env 会传给 freqtrade
   - 建议 wrapper 在调用 freqtrade 前显式：
     ```bash
     unset FREQTRADE__DRY_RUN
     unset FREQTRADE__EXCHANGE__SANDBOX
     ```
   - 加上之后，外部 env 永远盖不掉 config 里的 `dry_run: true`

2. **preflight 对 telegram / api_server 的校验是否够严**
   - 当前只校验 `enabled === false`
   - 是否需要追加：即使 enabled=false，如果 telegram.token 或 api_server.password 不是预期值（"" / "disabled-not-used"），也拒绝？
   - 这能防止"留着真 token 等未来一改 enabled=true 就生效"的情况

3. **是否需要 wrapper 拒绝某些 freqtrade 子命令**
   - 例如 `wrapper.sh new-config` 会让 freqtrade 写入新 config 文件，可能覆盖我们的 config
   - `wrapper.sh trade` Step 1 阶段不应该被允许跑（因为策略不存在 + risk gate 不存在）
   - 建议 wrapper 引入"允许的子命令白名单"，目前是 [show-config, download-data, backtesting]，trade 等到 Step 8 再加

### 🟡 中（涉及未来 Step 衔接）

4. **三个风控字段的语义在 Step 1 是松耦合**
   - `max_leverage_cap` / `risk_per_trade_pct` / `daily_loss_halt_pct` 在 config 但 freqtrade 不读
   - Step 2 写 `risk_control.py` 时，这些值应该从 config 读取（确保 single source of truth）
   - 建议 Codex 在 Step 2 review 时确认这点

5. **user_data dir 当前用 `--userdir` 绝对路径覆盖 config 里的相对路径**
   - 是否需要把 config 里的 `user_data_dir` 字段直接删掉（避免 source-of-truth 不一致）？
   - 还是保留作为"文档性默认值"？

### 🟢 低（工程清理）

6. **gitignore 的 `**/__pycache__/` 模式是否过宽**
   - 当前 `agents/wanglin/ZeroOne_Forge_AI_Trading_OS/**/__pycache__/`
   - 是否会误伤将来 `data/` 下的内容？

7. **bot_name `ZeroOneForge_MainTrend_Dryrun` 的命名是否符合王林 OS 命名风格**

---

## 不在本轮范围（明确推迟）

按 Codex review 的 7 步顺序，下面这些**不在 Step 1 的责任内**：

- ❌ `risk/risk_control.py` 风控 gate（Step 2）
- ❌ `strategies/main_trend_strategy.py` 策略文件（Step 3）
- ❌ Donchian 通道 / funding rate 拉取的具体实现（Step 3）
- ❌ K 线历史数据下载（Step 5）
- ❌ 回测脚本调用 + 报告生成（Step 6）
- ❌ 与 buy-and-hold benchmark 对比（Step 7）

---

## 等待信号

- ⏳ Codex 对本 step1 handoff 的反馈（如有 🔴 项，立即修；🟡 / 🟢 可在 Step 2 一起修）
- ⏳ 景森的 go 指令进入 Step 2（写 `risk/risk_control.py`）

如果 Codex 提了 🔴 高优先级问题，**Step 2 启动之前必须先解决**。
