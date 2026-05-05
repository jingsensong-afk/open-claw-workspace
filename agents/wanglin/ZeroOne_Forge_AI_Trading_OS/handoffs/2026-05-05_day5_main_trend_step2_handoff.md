# Day 5 · Step 2 Handoff · Risk Control Gate

**类型**：handoff（Codex 七步走的第 2 步落地）
**日期**：2026-05-05
**作者**：Claude Code
**对应提交**：`62bbadd wanglin: add risk gate module + integrate into preflight (Day 5 step 2)`
**关联 review**：`2026-05-05_day5_main_trend_step1_hardening_codex_review.md`（含 Step 2 spec）
**前置 handoff**：`2026-05-05_day5_main_trend_step1_hardening_handoff.md`

---

## 本轮目标

按 Codex Step 2 规范实现独立风控 gate。所有"产生订单意图"的代码（未来的策略文件、手动脚本、cron 复核器等）下单前必须经 `validate_order()` 审批，gate 通过才能下单。这一步**不接 strategy**（Step 3 才做），但提供了可独立测试的 gate 接口。

具体覆盖 Codex Step 2 spec 的硬要求：

- ✅ `risk/__init__.py` + `risk/risk_control.py` 两个文件
- ✅ 最小接口：`RiskLimits` / `RiskDecision` / `load_risk_limits` / `validate_order`
- ✅ 加 `ProposedOrder` / `AccountState` 数据结构（Codex spec 隐含需要）
- ✅ config 是 single source of truth：`load_risk_limits` 从 `freqtrade_main_dryrun.json` 读，**不在代码里另写默认值**
- ✅ fail closed：缺字段 / 字段超绝对硬上限 → `RiskConfigError`
- ✅ 多重违规一次性返回所有原因
- ✅ 接入 preflight：risk 模块可 import / 关键函数齐 / 能 load_risk_limits / 能拒绝坏订单

## 改动文件

```
新增：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/__init__.py            (33 行)
    └── 包导出：6 个公共类 + 2 个函数 + 1 个异常
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/risk_control.py        (246 行)
    └── 核心 gate 实现，纯 stdlib（json + Decimal + dataclasses）
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/test_risk_control.py   (322 行)
    └── 22 个测试场景（Codex 要求的 8 个 + 9 个边界 + 5 个 config 加载）

修改：
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py  (+76 行)
    └── 新增 check_risk_module_loadable()：3 项检查，preflight 总数 17 → 20
```

## 运行命令

**跑风控测试**：
```bash
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/risk/test_risk_control.py
```
预期输出：22/22 全过，退出码 0

**跑完整 preflight**（含风控集成）：
```bash
agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \
  agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/preflight_freqtrade_main_dryrun.py
```
预期：20/20 全过

**完整 wrapper smoke**：
```bash
bash agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/run_main_trend_dryrun.sh show-config
```
预期：preflight 20/20 → 凭证注入 → freqtrade show-config 输出完整 effective config

## 产出文件

无新增数据产物。仅代码 + 测试。

## 是否涉及真实交易

**否**。本轮只增强了"绝不允许触发真实交易"的护栏：
- risk_control 只做数据结构计算 + 决策返回，**不调任何 API、不发任何请求**
- preflight 的 risk 检查也是纯 in-memory 验证（构造一个坏订单看 gate 是否拒绝）
- wrapper / 子命令白名单 / FREQTRADE__* 拒绝**全部沿用 Step 1 hardening**，未弱化

## 是否涉及外部分发

**否**。risk 模块零网络调用、零文件写入（除测试用 `tempfile`）。

## 是否涉及 API Key / token / secret

**否**。risk_control 不读凭证文件，不接触任何 key。preflight 的 risk 检查只读 config，与凭证无关。

## 已知风险

### 设计层

1. **`DEFAULT_ALLOWED_PAIRS` 在 risk_control.py 里硬编码**
   - 当前是 `frozenset({"BTC/USDT:USDT", "ETH/USDT:USDT"})`
   - 与 config 的 `pair_whitelist` 是两个独立来源（虽然内容一致）
   - **建议未来从 config 读取**，让 config 真正成为 single source of truth
   - 当前 v1 没有迭代压力，先硬编码 + 注释指向

2. **绝对硬上限 (5x / 1% / 3%) 写在 risk_control.py 模块常量**
   - `ABSOLUTE_MAX_LEVERAGE = Decimal("5")` 等
   - 这是 defense-in-depth：即使 config 校验被绕过，risk_control 仍兜底
   - 如果未来要调整这些（如收紧 0.5%），需要改三个地方：config + preflight + risk_control
   - **这是有意的冗余**，不是 bug

3. **AccountState 当前由调用方手动构造**
   - Step 3 写策略时，需要从 Freqtrade 的 wallet/account API 拿真实数据填进来
   - 当前没有"自动获取" helper —— 是 Step 3 责任

### 工程层

4. **测试用 `tempfile` 创建临时 config**
   - 测试结束 `unlink` 删除
   - 如果测试中途异常退出，临时文件可能残留在 /tmp
   - 不影响功能，但会留垃圾。可后续加 `try/finally` 或 `pytest fixture` 清理

5. **`risk/test_risk_control.py` 是手写 runner，不是 pytest**
   - 优点：零依赖，能直接 `python file.py` 跑
   - 缺点：没有 pytest 的 fixture / parametrize 等便利
   - 当前体量不需要 pytest，22 个场景手写 runner 够用

