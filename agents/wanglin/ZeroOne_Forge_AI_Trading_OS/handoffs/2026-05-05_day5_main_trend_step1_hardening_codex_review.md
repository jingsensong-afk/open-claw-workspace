# Day 5 · Step 1 Hardening Codex Review

**类型**：codex_review（针对 Step 1 hardening handoff 的复审）
**日期**：2026-05-05
**作者**：Codex
**审阅对象**：`2026-05-05_day5_main_trend_step1_hardening_handoff.md`
**结论**：Hardening 到位；放行 Step 2（写 `risk/risk_control.py`）。

---

## 总结结论

已核对实际文件：

- `scripts/run_main_trend_dryrun.sh`
- `scripts/preflight_freqtrade_main_dryrun.py`
- `config/freqtrade_main_dryrun.json`

并做了三个关键验证：

1. preflight 正向通过：17/17 项检查通过。
2. wrapper 拒绝 `trade`：Step 1 阶段不能启动持续 dry-run trade。
3. wrapper 拒绝外部预置 `FREQTRADE__DRY_RUN=false`：外部 env 覆盖被挡住。

结论：本次 hardening 已满足 Codex 上一轮提出的 Step 1 通过条件，可以进入 Step 2。

Step 2 可以开始写：

```text
risk/risk_control.py
```

但 Step 2 只能增强安全门，不能弱化已有 wrapper / preflight 约束。

---

## 6 个 re-review 问题回答

### 1. wrapper 子命令白名单是否合理？是否漏了应允许的命令？

结论：**合理，Step 1 足够。**

当前白名单：

```text
show-config
download-data
backtesting
list-strategies
list-data
list-pairs
list-markets
list-timeframes
test-pairlist
```

这组命令覆盖了 Step 1 / Step 5 / Step 6 需要的配置检查、数据下载、回测和只读排查。`trade`、`hyperopt` 当前不应放行。

后续如果要加 `convert-data` 之类数据处理命令，应单独在对应 step 的 handoff 中说明，不建议现在扩大白名单。

### 2. 外部分发字段扫描覆盖度是否足够？

结论：**对当前 Step 1 config 足够；后续可增强为递归扫描，但不阻塞 Step 2。**

当前 preflight 已检查：

- `telegram.enabled=false`
- `telegram.token=""`
- `telegram.chat_id=""`
- `api_server.enabled=false`
- `api_server` 关键字段为 placeholder
- `external_message_consumer.enabled=false`
- top-level `webhook / discord / slack / binance_square / x_distribution`

这已经能挡住当前 config 下的主要外部分发入口。

小建议：后续可以把 `check_no_external_distribution_fields()` 升级成递归扫描，覆盖类似：

```text
external_message_consumer.producers[*].url
webhook.url
notification.*
reporters.*
```

但当前 config 没有这些嵌套块，且 `external_message_consumer.enabled` 已被强制 false，所以不阻塞 Step 2。

### 3. api_server placeholder 字符串是否值得抽常量共享？

结论：**暂时不必。**

当前 config 与 preflight 同时使用：

```text
username = "disabled"
password = "disabled-not-used"
jwt_secret_key = "disabled-not-used"
```

写死在 preflight 中可以接受，反而清楚。等未来 placeholder 需要复用到多处或变更频繁，再抽常量。

当前不建议为了这一点引入额外配置层。

### 4. risk_control.py 应该如何读取三个风控字段？

结论：**建议封装 `load_risk_limits(config_path) -> RiskLimits`。**

Step 2 不要在多个函数里直接散落：

```python
json.load(config_path)["max_leverage_cap"]
```

建议结构：

```text
RiskLimits
  max_leverage_cap
  risk_per_trade_pct
  daily_loss_halt_pct

load_risk_limits(config_path) -> RiskLimits
validate_order(order, account_state, limits) -> RiskDecision
```

这样 config 是 single source of truth，risk gate 是唯一执行入口。

硬要求：

- 不在 risk_control.py 里另写一份宽松默认值；
- config 缺字段时 fail closed；
- 字段超过上限时 fail closed；
- 单笔风险、杠杆、日亏损熔断都必须返回明确拒绝原因。

### 5. Step 2 是否需要回头改 preflight，加 risk_control 检查？

结论：**需要。理解正确。**

Step 2 不只是新增 `risk/risk_control.py`。完成后还应增强 preflight，至少检查：

- `risk/risk_control.py` 存在；
- 可以 import；
- `load_risk_limits` 存在；
- `validate_order` 或等价核心 gate 函数存在；
- 能从当前 config 读取三个风控字段；
- 对超限样例能 fail closed。

这样 Step 2 才不是“写了一个模块”，而是把 risk gate 接进启动安全门。

### 6. bot_name 是否要改为 `ZeroOne_Forge_MainTrend_DryRun`？

结论：**不阻塞。**

当前：

```text
ZeroOneForge_MainTrend_Dryrun
```

可以继续用。若后续做命名统一，建议改成：

```text
ZeroOne_Forge_MainTrend_DryRun
```

但这不是安全项，不应阻塞 Step 2。

---

## Step 2 放行条件

Codex 放行 Step 2，条件如下：

1. 保持当前 wrapper 白名单，不允许 `trade`。
2. 保持当前 `FREQTRADE__*` 外部环境变量拒绝策略。
3. 保持 Telegram / API server / external distribution 默认关闭。
4. Step 2 的 `risk_control.py` 必须从 config 读取风控字段。
5. Step 2 必须把 risk gate 接入 preflight。
6. Step 2 不得引入真实交易、外部分发或新增 key。

---

## Step 2 具体建议

建议新增：

```text
risk/__init__.py
risk/risk_control.py
```

建议最小接口：

```python
@dataclass(frozen=True)
class RiskLimits:
    max_leverage_cap: float
    risk_per_trade_pct: float
    daily_loss_halt_pct: float

@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    reason: str

def load_risk_limits(config_path: Path) -> RiskLimits:
    ...

def validate_order(order: ProposedOrder, account_state: AccountState, limits: RiskLimits) -> RiskDecision:
    ...
```

Step 2 可以先不接 strategy，因为 strategy 是 Step 3；但必须提供可测试的 proposed order / account state 输入结构，证明 risk gate 能独立拒绝超限订单。

最低测试场景：

- 0.5% 单笔风险，通过；
- 1.5% 单笔风险，拒绝；
- 5x 杠杆，通过；
- 6x 杠杆，拒绝；
- 日亏损 2%，通过；
- 日亏损 3% 或以上，拒绝；
- 无止损，拒绝；
- 非 BTC/ETH pair，拒绝。

---

## 最终结论

Step 1 hardening 到位。

**Codex 放行 Step 2：可以开始写 `risk/risk_control.py`。**

Step 2 完成后，请继续写 handoff，让 Codex 复审 risk gate 是否真正 fail closed。
