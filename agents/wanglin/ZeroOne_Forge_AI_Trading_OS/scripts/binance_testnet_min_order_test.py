"""
币安合约测试网最小下单测试脚本（10 USDT DOGE 开多 → 立即平仓）

用途：验证你的测试网 Key 真的能"写"——不只是查询，还能下单 + 平仓。
DOGEUSDT 选作 hello-world 标的因为最小下单量小、流动性好。

【安全保障】
- 强制校验 base_url 必须是测试网（含 "testnet"），否则拒绝执行
- 名义金额硬编码 10 USDT（约等于一杯咖啡的钱，但用的是测试网假币）
- 自动识别仓位模式（单向 / 双向），生成对应的下单参数
- 平仓使用 reduceOnly（单向模式）或 positionSide（双向模式），杜绝意外反向开仓

【运行方式】（从仓库根目录）
    agents/wanglin/ZeroOne_Forge_AI_Trading_OS/.venv/bin/python \\
        agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/binance_testnet_min_order_test.py

【输出】
- 终端打印每一步状态
- 完整请求 / 响应记录写入：
  data/market_os_stage1/execution_layer/binance_testnet_min_order_<timestamp>.json
"""

import json
import time
import hmac
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from decimal import Decimal, ROUND_UP, ROUND_DOWN, getcontext

getcontext().prec = 28


# 自动定位仓库（脚本在 repo/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/ 下）
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[4]
CREDENTIAL_PATH = REPO_ROOT / "agents" / "wanglin" / ".binance_futures_api.testnet.json"
EXECUTION_LAYER_DIR = (
    REPO_ROOT
    / "agents" / "wanglin" / "ZeroOne_Forge_AI_Trading_OS"
    / "data" / "market_os_stage1" / "execution_layer"
)

SYMBOL = "DOGEUSDT"
TARGET_NOTIONAL_USDT = Decimal("10")
SLEEP_SECONDS_BEFORE_CLOSE = 2  # 开仓和平仓之间的间隔


# ---------- 工具函数 ----------

def load_credentials():
    """读取测试网凭证。失败时给出清晰错误指引。"""
    if not CREDENTIAL_PATH.exists():
        raise FileNotFoundError(f"凭证文件不存在：{CREDENTIAL_PATH}")
    cred = json.loads(CREDENTIAL_PATH.read_text())
    if "在这里粘贴" in cred.get("apiKey", "") or "在这里粘贴" in cred.get("apiSecret", ""):
        raise ValueError(f"凭证文件还是模板内容，请先填入真实 Key：{CREDENTIAL_PATH}")
    return cred


def public_request(base_url: str, path: str, params: dict | None = None):
    """无签名 GET（用于行情/规则查询）"""
    qs = urllib.parse.urlencode(params or {})
    url = f"{base_url}{path}" + (f"?{qs}" if qs else "")
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode())


