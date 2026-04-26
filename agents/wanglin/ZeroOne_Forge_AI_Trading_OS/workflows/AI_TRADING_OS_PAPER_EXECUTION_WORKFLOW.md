# 王林｜AI交易OS 模拟执行工作流

## 目标
把第四层从执行骨架推进到可运行的 paper execution。

## 默认顺序
1. 读取 execution_whitelist
2. 生成模拟执行计划
3. 记录仓位上限 / 止损条件 / 止盈模式
4. 写入 paper execution log
5. 后续用于校验第三层到第四层衔接是否合理

## 当前阶段原则
- 只做 paper execution
- 不直接进入实盘自动执行
