# 王林｜AI交易OS 第六层连续校准层工作流

## 默认顺序
1. 读取当前 pools / thought / execution / distribution outputs
2. 记录本轮主判断与执行输出
3. 下一轮对比验证哪些成立、哪些失效、哪些要修正
4. 输出 calibration report
5. 把规则修正回写到系统
