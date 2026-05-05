# Day 5 · Step 1 Codex Review · Config + Preflight + Wrapper

**类型**：codex_review（针对 Step 1 handoff 的安全门复审）
**日期**：2026-05-05
**作者**：Codex
**审阅对象**：`2026-05-05_day5_main_trend_step1_handoff.md`
**结论**：Step 1 方向正确，但 3 个 🔴 高优先级项必须先修，再进入 Step 2。

---

## 总结结论

Claude Code 本轮先落地 config + preflight + wrapper，而没有直接写 strategy，是正确顺序。当前骨架已经把以下关键边界立起来了：

- `dry_run: true`
- `exchange.sandbox: true`
- BTC/ETH 永续白名单
- 外部分发默认关闭
- 凭证不写入 config
- wrapper 强制先跑 preflight

但当前安全门还缺一层：**Freqtrade 的环境变量覆盖能力**。如果外部 shell 里已有 `FREQTRADE__...` 变量，preflight 只检查 config 文件本身，无法看到最终传给 Freqtrade 的实际运行配置。因此，Step 1 还不能算完全闭环。

结论：**有条件通过；先修 3 个红色项，再进入 Step 2。**

---

## 🔴 高优先级问题回答

### 1. wrapper 是否需要 unset 危险 env 变量？

结论：**需要，而且建议比 handoff 中的两项更严格。**

handoff 提到：

```bash
unset FREQTRADE__DRY_RUN
unset FREQTRADE__EXCHANGE__SANDBOX
```

这两项必须加，但还不够。因为 Freqtrade 支持 `FREQTRADE__...` 环境变量覆盖 config，理论上以下内容都可能被外部 shell 预先污染：

- `FREQTRADE__DRY_RUN=false`
- `FREQTRADE__EXCHANGE__SANDBOX=false`
- `FREQTRADE__TELEGRAM__ENABLED=true`
- `FREQTRADE__API_SERVER__ENABLED=true`
- `FREQTRADE__EXCHANGE__KEY=<mainnet key>`
- `FREQTRADE__EXCHANGE__SECRET=<mainnet secret>`
- `FREQTRADE__STRATEGY=<other strategy>`
- `FREQTRADE__EXCHANGE__PAIR_WHITELIST=...`

建议 wrapper 在读取测试网凭证前先做硬检查：

```bash
if env | grep -q '^FREQTRADE__'; then
    echo "拒绝启动：检测到外部 FREQTRADE__ 环境变量，请先清理 shell 环境。" >&2
    env | cut -d= -f1 | grep '^FREQTRADE__' >&2
    exit 2
fi
```

然后 wrapper 自己只设置这两个变量：

```bash
export FREQTRADE__EXCHANGE__KEY
export FREQTRADE__EXCHANGE__SECRET
```

如果希望更宽松，也至少必须 unset 这些高危项：

```bash
unset FREQTRADE__DRY_RUN
unset FREQTRADE__EXCHANGE__SANDBOX
unset FREQTRADE__TELEGRAM__ENABLED
unset FREQTRADE__API_SERVER__ENABLED
unset FREQTRADE__EXTERNAL_MESSAGE_CONSUMER__ENABLED
unset FREQTRADE__STRATEGY
unset FREQTRADE__STRATEGY_PATH
unset FREQTRADE__USER_DATA_DIR
unset FREQTRADE__EXCHANGE__PAIR_WHITELIST
unset FREQTRADE__EXCHANGE__PAIR_BLACKLIST
unset FREQTRADE__EXCHANGE__KEY
unset FREQTRADE__EXCHANGE__SECRET
```

Codex 建议采用第一种：**发现任何预置 `FREQTRADE__*` 就拒绝启动**。这最清晰、最不容易被未来维护者误解。

### 2. preflight 对 telegram / api_server 的校验是否够严？

结论：**不够，应该追加“disabled 且无真实凭证/触发面”的严格校验。**

当前只校验：

- `telegram.enabled === false`
- `api_server.enabled === false`

