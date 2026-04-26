# 王林｜AI交易OS execution 一致性硬约束

## 目标
确保 execution pool 与第三层 thought layer、第四层 paper execution 强一致，不允许 execution 长期领先于后两层。

## 硬规则
1. execution_pool 中的标的，必须同步进入 thought outputs。
2. execution_pool 中的标的，必须同步进入 paper execution。
3. 若某标的未进入 thought outputs 或 paper execution，则不得长期停留在 execution。
4. 不满足上述条件的标的，默认降级为 candidate。
