"""
持仓状态抽取（Step 4）

【职责】
把 Freqtrade Trade 对象列表（或任何具有 pair / is_open / is_short 字段的对象）
转成 risk_control 消费的 OpenPosition 元组。

【设计原则】
- 纯数据转换，无副作用
- duck typing：调用方可以传 Freqtrade Trade 实例，也可以传任何含相应字段的对象
- 异常 / 未知 side → fail closed（跳过该条）
"""

from __future__ import annotations

from typing import Iterable

from risk import OpenPosition


def extract_open_positions(trades: Iterable) -> tuple[OpenPosition, ...]:
    """从交易对象列表中抽取当前持仓的 OpenPosition 元组。

    每个 trade 对象需要有以下属性（Freqtrade Trade 自带，或自定义对象兼容）：
    - pair: str
    - is_open: bool
    - is_short: bool   （True 表示 short，False 表示 long）

    缺失字段 / 类型异常的条目会被跳过（fail closed）。
    """
    positions: list[OpenPosition] = []
    for t in trades:
        try:
            if not getattr(t, "is_open", False):
                continue
            pair = getattr(t, "pair", None)
            if not pair or not isinstance(pair, str):
                continue
            is_short = bool(getattr(t, "is_short", False))
            side = "short" if is_short else "long"
            positions.append(OpenPosition(symbol=pair, side=side))
        except Exception:
            # fail closed：异常 trade 跳过
            continue
    return tuple(positions)
