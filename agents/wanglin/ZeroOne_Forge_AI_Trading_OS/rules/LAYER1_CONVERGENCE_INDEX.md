# 第一层信息流层收口索引（2026-04-28）

## 当前唯一主逻辑
### 主规则
- `rules/AI_TRADING_OS_DUAL_PATH_LAYER1_RULES.md`
- `rules/AI_TRADING_OS_STAGE1_PLAN.md`（其中双路径筛选主轴部分为当前有效主定义）

### 主工作流
- `workflows/AI_TRADING_OS_DUAL_PATH_LAYER1_WORKFLOW.md`

### 当前主产物
- `data/market_os_stage1/processed/layer1_dual_path_A_resonance.json`
- `data/market_os_stage1/processed/layer1_dual_path_B_capital_only.json`
- `data/market_os_stage1/processed/layer1_dual_path_C_attention_only.json`
- `data/market_os_stage1/pools/candidate_pool_v2_from_signal_cards.json`（当前第二层入口，现仅承接 A 类）

## 继续有效但属于底层辅助
- `rules/AI_TRADING_OS_REAL_FETCH_DEPTH_RULES.md`
- `rules/AI_TRADING_OS_SHORT_CYCLE_PRE_SIGNAL_RULES.md`
- `rules/AI_TRADING_OS_SOURCE_INGESTION_PLAN.md`
- `processed/market_signals_v1.json`
- `raw/` 下各抓取源数据

## 已彻底移除的旧主链部分
- 旧 signal card 主规则与工作流
- 旧 normalized signal cards 主产物

说明：当前第一层只保留双路径主逻辑，不再保留旧 signal card 主链引用。