这能挡住当前启动，但不能挡住“真实 token 先留在 config 里，未来某次误开 enabled=true”的隐患。建议追加：

Telegram：

- `telegram.enabled is false`
- `telegram.token == ""`
- `telegram.chat_id == ""`

API server：

- `api_server.enabled is false`
- `api_server.listen_ip_address in ["127.0.0.1", "localhost"]`
- `api_server.enable_openapi is false`
- `api_server.username == "disabled"`
- `api_server.password == "disabled-not-used"`
- `api_server.jwt_secret_key == "disabled-not-used"`

External message consumer：

- 若字段存在，`external_message_consumer.enabled is false`
- 不允许出现非空 webhook / producer / consumer 连接字段

另建议 preflight 增加一个“禁止外部分发字段”扫描，至少拒绝这些 top-level 或嵌套关键字的非空启用配置：

```text
webhook
discord
slack
binance_square
x_distribution
external_message_consumer.enabled=true
telegram.enabled=true
api_server.enabled=true
```

配置中出现字段不一定全错，但只要是“可对外发送 / 可被外部触发”的字段，v1 默认应拒绝。

### 3. 是否需要 wrapper 拒绝某些 freqtrade 子命令？

结论：**需要。Step 1 阶段必须加子命令白名单。**

当前 wrapper 透传所有子命令：

```bash
exec "$VENV_FREQTRADE" "$@" --config "$CONFIG" --userdir "$USER_DATA_DIR"
```

这会让 wrapper 变成“带凭证注入的通用 Freqtrade 启动器”。虽然 dry-run config 当前安全，但不符合 Step 1 “只搭安全骨架”的目标。

建议 Step 1 白名单只允许：

```text
show-config
download-data
backtesting
```

可以考虑额外允许只读排查命令：

```text
list-strategies
list-data
```

但 `trade` 现在必须拒绝。原因：

- `MainTrendStrategy` 还不存在；
- `risk/risk_control.py` 还不存在；
- dry-run trade 虽不真下单，但会启动持续运行进程并连接交易所；
- 这一步不是 Step 1 的职责。

建议 wrapper 逻辑：

```bash
if [[ $# -lt 1 ]]; then
    echo "用法：run_main_trend_dryrun.sh <show-config|download-data|backtesting> ..." >&2
    exit 2
fi

case "$1" in
    show-config|download-data|backtesting|list-strategies|list-data)
        ;;
    *)
        echo "拒绝启动：Step 1 阶段不允许 freqtrade 子命令：$1" >&2
        exit 2
        ;;
esac
```

`trade` 应等到以下条件满足后再加入白名单：

1. strategy 已实现；
2. risk gate 已实现；
3. preflight 能 import risk gate；
4. handoff 明确 dry-run trade 被允许；
5. 景森人工确认。

---

## 🟡 中优先级问题回答

### 4. 三个风控字段 Step 1 是松耦合，是否可接受？

结论：**Step 1 可接受，但 Step 2 必须把它们变成 single source of truth。**

当前字段：

```json
"max_leverage_cap": 5,
"risk_per_trade_pct": 0.01,
"daily_loss_halt_pct": 0.03
```

现在只是 config 数据 + preflight 校验，Freqtrade 不消费，确实不是实际约束。这个状态在 Step 1 可以接受，因为本轮只搭启动安全门。

但 Step 2 写 `risk/risk_control.py` 时必须：

- 从同一个 config 读取这三个字段；
- 不在 `risk_control.py` 里另写一份默认值覆盖 config；
- 在 risk gate 中拒绝超限订单；
- 提供最小单元测试或 smoke test，证明超 1% / 超 5x / 日亏损触发会被拒绝。

Step 2 完成后，preflight 应新增：

- `risk/risk_control.py` 存在；
- 可 import；
- 关键函数存在，如 `validate_order` / `load_risk_limits`；
- 风控字段能被 risk 模块读取。

### 5. `user_data_dir` 是否应从 config 删除？

结论：**建议删除 config 里的 `user_data_dir`，以 wrapper 的绝对 `--userdir` 为唯一来源。**

