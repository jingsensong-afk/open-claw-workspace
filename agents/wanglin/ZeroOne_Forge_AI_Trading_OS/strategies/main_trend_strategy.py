"""
ZeroOne Forge · MainTrendStrategy v1（Day 5 Step 3）

【定位】
双系统架构中的"Main 主系统"——专做 BTC/ETH 等主流币的小时线中频趋势捕捉。
v1 仅多头，仅 BTC/USDT 与 ETH/USDT 永续合约，testnet dry-run。

【4 段结构（按 Codex Step 3 spec）】
1. Indicators：Donchian 通道（带 .shift(1) 防 lookahead）+ ATR + funding rate
2. Signal intent：在 populate_entry_trend 中标记候选多头 K 线
3. Risk approval：custom_stake_amount 计算 R 单位仓位 + confirm_trade_entry 调用风控 gate
4. Freqtrade signal：只有风控批准的订单才会被实际下出去

【硬约束】
- 任何 entry 前必须经 risk.validate_order()，拒绝则取消
- 仓位计算用 0.8 × risk_per_trade_pct（留 0.2 buffer 给手续费 + 滑点）
- ATR-based 动态止损（custom_stoploss）
- 不做 short（v1 only_long）

【降级（degraded）说明】
- daily_realized_pnl: v1 暂用 0（Freqtrade 不直接暴露当日 PnL，需要 Step 4 加聚合）
- open_positions_count: v1 暂用 0
- funding_rate: 回测时为 0（历史 funding 接入 Step 5 数据下载阶段再补）
- 这些将在后续 step 通过 Freqtrade dataprovider / wallet API 补全
"""

from __future__ import annotations

import logging
import sys
from decimal import Decimal
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy

# 让本文件能 import 我们的 risk 模块（risk/ 与 strategies/ 是兄弟目录）
_HERE = Path(__file__).resolve().parent
_WANGLIN_OS_ROOT = _HERE.parent
if str(_WANGLIN_OS_ROOT) not in sys.path:
    sys.path.insert(0, str(_WANGLIN_OS_ROOT))

from risk import (  # noqa: E402  (sys.path setup must come first)
    AccountState,
    ProposedOrder,
    RiskLimits,
    load_risk_limits,
    validate_order,
)

logger = logging.getLogger(__name__)

# 策略所在 OS 的 freqtrade 配置文件路径（risk gate 与策略读同一份 config）
_CONFIG_PATH = _WANGLIN_OS_ROOT / "config" / "freqtrade_main_dryrun.json"


