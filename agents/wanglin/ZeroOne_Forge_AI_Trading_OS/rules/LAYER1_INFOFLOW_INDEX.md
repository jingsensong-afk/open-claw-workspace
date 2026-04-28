# 第一层信息流层固定索引

## 规则
- AI_TRADING_OS_STAGE1_PLAN.md
- AI_TRADING_OS_SIGNAL_CARD_RULES.md
- AI_TRADING_OS_REAL_FETCH_DEPTH_RULES.md
- AI_TRADING_OS_SHORT_CYCLE_PRE_SIGNAL_RULES.md
- AI_TRADING_OS_SOURCE_INGESTION_PLAN.md

## 数据产物
- data/market_os_stage1/raw/
- data/market_os_stage1/processed/market_signals_v1.json
- data/market_os_stage1/processed/normalized_signal_cards_v1.json

## 职责
- 独立实时扫描
- 盘口异动捕捉
- 实时验证
- 映射扩展

## 收口说明
- 当前第一层唯一主逻辑参见：`rules/LAYER1_CONVERGENCE_INDEX.md`
- 双路径 A/B/C 输出为当前主产物，旧 signal card 逻辑已降级。
