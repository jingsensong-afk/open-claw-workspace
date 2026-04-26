# 王林｜AI交易OS execution 一致性工作流

## 默认顺序
1. 读取 execution_pool
2. 读取 thought outputs
3. 读取 paper execution
4. 找出缺口标的
5. 自动降级 execution -> candidate
6. 回写 pools 并生成修正报告
