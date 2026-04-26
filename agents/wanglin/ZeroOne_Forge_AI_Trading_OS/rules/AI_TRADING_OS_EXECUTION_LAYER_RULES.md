# 王林｜AI交易OS 第四层执行层规则

## 目标
把第三层输出转成可执行的交易动作，但当前阶段先建立“可运行执行骨架”，不直接进入高风险自动实盘。

## 当前阶段定位
- 第一阶段：执行层骨架 + 风控边界 + 执行白名单
- 第二阶段：模拟执行 / 小额测试执行
- 第三阶段：真实自动执行

## 当前执行层默认边界
1. 默认不直接高风险自动实盘。
2. 先从 execution pool 读取标的。
3. 只有进入白名单的标的才可进入执行层。
4. 必须带：动作、方向、仓位上限、失效条件。
5. 未明确风控边界前，不得自动开仓。

## 当前执行层必备字段
- symbol
- action
- side
- confidence
- max_position_pct
- stop_condition
- take_profit_mode
- execution_status
- updated_at