6. **risk 模块路径加载方式（preflight 内部 sys.path 操作）**
   - preflight 用 `sys.path.insert(0, str(WANGLIN_OS_ROOT))` 临时把 OS 根加进 path 来 import risk
   - 用完 `sys.path.remove` 清理
   - 不太优雅但可工作。更好做法是把 wanglin OS 做成 Python 包（加 `pyproject.toml` 注册）
   - 暂时不做包化处理，等仓库结构稳定再说

### 接入层

7. **目前 risk gate 没有"被实际调用方"**
   - Step 3 写 strategy 时，必须显式 `from risk import validate_order`
   - 当前 Step 2 没法验证"未来的策略一定会调用 gate"，只能验证 gate 本身正确
   - **Step 3 review 时需要 Codex 检查 strategy 是否真的过了 gate**

## 建议 Codex 检查点

按重要性排序：

### 🔴 高（关于 gate 本身的正确性）

1. **`validate_order` 的 8 条规则覆盖度**
   - 当前 8 条：白名单 / side 合法性 / 必带止损 / 数量入场杠杆为正 / 杠杆≤上限 / 止损方向 / 单笔风险 / 日内熔断
   - 是否漏了什么 Codex 想看到的规则？比如：
     - 持仓数上限（`open_positions_count >= N` 拒绝）
     - 订单冷却（同一 symbol 在 N 分钟内不能开多次）
     - 反向开仓限制（已有多头持仓时不能开空）
     - 名义额上限（单笔名义 USDT 不超过总权益 X%）
   - 这些是 v1 必要的还是 Step 4+ 再加？

2. **风险百分比计算是否合理**
   - 当前公式：`(entry - stop_loss) * quantity / total_equity`
   - **没扣手续费、没扣滑点 buffer**
   - 真实情况：单笔最大亏损 ≈ 名义风险 + 手续费 + 滑点
   - 是否应该把 fee_pct + slippage_pct 加进 limits，并在 risk 计算里包含？
   - 还是 Step 3 由 strategy 在算 quantity 时自己留 buffer？

3. **杠杆与风险百分比是否互斥校验**
   - 当前两条规则**独立**：杠杆 ≤ 5 + 单笔风险 ≤ 1%
   - 但实际上仓位 = `(risk_pct * equity) / stop_loss_distance_pct`，杠杆是 `仓位名义 / 保证金`
   - 这两个数学上**有联动**：止损距离 + 风险预算决定仓位，仓位 + 保证金决定杠杆
   - 当前实现可能允许"风险 1% 但杠杆 4.5x" 这种几何上看着合理但意图不明的组合
   - 是否需要加一条断言：`leverage * risk_per_trade_pct <= some_threshold`？

### 🟡 中（关于工程清理）

4. **`DEFAULT_ALLOWED_PAIRS` 硬编码 vs 从 config 读**
   - 当前两个独立来源（risk_control 模块常量 + config.exchange.pair_whitelist）
   - 应该让 risk_control 默认从 config 读，但 caller 可以传别的吗？
   - 还是保持当前"hardcoded fallback + 调用方可覆盖"模式？

5. **risk 模块的 sys.path 操作**
   - preflight 临时把 OS 根加进 path 来 import
   - 不优雅但可工作。Codex 觉得需要立刻清理（搞 pyproject.toml + pip install -e .）还是后续再处理？

6. **测试 runner 是手写还是改 pytest**
   - 当前 22 个场景手写 runner，零依赖
   - 切到 pytest 可以更清晰但要 pip install pytest

### 🟢 低（关于命名 / 注释）

7. **`RiskDecision.reasons` 是 `tuple[str, ...]` 还是 `list[dict]`**
   - 当前是中文 string tuple
   - 未来要做结构化日志 / 校准层 SQL 查询时，可能需要每条 reason 带 code + severity 字段
   - v1 string 够用，但可以考虑

---

## 测试覆盖

```
A. validate_order Codex 8 个最低场景         8/8 通过
B. validate_order 边界 / 异常 / 多重违规     9/9 通过
C. load_risk_limits config 加载 + 硬上限     5/5 通过
D. preflight 集成检查（risk 模块端到端）     3/3 通过

总计：22 个 risk 单元测试 + 3 个 preflight 集成测试 = 25 项全部通过
preflight 总检查数：17 → 20（risk 集成 +3）
wrapper smoke：show-config 走完链路，effective config 正确
```

## 等待信号

- ⏳ Codex 对本 Step 2 handoff 的 review，重点是 🔴 高优先级 3 项
- ⏳ 如果 🔴 项中第 1 条（额外规则）被 Codex 要求加，**Step 2 v2 patch**，Step 3 推迟
- ⏳ 如果 🔴 都通过，景森给 go 进入 Step 3（写 `strategies/main_trend_strategy.py`）

Step 3 的具体动作（提前预告）：
- 实现 `MainTrendStrategy(IStrategy)` 类
- Donchian 通道 + funding rate 过滤 + ATR 止损
- **关键约束：策略下单前必须显式调用 risk.validate_order()，否则下单代码不应存在**
- 这意味着策略文件结构会有"信号生成 → ProposedOrder 构造 → validate_order 审批 → Freqtrade entry/exit signal"四阶段