def signed_request(
    base_url: str, api_key: str, api_secret: str,
    method: str, path: str, params: dict
):
    """带签名的请求（账户/下单/查询自己持仓 等需要权限的接口）"""
    params = dict(params)
    params["timestamp"] = int(time.time() * 1000)
    params["recvWindow"] = 60000
    qs = urllib.parse.urlencode(params)
    sig = hmac.new(api_secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{qs}&signature={sig}"
    req = urllib.request.Request(url, method=method, headers={"X-MBX-APIKEY": api_key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", errors="replace"))


def calc_quantity(target_notional: Decimal, price: Decimal, step: Decimal, min_qty: Decimal) -> str:
    """根据目标名义金额，按交易对的步长向上取整算下单数量。"""
    raw_qty = target_notional / price
    steps = (raw_qty / step).to_integral_value(rounding=ROUND_UP)
    qty = steps * step
    if qty < min_qty:
        qty = min_qty
    qty = qty.quantize(step, rounding=ROUND_DOWN)
    return format(qty, "f")


def wait_for_fill(base_url, api_key, api_secret, symbol, order_id, max_wait_sec=5):
    """轮询查询订单状态，直到 FILLED 或超时（市价单几乎瞬时成交）。"""
    deadline = time.time() + max_wait_sec
    last_body = None
    while time.time() < deadline:
        status, body = signed_request(
            base_url, api_key, api_secret, "GET", "/fapi/v1/order",
            {"symbol": symbol, "orderId": order_id}
        )
        last_body = body
        if status == 200 and body.get("status") == "FILLED":
            return body
        time.sleep(0.3)
    return last_body  # 超时也返回最后一次状态供调用方决策


# ---------- 主流程 ----------

def main():
    print("=" * 64)
    print(f"币安合约测试网 · 最小下单测试")
    print(f"标的：{SYMBOL}   目标名义额：{TARGET_NOTIONAL_USDT} USDT")
    print("=" * 64)

    # 0. 读凭证 + 安全检查
    cred = load_credentials()
    api_key = cred["apiKey"]
    api_secret = cred["apiSecret"]
    base_url = cred.get("base_url", "https://testnet.binancefuture.com")

    if "testnet" not in base_url.lower():
        raise RuntimeError(
            f"❌ 安全检查失败：base_url 不含 'testnet' ({base_url})。\n"
            f"   拒绝执行——这个脚本只能在测试网跑。"
        )
    print(f"\n[0] 安全检查 ✅  base_url = {base_url}")

    # 1. 查仓位模式（单向 vs 双向）
    print(f"\n[1/6] 查询仓位模式（dualSidePosition）...")
    mode_status, mode_body = signed_request(
        base_url, api_key, api_secret, "GET", "/fapi/v1/positionSide/dual", {}
    )
    if mode_status != 200:
        print(f"      ❌ 查询失败 HTTP {mode_status}: {mode_body}")
        return
    is_hedge_mode = bool(mode_body.get("dualSidePosition"))
    print(f"      仓位模式：{'双向（hedge）' if is_hedge_mode else '单向（one-way，默认）'}")

    # 2. 查当前价
    print(f"\n[2/6] 查询 {SYMBOL} 当前价...")
    ticker = public_request(base_url, "/fapi/v1/ticker/price", {"symbol": SYMBOL})
    price = Decimal(ticker["price"])
    print(f"      当前价：{price} USDT")

    # 3. 查交易对规则
    # 注意：测试网的 ?symbol= 过滤参数不可靠，会返回错的交易对，所以拉全部再客户端过滤
    print(f"\n[3/6] 查询 {SYMBOL} 交易规则（市价单优先用 MARKET_LOT_SIZE）...")
    all_info = public_request(base_url, "/fapi/v1/exchangeInfo")
    sym_info = next((s for s in all_info["symbols"] if s["symbol"] == SYMBOL), None)
    if sym_info is None:
        raise RuntimeError(f"{SYMBOL} 在测试网不存在")

    # 市价单的步长由 MARKET_LOT_SIZE 决定，回退到 LOT_SIZE
    step = Decimal("1")
    min_qty = Decimal("1")
    min_notional = Decimal("5")
    for f in sym_info["filters"]:
        if f["filterType"] == "MARKET_LOT_SIZE":
            step = Decimal(f["stepSize"])
            min_qty = Decimal(f["minQty"])
        elif f["filterType"] == "MIN_NOTIONAL":
            min_notional = Decimal(f["notional"])
    qty_str = calc_quantity(TARGET_NOTIONAL_USDT, price, step, min_qty)
    notional = Decimal(qty_str) * price
    print(f"      步长 {step}，最小数量 {min_qty}，最低名义额 {min_notional} USDT")
    print(f"      → 计算下单量：{qty_str}（≈ {notional} USDT）")
    if notional < min_notional:
        raise RuntimeError(
            f"目标名义额 {notional} 低于交易对最低 {min_notional} USDT，请把 TARGET_NOTIONAL_USDT 调高。"
        )

    # 4. 开多单
    print(f"\n[4/6] 开多单（MARKET BUY）...")
    open_params = {
        "symbol": SYMBOL,
        "side": "BUY",
        "type": "MARKET",
        "quantity": qty_str,
    }
    if is_hedge_mode:
        open_params["positionSide"] = "LONG"
    open_status, open_body = signed_request(
        base_url, api_key, api_secret, "POST", "/fapi/v1/order", open_params
    )
    print(f"      HTTP {open_status}")
    if open_status != 200:
        print(f"      ❌ 开单失败：{open_body}")
        _save_report(SYMBOL, price, step, min_qty, qty_str, notional, is_hedge_mode,
                     open_status, open_body, None, None, base_url)
        return
    open_order_id = open_body.get("orderId")
    print(f"      ✅ 订单 ID：{open_order_id}（已接受）")
    # 市价单需要查询才能拿到实际成交价（开始响应只是 ACK）
    open_body = wait_for_fill(base_url, api_key, api_secret, SYMBOL, open_order_id)
    print(f"      成交均价：{open_body.get('avgPrice')}")
    print(f"      实际成交：{open_body.get('executedQty')} / {open_body.get('origQty')}")
    print(f"      状态：{open_body.get('status')}")

    # 5. 等待 N 秒
    print(f"\n[5/6] 等待 {SLEEP_SECONDS_BEFORE_CLOSE} 秒后平仓...")
    time.sleep(SLEEP_SECONDS_BEFORE_CLOSE)

    # 6. 平仓
    print(f"\n[6/6] 平仓（MARKET SELL）...")
    close_params = {
        "symbol": SYMBOL,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty_str,
    }
    if is_hedge_mode:
        close_params["positionSide"] = "LONG"  # 双向模式：平 LONG 仓位
    else:
        close_params["reduceOnly"] = "true"   # 单向模式：reduceOnly 防止意外反向开仓
    close_status, close_body = signed_request(
        base_url, api_key, api_secret, "POST", "/fapi/v1/order", close_params
    )
    print(f"      HTTP {close_status}")
    if close_status != 200:
        print(f"      ❌ 平仓失败：{close_body}")
        print(f"      ⚠️  注意：开多单已成交，但平仓未成功，请去测试网手动平仓！")
        _save_report(SYMBOL, price, step, min_qty, qty_str, notional, is_hedge_mode,
                     open_status, open_body, close_status, close_body, base_url)
        return
    close_order_id = close_body.get("orderId")
    print(f"      ✅ 订单 ID：{close_order_id}（已接受）")
    close_body = wait_for_fill(base_url, api_key, api_secret, SYMBOL, close_order_id)
    print(f"      成交均价：{close_body.get('avgPrice')}")
    print(f"      实际成交：{close_body.get('executedQty')} / {close_body.get('origQty')}")
    print(f"      状态：{close_body.get('status')}")

    # 写报告
    report_path = _save_report(
        SYMBOL, price, step, min_qty, qty_str, notional, is_hedge_mode,
        open_status, open_body, close_status, close_body, base_url,
    )

    # 简单收益计算（仅供观察，未扣手续费）
    open_avg = Decimal(open_body.get("avgPrice", "0") or "0")
    close_avg = Decimal(close_body.get("avgPrice", "0") or "0")
    qty_dec = Decimal(qty_str)
    if open_avg > 0 and close_avg > 0:
        gross_pnl = (close_avg - open_avg) * qty_dec
        print(f"\n      毛盈亏（不计手续费）：{gross_pnl:+.6f} USDT")
        print(f"      （测试网开平这种瞬时单几乎都是 0±手续费）")

    print("\n" + "=" * 64)
    print("✅ 测试网最小下单 + 平仓完成")
    print(f"📝 完整记录已写入：{report_path.relative_to(REPO_ROOT)}")
    print("=" * 64)


def _save_report(symbol, price, step, min_qty, qty_str, notional, is_hedge_mode,
                 open_status, open_body, close_status, close_body, base_url):
    """把整个测试结果写入执行层目录。"""
    EXECUTION_LAYER_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_for_filename = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    report = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "network": "testnet",
        "base_url": base_url,
        "symbol": symbol,
        "position_mode": "hedge" if is_hedge_mode else "one_way",
        "price_at_test": format(price, "f"),
        "step_size": format(step, "f"),
        "min_qty": format(min_qty, "f"),
        "quantity": qty_str,
        "notional_usdt": format(notional, "f"),
        "open_order": {"http_status": open_status, "body": open_body},
        "close_order": {"http_status": close_status, "body": close_body} if close_status else None,
    }
    report_path = EXECUTION_LAYER_DIR / f"binance_testnet_min_order_{timestamp_for_filename}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report_path


if __name__ == "__main__":
    main()
