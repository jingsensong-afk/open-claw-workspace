import json, time, hmac, hashlib, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from decimal import Decimal, ROUND_UP, ROUND_DOWN, getcontext

getcontext().prec = 28

root = Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS')
cred = json.loads(Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/.binance_futures_api.json').read_text())
key = cred['apiKey']
secret = cred['apiSecret']
base = 'https://fapi.binance.com'
symbol = 'DOGEUSDT'
position_side = 'LONG'
side = 'BUY'

def signed_request(method, path, params):
    params['timestamp'] = int(time.time() * 1000)
    params['recvWindow'] = 60000
    qs = urllib.parse.urlencode(params)
    sig = hmac.new(secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
    url = base + path + '?' + qs + '&signature=' + sig
    req = urllib.request.Request(url, method=method, headers={'X-MBX-APIKEY': key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8', errors='replace'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8', errors='replace'))

with urllib.request.urlopen(f'https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}', timeout=20) as resp:
    price = Decimal(json.loads(resp.read().decode())['price'])

with urllib.request.urlopen(f'https://fapi.binance.com/fapi/v1/exchangeInfo?symbol={symbol}', timeout=20) as resp:
    info = json.loads(resp.read().decode())['symbols'][0]

step = Decimal('0.001')
min_qty = Decimal('0.001')
for f in info['filters']:
    if f['filterType'] == 'LOT_SIZE':
        step = Decimal(f['stepSize'])
        min_qty = Decimal(f['minQty'])

# target 10U notional, round UP to step grid, then quantize exactly to step exponent
raw_qty = (Decimal('10') / price)
steps = (raw_qty / step).to_integral_value(rounding=ROUND_UP)
qty = steps * step
if qty < min_qty:
    qty = min_qty
qty = qty.quantize(step, rounding=ROUND_DOWN)
qty_str = format(qty, 'f')

open_status, open_body = signed_request('POST', '/fapi/v1/order', {
    'symbol': symbol,
    'side': side,
    'positionSide': position_side,
    'type': 'MARKET',
    'quantity': qty_str
})

time.sleep(2)
close_status, close_body = signed_request('POST', '/fapi/v1/order', {
    'symbol': symbol,
    'side': 'SELL',
    'positionSide': position_side,
    'type': 'MARKET',
    'quantity': qty_str,
    'reduceOnly': 'true'
})

report = {
    'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'symbol': symbol,
    'price': format(price, 'f'),
    'step': format(step, 'f'),
    'min_qty': format(min_qty, 'f'),
    'quantity': qty_str,
    'open_order': {'status': open_status, 'body': open_body},
    'close_order': {'status': close_status, 'body': close_body}
}
(root / 'data/market_os_stage1/execution_layer/binance_futures_live_min_test_precision_fixed_2026-04-26.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False))
