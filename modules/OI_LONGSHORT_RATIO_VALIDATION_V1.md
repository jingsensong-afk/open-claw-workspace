# OI + 多空持仓比完整验证模块 V1

更新时间：2026-03-14

## 目标
补齐“仅看 OI 不够、缺少多空持仓比验证”的能力缺口，用于判断：
- 当前上涨/下跌是健康趋势，还是拥挤方向的反身性行情
- OI 变化是否被 long/short ratio 结构确认
- 何时属于挤空/挤多高风险区

## 核心输入
1. OI（绝对值 + 变化速度）
2. Funding（方向与极值）
3. Long/Short Ratio（账户比、持仓比，按可得口径）
4. 价格结构（关键位突破/跌破）
5. 量能（是否放大）

## 判断框架
### A. 趋势健康上行（偏可持续）
- 价格上行
- OI 温和上升
- long/short ratio 未极端偏多
- funding 不过热

### B. 挤空上行（高波动）
- 价格上行
- OI 上升
- long/short ratio 仍偏空或快速修复
- funding 仍负或由负向0收敛

### C. 诱多风险（高位转弱）
- 价格上冲
- long/short ratio 极端偏多
- funding 过热
- OI 不再抬升或开始下滑

### D. 下跌踩踏（挤多）
- 价格跌破关键承接位
- OI 快速回落
- long/short ratio 由高位偏多快速塌陷
- 量能放大

## 输出模板
1. 当前价格状态
2. OI 状态
3. long/short ratio 状态
4. funding 状态
5. 当前归类（A/B/C/D）
6. 当前判断（延续/反身性/诱多/踩踏）
7. 触发条件
8. 失效条件
9. 风险提示

## 使用原则
1. 不能只看 OI 做结论
2. OI 与 long/short ratio 必须联合验证
3. funding 与 ratio 冲突时，优先看价格+OI是否确认
4. 极端 ratio 只能提示风险，不单独决定方向

## 当前结论
该模块用于补齐 ZeroOne 在“OI + 多空持仓比完整验证”方面的能力缺口，后续将与：
- `SHORT_TERM_TURNING_POINT_ALERT_RULES_V1`
- `LIQUIDITY_HEATMAP_ALT_V1`
- `INVALIDATION_FIRST_MECHANISM_V1`
联动使用。
