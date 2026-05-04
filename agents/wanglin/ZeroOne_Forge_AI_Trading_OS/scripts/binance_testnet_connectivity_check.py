"""
币安合约测试网连通性检查脚本（只读，不下任何订单）

用途：验证你的测试网 API Key 能正常调用 Binance API。
脚本只调用账户查询接口，不会下单、不会改任何账户状态。

运行方式（从仓库根目录）：
    .venv/bin/python agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/binance_testnet_connectivity_check.py

凭证文件位置（必须先创建）：
    agents/wanglin/.binance_futures_api.testnet.json
    （格式参考同目录下的 .example 文件，不要把真实文件提交到 git）
"""

import json
import time
import hmac
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path


# 自动定位仓库根目录（这个脚本在 repo/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/ 下）
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[4]
CREDENTIAL_PATH = REPO_ROOT / "agents" / "wanglin" / ".binance_futures_api.testnet.json"


def load_credentials():
    """读取测试网凭证文件。失败时给出清晰错误指引。"""
    if not CREDENTIAL_PATH.exists():
        raise FileNotFoundError(
            f"\n找不到凭证文件：{CREDENTIAL_PATH}\n"
            f"请按下面步骤创建：\n"
            f"  1. cp {CREDENTIAL_PATH}.example {CREDENTIAL_PATH}\n"
            f"  2. 用文本编辑器打开 {CREDENTIAL_PATH}\n"
            f"  3. 把 apiKey 和 apiSecret 替换成你的真实测试网 Key\n"
        )
    cred = json.loads(CREDENTIAL_PATH.read_text())
    if "在这里粘贴" in cred.get("apiKey", "") or "在这里粘贴" in cred.get("apiSecret", ""):
        raise ValueError(
            f"\n凭证文件还是模板内容，没填真实 Key。\n"
            f"请编辑：{CREDENTIAL_PATH}\n"
        )
    return cred


def signed_get(base_url: str, api_key: str, api_secret: str, path: str, params: dict | None = None):
    """对 Binance 测试网做签名 GET 请求。返回 (status_code, json_body)。"""
    params = dict(params or {})
    params["timestamp"] = int(time.time() * 1000)
    params["recvWindow"] = 60000
    qs = urllib.parse.urlencode(params)
    sig = hmac.new(api_secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{qs}&signature={sig}"
    req = urllib.request.Request(url, method="GET", headers={"X-MBX-APIKEY": api_key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", errors="replace"))


def main():
    print("=" * 60)
    print("币安合约测试网 · 连通性检查（只读，不下单）")
    print("=" * 60)

    # 步骤 1：读凭证
    try:
        cred = load_credentials()
    except (FileNotFoundError, ValueError) as e:
        print(f"\n❌ 凭证加载失败：{e}")
        return

    api_key = cred["apiKey"]
    api_secret = cred["apiSecret"]
    base_url = cred.get("base_url", "https://testnet.binancefuture.com")

    # 不打印 Key 本身，只打印长度和前后 4 位用于核对
    print(f"\n[1/3] 凭证读取 OK")
    print(f"      Key 长度：{len(api_key)}（应为 64）")
    print(f"      Key 头尾：{api_key[:4]}...{api_key[-4:]}")
    print(f"      Network：{cred.get('network', 'testnet')}")
    print(f"      Base URL：{base_url}")

    # 步骤 2：调用账户余额接口（只读）
    print(f"\n[2/3] 调用账户余额接口 /fapi/v2/balance ...")
    status, body = signed_get(base_url, api_key, api_secret, "/fapi/v2/balance")

    if status != 200:
        print(f"      ❌ 请求失败 HTTP {status}")
        print(f"      返回内容：{body}")
        if body.get("code") == -2014 or body.get("code") == -2015:
            print(f"\n      → API Key 格式或权限有误。检查测试网创建 Key 时是否勾选了'启用合约'权限。")
        elif body.get("code") == -1022:
            print(f"\n      → 签名错误。Secret Key 可能复制错了。")
        return

    print(f"      ✅ HTTP 200，账户余额条目数：{len(body)}")

    # 找到 USDT 余额
    usdt = next((b for b in body if b.get("asset") == "USDT"), None)
    if usdt:
        print(f"      USDT 可用余额：{usdt.get('availableBalance')}")
        print(f"      USDT 总余额：  {usdt.get('balance')}")
    else:
        print(f"      （账户中暂无 USDT 余额，测试网应该自动给 10000 USDT，可能需要在测试网点 'Get test funds'）")

    # 步骤 3：调用账户信息接口
    print(f"\n[3/3] 调用账户信息接口 /fapi/v2/account ...")
    status, body = signed_get(base_url, api_key, api_secret, "/fapi/v2/account")

    if status != 200:
        print(f"      ❌ HTTP {status}：{body}")
        return

    print(f"      ✅ HTTP 200")
    print(f"      账户总权益：{body.get('totalWalletBalance')} USDT")
    print(f"      未实现盈亏：{body.get('totalUnrealizedProfit')}")
    print(f"      可用保证金：{body.get('availableBalance')}")
    print(f"      持仓数量：  {sum(1 for p in body.get('positions', []) if float(p.get('positionAmt', 0)) != 0)}")

    print("\n" + "=" * 60)
    print("✅ 连通性测试全部通过。下一步可以做测试网下单。")
    print("=" * 60)


if __name__ == "__main__":
    main()
