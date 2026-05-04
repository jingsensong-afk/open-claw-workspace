import argparse
import json
import os
import sys
import time
import hmac
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from decimal import Decimal, ROUND_UP, ROUND_DOWN, getcontext

getcontext().prec = 28

ROOT = Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS')
CREDENTIAL_PATH = Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/.binance_futures_api.json')
BASE_URL = 'https://fapi.binance.com'
SYMBOL = 'DOGEUSDT'
POSITION_SIDE = 'LONG'
SIDE = 'BUY'
TARGET_NOTIONAL = Decimal('10')
SLEEP_SECONDS_BEFORE_CLOSE = 2


def parse_args():
    parser = argparse.ArgumentParser(
        description='DANGEROUS: Binance Futures mainnet minimum order test.'
    )
    parser.add_argument(
        '--i-understand-mainnet',
        action='store_true',
        help='Required. Confirms this script sends real Binance Futures mainnet orders.',
    )
    return parser.parse_args()


def enforce_manual_mainnet_guard(args):
    if not args.i_understand_mainnet:
        print(
            'Refusing to run: missing --i-understand-mainnet. '
            'This script can send real Binance Futures mainnet orders.',
            file=sys.stderr,
        )
        sys.exit(2)
    if os.environ.get('LIVE_TRADING') != '1':
        print(
            'Refusing to run: LIVE_TRADING=1 is required. '
            'No network request was sent.',
            file=sys.stderr,
        )
        sys.exit(2)


def signed_request(method, path, params, key, secret):
    params['timestamp'] = int(time.time() * 1000)
    params['recvWindow'] = 60000
    qs = urllib.parse.urlencode(params)
    sig = hmac.new(secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
    url = BASE_URL + path + '?' + qs + '&signature=' + sig
    req = urllib.request.Request(url, method=method, headers={'X-MBX-APIKEY': key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8', errors='replace'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8', errors='replace'))


def main():
    args = parse_args()
    enforce_manual_mainnet_guard(args)

    print('DANGER: Binance Futures MAINNET order test.')
    print('This script will send a real MARKET BUY, wait briefly, then send a real MARKET SELL reduceOnly close.')
    print(f'Symbol: {SYMBOL}; target notional: {TARGET_NOTIONAL} USDT; base URL: {BASE_URL}')

    cred = json.loads(CREDENTIAL_PATH.read_text())
    key = cred['apiKey']
    secret = cred['apiSecret']

    with urllib.request.urlopen(f'{BASE_URL}/fapi/v1/ticker/price?symbol={SYMBOL}', timeout=20) as resp:
        price = Decimal(json.loads(resp.read().decode())['price'])

    with urllib.request.urlopen(f'{BASE_URL}/fapi/v1/exchangeInfo?symbol={SYMBOL}', timeout=20) as resp:
        info = json.loads(resp.read().decode())['symbols'][0]

    step = Decimal('0.001')
    min_qty = Decimal('0.001')
    for f in info['filters']:
        if f['filterType'] == 'LOT_SIZE':
            step = Decimal(f['stepSize'])
            min_qty = Decimal(f['minQty'])

    # Target 10U notional, round UP to step grid, then quantize exactly to step exponent.
    raw_qty = (TARGET_NOTIONAL / price)
    steps = (raw_qty / step).to_integral_value(rounding=ROUND_UP)
    qty = steps * step
    if qty < min_qty:
        qty = min_qty
    qty = qty.quantize(step, rounding=ROUND_DOWN)
    qty_str = format(qty, 'f')

    open_status, open_body = signed_request('POST', '/fapi/v1/order', {
        'symbol': SYMBOL,
        'side': SIDE,
        'positionSide': POSITION_SIDE,
        'type': 'MARKET',
        'quantity': qty_str
    }, key, secret)

    time.sleep(SLEEP_SECONDS_BEFORE_CLOSE)
    close_status, close_body = signed_request('POST', '/fapi/v1/order', {
        'symbol': SYMBOL,
        'side': 'SELL',
        'positionSide': POSITION_SIDE,
        'type': 'MARKET',
        'quantity': qty_str,
        'reduceOnly': 'true'
    }, key, secret)

    report = {
        'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'symbol': SYMBOL,
        'price': format(price, 'f'),
        'step': format(step, 'f'),
        'min_qty': format(min_qty, 'f'),
        'quantity': qty_str,
        'open_order': {'status': open_status, 'body': open_body},
        'close_order': {'status': close_status, 'body': close_body}
    }
    (ROOT / 'data/market_os_stage1/execution_layer/binance_futures_live_min_test_precision_fixed_2026-04-26.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
