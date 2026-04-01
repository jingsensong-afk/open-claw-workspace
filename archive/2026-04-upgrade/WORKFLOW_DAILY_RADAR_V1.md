# 每日投研机会雷达工作流 V1（6个主力 Skill 接入版）

## 目标
将 6 个主力 Skill 接入《每日投研机会雷达》主报告与补充报告流程，形成固定执行顺序。

## 已接入的 6 个主力 Skill
1. funding-rate-scanner
2. hyperliquid
3. polymarket-wallet-xray
4. polyedge
5. crypto-whale-monitor
6. market-sentiment-pulse

## 11:00 主报告执行顺序
### A. 市场结构 / 杠杆 / 资金费率
- funding-rate-scanner
  - 输出：极端 funding、负费率机会、异常币种
- hyperliquid
  - 输出：BTC/ETH 等核心币的 quote、funding、OI、volume、book

### B. 预测市场
- polymarket-wallet-xray
  - 输出：重点钱包画像、是否有 edge、行为特征
- polyedge
  - 输出：预测市场间相关性、错价/相关性偏差

### C. 链上 / 鲸鱼
- crypto-whale-monitor
  - 输出：监控钱包异动、是否有大额变化、是否出现新线索

### D. 市场情绪
- market-sentiment-pulse
  - 输出：基础情绪评分（仅作辅助，不单独作为交易依据）

## 15:30 补充报告执行顺序
1. funding-rate-scanner：是否出现新一轮 funding 异动
2. hyperliquid：OI / funding / volume 是否显著变化
3. crypto-whale-monitor：是否出现新增鲸鱼异动
4. polymarket-wallet-xray / polyedge：预测市场钱包/相关性是否出现新增变化
5. market-sentiment-pulse：补充轻量情绪变化

## 输出结构
1. 今日新增重大事件 / 热点事件
2. 资金流向判断
3. 加密市场：主交易标的 / 高弹性标的 / 观察标的
4. 港美股市场：主交易标的 / 高弹性标的 / 观察标的
5. 大宗商品：主交易标的 / 观察标的
6. 预测市场：主交易标的 / 观察标的
7. 风险提示

## 使用原则
- 6 个 Skill 作为“证据层”和“信号层”，服务于投研判断
- 不因为某一个 Skill 的单点输出直接下结论
- market-sentiment-pulse 仅作辅助参考
- polymarket-wallet-xray / polyedge 偏预测市场补充，不替代主市场判断

## 当前限制
- 暂无清算热图 / 流动性热区专门能力
- 暂无完整自动化“市场是否相信”闭环
- mobula 暂未接入