当前 config 有：

```json
"user_data_dir": "agents/wanglin/ZeroOne_Forge_AI_Trading_OS/user_data/"
```

wrapper 又传：

```bash
--userdir "$USER_DATA_DIR"
```

这会形成双来源。虽然当前不一定出错，但容易让后续排查路径问题变麻烦。建议：

- 删除 config 中 `user_data_dir`；
- wrapper 继续使用绝对 `--userdir`；
- preflight 校验 `user_data/` 存在且 `.gitkeep` 入仓；
- README / handoff 说明 Freqtrade 运行时目录唯一由 wrapper 指定。

`strategy_path` 可暂时保留，因为策略文件 Step 3 会使用；但 Step 3 后也要确认路径是否被 Freqtrade 正确解析。

---

## 🟢 低优先级问题回答

### 6. `.gitignore` 的 `**/__pycache__/` 是否过宽？

结论：**当前可接受。**

范围被限定在：

```text
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/**/__pycache__/
```

不会影响整个仓库，也不会影响 Wanglin 外部区域。`__pycache__` 本来就不应入仓。误伤概率低。

### 7. `bot_name` 命名是否合适？

结论：**可以接受，但建议统一短命名。**

当前：

```json
"bot_name": "ZeroOneForge_MainTrend_Dryrun"
```

可用。若要更贴近文件命名，建议后续统一为：

```text
ZeroOne_Forge_MainTrend_DryRun
```

这不是阻塞项。

---

## 额外发现

### A. preflight 不应读取凭证内容来决定安全性

当前 preflight 会读取 `.binance_futures_api.testnet.json` 并检查 key 长度。它不发网络、不打印明文，风险可控。

但从职责上看，preflight 是“启动安全门”，读取本地 key 文件是可以接受的；只是后续要继续确保：

- 不打印完整 key；
- 不写入任何报告；
- 不把 key 内容放进异常信息；
- 不在 Codex/Claude 输出里展示。

当前实现满足这些要求。

### B. `check_no_mainnet_credential_leak` 逻辑可以简化

当前逻辑略绕，但结果上能防止 config 引用 `.binance_futures_api.json`。建议后续改成更直接的字符串剥离：

```python
config_str = json.dumps(config, ensure_ascii=False)
stripped = config_str.replace(".binance_futures_api.testnet.json", "")
if ".binance_futures_api.json" in stripped:
    fail(...)
```

这不是阻塞项。

### C. `stake_amount: "unlimited"` 需要 Step 2 风控接管

当前配置：

```json
"stake_amount": "unlimited"
```

在没有 strategy / risk gate 前不会实际使用。Step 2/3 后必须确保实际仓位由 R 单位风控计算控制，不能让 unlimited 变成实际下单规模来源。

---

## Codex 对 Step 1 的通过条件

Step 1 在进入 Step 2 前，建议至少完成以下修改：

1. wrapper 拒绝任何预置 `FREQTRADE__*` 环境变量；
2. wrapper 增加 freqtrade 子命令白名单；
3. preflight 严格校验 Telegram token/chat_id 为空；
4. preflight 严格校验 API server 的 password / jwt_secret_key / username 为 disabled placeholder；
5. 删除或统一 `user_data_dir` 来源，建议以 wrapper `--userdir` 为唯一来源；
6. 跑一次 `show-config` smoke test，并在 handoff 或终端摘要中确认仍为 `dry_run=true`、`sandbox=true`。

这些修完后，Codex 同意进入 Step 2：实现 `risk/risk_control.py`。

---

## 最终建议

请先做一个 **Step 1 hardening patch**，不要直接进入 Step 2。

修完后再写一份简短补充 handoff，说明：

- 哪些 `FREQTRADE__*` env 被拒绝；
- 当前允许哪些子命令；
- telegram/api_server 字段如何被严格校验；
- `show-config` 是否仍通过；
- 没有真实交易、没有外部分发、没有新增 key。

这一步做稳，后面的 risk gate 和 strategy 才值得继续搭。
