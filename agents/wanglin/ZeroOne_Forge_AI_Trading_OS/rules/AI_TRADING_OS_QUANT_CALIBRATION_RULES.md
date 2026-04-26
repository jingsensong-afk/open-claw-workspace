# 王林｜AI交易OS 量化校准规则

## 目标
把第六层从“状态检查”升级到“量化纠偏”。

## 核心
1. 记录每轮 watch / candidate / execution 样本数量
2. 跟踪 execution 与 thought / paper 一致性
3. 统计连续多轮 execution 留存情况
4. 统计 source_type 结构与 real_fetch 占比
5. 输出下轮应修正的重点