class MainTrendStrategy(IStrategy):
    """主趋势突破策略（小时线 Donchian + ATR + funding 过滤 + 强制风控）。"""

    # ---------- Freqtrade 接口元数据 ----------
    INTERFACE_VERSION = 3
    timeframe = "1h"
    can_short = False                          # v1 仅多头
    process_only_new_candles = True
    use_exit_signal = False                    # 不用 populate_exit_trend，靠 custom_stoploss
    use_custom_stoploss = True
    startup_candle_count = 50                  # 让 Donchian / ATR 有足够 lookback

    # 安全网止损（实际由 custom_stoploss 决定，这是保险底）
    stoploss = -0.05

    # 不开启 trailing stop（v1 简化）
    trailing_stop = False

    # 订单类型
    order_types = {
        "entry": "limit",
        "exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC",
    }

    # ---------- 策略层可调参数 ----------
    DONCHIAN_PERIOD = 20
    ATR_PERIOD = 14
    STOP_LOSS_ATR_MULT = Decimal("2.0")
    FUNDING_THRESHOLD_LONG = Decimal("0.0005")  # +0.05% 8h funding 上限
    SIZING_BUFFER = Decimal("0.8")              # 实际只用 0.8 × risk_per_trade_pct（buffer for fee/slippage）

    # v1 标的白名单（与 config / risk_control.DEFAULT_ALLOWED_PAIRS 一致）
    ALLOWED_SYMBOLS = frozenset({"BTC/USDT:USDT", "ETH/USDT:USDT"})

    # ---------- 运行时状态 ----------
    _risk_limits: Optional[RiskLimits] = None

    # ============================================================
    # 1. 生命周期
    # ============================================================

    def bot_start(self, **kwargs) -> None:
        """Freqtrade 启动时调用一次。从 config 加载风控上限。"""
        try:
            self._risk_limits = load_risk_limits(_CONFIG_PATH)
            logger.info(
                f"[MainTrendStrategy] risk limits loaded: "
                f"leverage≤{self._risk_limits.max_leverage_cap} / "
                f"risk≤{self._risk_limits.risk_per_trade_pct} / "
                f"halt≤{self._risk_limits.daily_loss_halt_pct}"
            )
        except Exception as e:
            logger.error(
                f"[MainTrendStrategy] FATAL: 加载风控上限失败 ({e})；策略不启动。"
            )
            raise

    # ============================================================
    # 2. Indicators · Donchian + ATR + funding
    # ============================================================

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """计算技术指标。注意所有突破信号必须用 .shift(1) 防 lookahead。"""

        # Donchian 通道（基于过去 N 根已收盘 K 线，所以 .shift(1)）
        dataframe["donchian_upper"] = (
            dataframe["high"].rolling(self.DONCHIAN_PERIOD).max().shift(1)
        )
        dataframe["donchian_lower"] = (
            dataframe["low"].rolling(self.DONCHIAN_PERIOD).min().shift(1)
        )

        # ATR · True Range = max(H-L, |H-C₋₁|, |L-C₋₁|)
        prev_close = dataframe["close"].shift(1)
        tr = pd.concat(
            [
                dataframe["high"] - dataframe["low"],
                (dataframe["high"] - prev_close).abs(),
                (dataframe["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        dataframe["atr"] = tr.rolling(self.ATR_PERIOD).mean()

        # Funding rate（v1 degraded：回测时暂为 0；live/dry-run 时尽量从 dataprovider 拉）
        # Step 5 补完整历史 funding 数据下载后，本字段会有真实值
        funding_rate = 0.0
        try:
            if self.dp is not None and metadata.get("pair"):
                # 仅在 live/dry-run 模式下尝试拉
                if self.dp.runmode.value in ("live", "dry_run"):
                    rate_info = self.dp.exchange.fetch_funding_rate(metadata["pair"])
                    funding_rate = float(rate_info.get("fundingRate") or 0.0)
        except Exception as e:
            logger.debug(f"[MainTrendStrategy] funding_rate 获取失败（degraded to 0）: {e}")
            funding_rate = 0.0
        dataframe["funding_rate"] = funding_rate

        return dataframe

    # ============================================================
    # 3. Signal intent · 标记候选多头 K 线
    # ============================================================

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """标记 entry 候选。最终是否真下单由 confirm_trade_entry + risk gate 决定。"""

        dataframe["enter_long"] = 0

        # 标的白名单（防御深度，preflight + risk gate 都已检查）
        pair = metadata.get("pair", "")
        if pair not in self.ALLOWED_SYMBOLS:
            return dataframe

        # 突破信号：收盘价突破 Donchian 上轨（不含本根 = 已 .shift(1)）
        upper = dataframe["donchian_upper"]
        breakout = (dataframe["close"] > upper) & upper.notna()

        # Funding rate 过滤（多头方向）
        funding_ok = dataframe["funding_rate"] <= float(self.FUNDING_THRESHOLD_LONG)

        # ATR 必须有效（否则没法算止损）
        atr_ok = dataframe["atr"].notna() & (dataframe["atr"] > 0)

        candidate = breakout & funding_ok & atr_ok
        dataframe.loc[candidate, "enter_long"] = 1
        dataframe.loc[candidate, "enter_tag"] = "donchian_breakout"

        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """v1 不用 exit signal，全靠 custom_stoploss 触发出场。"""
        dataframe["exit_long"] = 0
        return dataframe

    # ============================================================
    # 4. Risk approval · 仓位计算 + 强制 risk gate
    # ============================================================

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        """根据 R 单位 + ATR 止损距离计算仓位（USDT 名义额）。
        Codex 要求：用 0.8 × risk_per_trade_pct，保留 buffer 给手续费/滑点。"""

        if self._risk_limits is None:
            logger.warning(f"[{pair}] risk_limits 未加载，拒绝下单")
            return 0.0

        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            return 0.0

        last_atr = df["atr"].iloc[-1]
        if pd.isna(last_atr) or last_atr <= 0:
            logger.debug(f"[{pair}] ATR 无效，跳过下单")
            return 0.0

        # 止损距离（绝对值）= ATR × multiplier
        stop_distance_abs = float(self.STOP_LOSS_ATR_MULT) * float(last_atr)
        stop_distance_pct = stop_distance_abs / current_rate
        if stop_distance_pct <= 0:
            return 0.0

        # 总权益（用 stake_currency 衡量）
        wallet_total = self.wallets.get_total(self.config["stake_currency"])
        if wallet_total <= 0:
            return 0.0

        # 实际风险预算（含 sizing buffer）
        effective_risk_pct = float(self._risk_limits.risk_per_trade_pct) * float(self.SIZING_BUFFER)
        risk_budget_usdt = wallet_total * effective_risk_pct

        # 仓位名义额 = 风险预算 / 止损距离百分比
        # 数学：quantity = risk_budget / stop_distance_abs
        #       notional  = quantity × current_rate = risk_budget / stop_distance_pct
        stake_usdt = risk_budget_usdt / stop_distance_pct

        # Freqtrade 限制
        if max_stake and stake_usdt > max_stake:
            stake_usdt = max_stake
        if min_stake and stake_usdt < min_stake:
            logger.debug(
                f"[{pair}] 计算仓位 {stake_usdt:.2f} 低于 min_stake {min_stake}，跳过"
            )
            return 0.0

        logger.info(
            f"[{pair}] 仓位计算：R预算={risk_budget_usdt:.2f}USDT · "
            f"止损距 {stop_distance_pct*100:.3f}% · 名义额 {stake_usdt:.2f}USDT"
        )
        return stake_usdt

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> bool:
        """Freqtrade 在真实下单前最后一道关卡。**强制经过 risk gate**。"""

        if self._risk_limits is None:
            logger.error(f"[{pair}] risk_limits 未加载，拒绝下单")
            return False

        if pair not in self.ALLOWED_SYMBOLS:
            logger.error(f"[{pair}] 不在策略白名单，拒绝下单")
            return False

        if side != "long":
            logger.error(f"[{pair}] v1 仅多头，收到 side={side}")
            return False

        # 重新算止损（与 custom_stake_amount / custom_stoploss 同源）
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            logger.error(f"[{pair}] dataframe 为空，拒绝下单")
            return False
        last_atr = df["atr"].iloc[-1]
        if pd.isna(last_atr) or last_atr <= 0:
            logger.error(f"[{pair}] ATR 无效，拒绝下单")
            return False

        entry_price = Decimal(str(rate))
        stop_distance = Decimal(str(self.STOP_LOSS_ATR_MULT)) * Decimal(str(last_atr))
        stop_loss_price = entry_price - stop_distance

        # 账户状态（v1 degraded：daily_realized_pnl 与 open_positions_count 暂未完整接入）
        wallet_total = self.wallets.get_total(self.config["stake_currency"])
        account = AccountState(
            total_equity=Decimal(str(wallet_total)),
            available_balance=Decimal(str(wallet_total)),
            daily_realized_pnl=Decimal("0"),       # TODO Step 4: 接入当日 PnL 聚合
            open_positions_count=len(Trade.get_open_trades()),
        )

        # 当前杠杆使用情况（保守取 config 的 max_leverage_cap，由 gate 校验）
        current_leverage = Decimal(str(self.config.get("max_leverage_cap", 5)))

        proposed = ProposedOrder(
            symbol=pair,
            side="long",
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            quantity=Decimal(str(amount)),
            leverage=current_leverage,
        )

        # 调用风控 gate（fail closed）
        decision = validate_order(proposed, account, self._risk_limits)
        if not decision.approved:
            logger.warning(
                f"[{pair}] 🛑 RISK GATE 拒绝 entry · "
                f"{len(decision.reasons)} 条原因：{list(decision.reasons)}"
            )
            return False

        logger.info(
            f"[{pair}] ✅ RISK GATE 批准 entry · "
            f"price={rate} qty={amount} stop={stop_loss_price}"
        )
        return True

    # ============================================================
    # 5. 动态止损 · ATR-based custom_stoploss
    # ============================================================

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> float:
        """ATR 倍数动态止损。返回 -0.02 表示在入场价下方 2% 止损。

        Freqtrade 约定 custom_stoploss 返回值是相对**入场价**的负百分比。
        """
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            return self.stoploss

        last_atr = df["atr"].iloc[-1]
        if pd.isna(last_atr) or last_atr <= 0:
            return self.stoploss

        # 距入场价的止损距离百分比
        stop_distance_pct = (float(self.STOP_LOSS_ATR_MULT) * float(last_atr)) / trade.open_rate

        # 限制不要太宽（万一 ATR 异常爆掉），上限 5%
        max_stop_pct = abs(self.stoploss)
        stop_distance_pct = min(stop_distance_pct, max_stop_pct)

        # Freqtrade 期待负百分比
        return -stop_distance_pct
