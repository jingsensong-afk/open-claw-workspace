# 王林｜MARKET OS 第一阶段工作流

## 目标
把外部市场信息统一转成第一层双路径结果，并继续收窄为第二层正式候选。

## 工作流
1. Sources
   - Binance Square
   - X / Twitter
   - Exchange Ranks
   - 短周期盘口/量价/OI/funding/榜单信号

2. Raw Storage
   - 原始抓取结果进入 `data/market_os_stage1/raw/`

3. Normalize
   - 标准化进入 `data/market_os_stage1/processed/market_signals_v1.json`

4. Dual-path Builder
   - 生成 `layer1_dual_path_A_resonance.json`
   - 生成 `layer1_dual_path_B_capital_only.json`
   - 生成 `layer1_dual_path_C_attention_only.json`

5. Candidate Builder
   - 仅由 A类共振标的生成 `candidate_pool_v2_from_signal_cards.json`

6. Downstream
   - 第三层判断
   - 第四层执行层
   - 第五层分发层
   - 第六层校准层

## 默认顺序
先抓取，再标准化，再输出第一层双路径结果，再从 A类中继续收窄为正式候选。

## 当前阶段要求
- 只围绕新主链运行
- 不再生成 v1 candidate/execution 并行池
- 不追求一开始就全自动实盘
