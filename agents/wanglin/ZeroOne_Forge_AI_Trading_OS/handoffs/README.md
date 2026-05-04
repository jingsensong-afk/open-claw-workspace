# Handoffs · 协作交接目录

## 用途

本目录是 **Claude Code 与 Codex 之间的异步协作通道**。两个 AI 不在实时聊天，所有结构化交流通过此目录的 markdown 文件 + git 历史完成。景森（人）扮演两个 AI 之间的"开关人"——告诉对方"该你了"——但不需要复制粘贴任何内容。

## 协作角色（来自 `../COLLABORATION_SAFETY_BOUNDARY.md`）

- **Claude Code**：主力实现 6 层主链业务代码（信息流 / 候选池 / 思考层 / 执行层 / 分发层 / 校准层）
- **Codex**：第二视角协作者——安全审查、风控边界、GitHub 卫生、执行网关设计、schema 加固、test/review
- **景森**：最终决策、风险上限、API Key 授权、真实交易确认（不可由 AI 代行）

## 文件命名规范

每个工作单元（一般是一天一组）按以下规则命名：

```
YYYY-MM-DD_dayN_<topic>_<role>.md
```

`<role>` 取值：

| role | 谁写 | 时机 |
|---|---|---|
| `pre_review` | Claude Code | 动手前 — 拟定方案、列已知风险、列建议检查点 |
| `codex_review` | Codex | 收到 pre_review 后 — 反馈风险盲点、推荐改进 |
| `handoff` | Claude Code | 实施完成后 — 按 7 字段格式回顾本轮成果 |

例：

```
2026-05-04_day4_min_order_handoff.md
2026-05-05_day5_main_trend_pre_review.md
2026-05-05_day5_main_trend_codex_review.md
2026-05-05_day5_main_trend_handoff.md
```

## 标准工作流（结构化版本）

```
[Day N 开工]

  Claude  → 写 day_N_<topic>_pre_review.md
            commit + push

  景森    → 在 Codex 会话说："读 handoffs/ 最新 pre_review，给反馈"

  Codex   → pull → 读 → 写 day_N_<topic>_codex_review.md
            commit + push

  景森    → 在 Claude 会话说："Codex 看过了"

  Claude  → pull → 整合反馈 → 实施代码改动
            commit + push

  景森    → 在 Codex 会话说："代码完成，最终审查"

  Codex   → pull → 看 diff → 直接修补 push 或追加 review 意见

  Claude  → 写 day_N_<topic>_handoff.md（最终交接）
            commit + push
```

## 7 字段交接格式（handoff 必含）

```yaml
本轮目标:
改动文件:
运行命令:
产出文件:
是否涉及真实交易:
是否涉及外部分发:
是否涉及 API Key / token / secret:
已知风险:
建议 Codex 检查点:
```

`pre_review` 里至少包含：本轮目标 / 已知风险 / 建议 Codex 检查点 三项。

## 轻量替代（成熟后可降级）

协作流跑顺后，**非风控、非安全、非真实动作**的改动可以从"独立 markdown 文件"降级为"代码内注释"：

```python
# CODEX_REVIEW: 这个阈值是经验值，BTC 上是否合理？
THRESHOLD = 0.05

# CODEX_REVIEW: ...
# CLAUDE_REPLY: 经过历史回测确认，BTC 上 0.05 在 70% 时间内有效，保留。
THRESHOLD = 0.05
```

**但涉及以下场景必须保持文件级 handoff**：
- 真实交易、风控参数调整
- 外部分发（Telegram / Binance Square / X）
- API Key / token / secret 相关改动
- 自动化主链（cron / refresh_market_os_full_chain.sh）的接入或扩展

## 硬约束

- Codex review 指出的**风控漏洞或安全风险，优先于功能进度**——发现就停手
- 7 字段中任何"是否涉及" 为"是"的项，**必须有景森的人工确认**才能进入实施
- 历史 handoff 文件**不删不改**，只追加（git 历史已足够审计，但保留单独文件方便对照）
- 多个 review 文件意见冲突时，按 `COLLABORATION_SAFETY_BOUNDARY.md` 的优先级裁决

## 维护

- 这个 README 由 Claude 起草，Codex 可直接修补完善
- 任何重要协作约定调整都应该体现在这个 README 里，并 commit 留痕
