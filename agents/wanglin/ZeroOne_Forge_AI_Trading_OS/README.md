# ZeroOne Forge AI交易OS

## 统一入口
这是王林分区下的 AI交易OS 主目录，后续与 AI交易OS 直接相关的规则、工作流、脚本、数据、校准、恢复说明，默认统一归入本目录。

## 与王林分区总规则的关系
- `agents/wanglin/rules/WORKING_RULES.md` 是王林分区的上位边界规则。
- `ZeroOne_Forge_AI_Trading_OS/rules/` 是 AI交易OS 子系统运行规则。
- AI交易OS 的所有运行规则，均不得违反王林分区总边界、身份边界与读写边界。

## 当前主链
### 自动主刷新链
- `scripts/refresh_market_os_full_chain.sh`
- 已接为主刷新链，默认按 cron 自动运行
- 负责依次刷新：
  1. 信息流层
  2. 候选池层
  3. 思考层
  4. 执行层
  5. execution 强一致性约束
  6. 分发层
  7. 校准层

## 关键目录
- `rules/`：系统规则
- `workflows/`：工作流
- `scripts/`：执行脚本
- `data/market_os_stage1/`：运行数据与校准结果

## 恢复优先阅读顺序
1. `rules/AI_TRADING_OS_STAGE1_PLAN.md`
2. `scripts/refresh_market_os_full_chain.sh`
3. `data/market_os_stage1/calibration_layer/quant_calibration_report_2026-04-26.json`
4. `data/market_os_stage1/calibration_layer/system_convergence_review_2026-04-26.json`

## 当前建设原则
- 追求精准、简洁、有效
- 避免乱散、极重、臃肿
- 六层联动，形成“发现 → 筛选 → 判断 → 执行 → 分发 → 校准 → 反向修正”的闭环系统
- 优先复用已有沉淀，不轻易平行新建

## 分层固定索引
- 第一层：`rules/LAYER1_INFOFLOW_INDEX.md`
- 第二层：`rules/LAYER2_CANDIDATE_INDEX.md`
- 第三层：`rules/LAYER3_THOUGHT_INDEX.md`
- 第四层：`rules/LAYER4_EXECUTION_INDEX.md`
- 第五层：`rules/LAYER5_DISTRIBUTION_INDEX.md`
- 第六层：`rules/LAYER6_CALIBRATION_INDEX.md`

说明：后续新增的规则、文件、模板、交易卡、数据产物，默认应固定到对应层，避免层级混乱、执行乱串与职责漂移。
