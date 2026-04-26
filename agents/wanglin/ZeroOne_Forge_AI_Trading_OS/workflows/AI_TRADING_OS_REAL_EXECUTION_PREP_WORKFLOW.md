# 王林｜AI交易OS 真实小额执行 / API 接入准备工作流

1. 盘点当前 paper execution 输出字段
2. 提取真实下单最小所需字段
3. 输出 API 接入清单
4. 输出风控约束清单
5. 输出最小真实执行白名单
6. 标记当前阶段为 prep_ready / waiting_api_connection

6. 执行器内部自动完成 目标名义价值(U) -> 合法quantity，再提交给交易所公开 API
