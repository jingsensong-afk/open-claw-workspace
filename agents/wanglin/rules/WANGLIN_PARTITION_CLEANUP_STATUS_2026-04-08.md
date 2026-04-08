# 王林分区整理状态说明（2026-04-08）

## 结论
当前 Git 已跟踪的 `agents/wanglin/` 文件清单，与本地现有王林分区文件清单已基本一致。

这意味着：
- 当前问题不是 GitHub 上还残留大量“本地没有的旧文件”；
- 当前主要问题是：本地分区内部需要把“默认入口 / 默认模板 / 历史保留稿 / 9维主链文件”区分得更清楚，避免恢复时混用。

## 当前整理原则
### 1. 保留为默认主链
以下文件已视为当前 BTC/ETH 主报告与热点异动报告的默认主链：
- `rules/BTC_ETH_9D_ANALYSIS_PROTOCOL.md`
- `rules/BTC_ETH_MAIN_REPORT_OUTPUT_ENFORCEMENT.md`
- `rules/KEY_DATA_GAP_AND_SOURCE_PLAN.md`
- `rules/BTC_ETH_9D_RECOVERY_INDEX.md`
- `templates/BTC_ETH_MAIN_REPORT_BACKEND_CHECKLIST.md`
- `templates/BTC_ETH_MAIN_REPORT_TEMPLATE.md`
- `templates/BTC_ETH_MAIN_REPORT_EXAMPLE.md`
- `templates/HOT_MARKET_OPPORTUNITY_TEMPLATE.md`
- `templates/HOT_MARKET_OPPORTUNITY_EXAMPLE.md`

### 2. 保留为分区总入口 / 恢复入口
- `README.md`
- `REBOOT_RULES.md`
- `MEMORY.md`

### 3. 保留为执行与复盘链
- `templates/CRYPTO_EXECUTION_TEMPLATE.md`
- `templates/CRYPTO_EXECUTION_LOG_TEMPLATE.md`
- `templates/END_OF_DAY_REVIEW_TEMPLATE.md`
- `rules/CRYPTO_EXECUTION_SYSTEM.md`
- `rules/WORKING_RULES.md`

### 4. 历史保留，不作为当前9维主链默认入口
- `templates/EXECUTION_LOG_TEMPLATE_V2.md`

## 当前不建议动作
1. 不建议为追求简洁直接删除历史保留稿。
2. 不建议在尚未验证完全替代关系前，删除执行链旧模板。
3. 不建议在 push 前再大规模移动路径，避免恢复链再次变化。

## 当前建议动作
1. 以当前本地王林分区作为“定版结构”。
2. 将本说明与恢复索引一并保留到 GitHub。
3. 后续若要继续精简，单独做“模板收敛”专项，而不是与本次 9维补链混在一起。

## 一句话
本次应做的是“结构定版并推送”，不是“继续大删大改”。当前本地结构已足够清晰，适合作为 GitHub 侧的新基准版本。
