# 王林｜真实抓取替代计划

## 目标
逐步用真实抓取替代当前 seed / 结构化样本，降低人工痕迹，提高信息流可信度。

## 替代优先顺序
1. Binance Square
2. X
3. Binance 公告 / 上线 / 新合约

## 替代原则
- 不一次性删除全部 seed
- 哪类来源拿到真实抓取，就先替代哪类来源
- 被替代的 seed 保留留痕，但不再作为主评分输入
- pool 评分优先使用真实抓取来源

## 当前阶段
- 真实抓取来源标记：`source_type` 含 `live` / `real_fetch`
- seed 来源标记：`raw_ref` 中含 `seed`
- 后续逐步把 seed 权重下调，把 real_fetch 权重上调
