"""
ZeroOne Forge · MainTrendStrategy · Dry-Run 启动安全门（preflight）

【职责】
在 Freqtrade 启动**前**做机器可校验的硬检查。任何一条不过 → 退出码 2，
不允许 wrapper 继续启动 freqtrade。

【设计原则（来自 Codex 2026-05-05_day5_main_trend_codex_review.md）】
- 配置文件、命令行、env 任何一处被误改，都不能让"测试策略"变真实执行
- 所有检查都是**机器校验**，不依赖运行时人眼盯
- 缺一拒绝，不做"宽容兜底"
- 只读不写：本脚本不改任何文件、不发任何网络请求

【运行】
直接：
    .venv/bin/python scripts/preflight_freqtrade_main_dryrun.py

或经 wrapper：
    scripts/run_main_trend_dryrun.sh trade   # wrapper 内部先调本脚本

【退出码】
0 - 全部检查通过，可以继续启动 Freqtrade
2 - 任一检查失败（详细原因打印到 stderr）
"""

import json
import sys
from pathlib import Path
from typing import Any


# ---------- 路径常量 ----------

SCRIPT_PATH = Path(__file__).resolve()
WANGLIN_OS_ROOT = SCRIPT_PATH.parents[1]              # agents/wanglin/ZeroOne_Forge_AI_Trading_OS/
WANGLIN_PARTITION_ROOT = WANGLIN_OS_ROOT.parents[0]   # agents/wanglin/
REPO_ROOT = WANGLIN_OS_ROOT.parents[3]                # 仓库根

CONFIG_PATH = WANGLIN_OS_ROOT / "config" / "freqtrade_main_dryrun.json"
TESTNET_CRED_PATH = WANGLIN_PARTITION_ROOT / ".binance_futures_api.testnet.json"
MAINNET_CRED_PATH = WANGLIN_PARTITION_ROOT / ".binance_futures_api.json"

# 允许的标的白名单（与 config pair_whitelist 必须一致）
ALLOWED_PAIRS = {"BTC/USDT:USDT", "ETH/USDT:USDT"}

# 风控硬上限
MAX_LEVERAGE_HARD_CAP = 5
MAX_RISK_PER_TRADE_PCT = 0.01      # 单笔 1%
MAX_DAILY_LOSS_PCT = 0.03          # 日内 3%


# ---------- 工具：打印通过 / 失败 ----------

class CheckResult:
    """检查项结果聚合器。任何 fail 调用后 exit_code 会变成 2。"""

    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []

    def ok(self, name: str, detail: str = "") -> None:
        self.passed.append(f"{name}{(' · ' + detail) if detail else ''}")

    def fail(self, name: str, reason: str) -> None:
        self.failed.append(f"{name} · {reason}")

    @property
    def exit_code(self) -> int:
        return 0 if not self.failed else 2

    def render(self) -> None:
        print("=" * 64)
        print("Preflight · ZeroOne Forge MainTrendStrategy Dry-Run 启动安全门")
        print("=" * 64)
        for line in self.passed:
            print(f"  ✅ {line}")
        for line in self.failed:
            print(f"  ❌ {line}", file=sys.stderr)
        print("-" * 64)
        if self.failed:
            print(
                f"❌ {len(self.failed)} 项失败 / {len(self.passed)} 项通过 → 拒绝启动 Freqtrade",
                file=sys.stderr,
            )
        else:
            print(f"✅ {len(self.passed)} 项检查全部通过 → 可以启动 Freqtrade")
        print("=" * 64)


# ---------- 检查项实现 ----------

def check_config_exists(r: CheckResult) -> dict[str, Any] | None:
    """检查配置文件存在，返回解析后的 dict（失败返回 None）。"""
    if not CONFIG_PATH.exists():
        r.fail("config 文件存在", f"找不到 {CONFIG_PATH}")
        return None
    try:
        config = json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as e:
        r.fail("config 文件可解析", f"JSON 格式错误：{e}")
        return None
    r.ok("config 文件存在 + JSON 合法", str(CONFIG_PATH.relative_to(REPO_ROOT)))
    return config


def check_dry_run_true(r: CheckResult, config: dict[str, Any]) -> None:
    """dry_run 必须严格为 True。"""
    val = config.get("dry_run")
    if val is True:
        r.ok("dry_run === true")
    else:
        r.fail("dry_run === true", f"实际值是 {val!r}（类型 {type(val).__name__}）")


def check_sandbox_true(r: CheckResult, config: dict[str, Any]) -> None:
    """exchange.sandbox 必须严格为 True（对应 Binance testnet）。"""
    val = config.get("exchange", {}).get("sandbox")
    if val is True:
        r.ok("exchange.sandbox === true")
    else:
        r.fail("exchange.sandbox === true", f"实际值是 {val!r}")


def check_exchange_name(r: CheckResult, config: dict[str, Any]) -> None:
    """交易所必须是 binance（其他交易所 v1 不支持）。"""
    val = config.get("exchange", {}).get("name")
    if val == "binance":
        r.ok("exchange.name === binance")
    else:
        r.fail("exchange.name === binance", f"实际值是 {val!r}")


def check_pair_whitelist(r: CheckResult, config: dict[str, Any]) -> None:
    """pair 白名单只能是 BTC/USDT:USDT 和 ETH/USDT:USDT。"""
    pairs = config.get("exchange", {}).get("pair_whitelist", [])
    pairs_set = set(pairs)
    if pairs_set <= ALLOWED_PAIRS and len(pairs_set) > 0:
        r.ok("pair_whitelist 仅含 BTC/ETH", ", ".join(sorted(pairs_set)))
    else:
        forbidden = pairs_set - ALLOWED_PAIRS
        r.fail(
            "pair_whitelist 仅含 BTC/ETH",
            f"出现禁止标的 {sorted(forbidden)} 或白名单为空",
        )


def check_telegram_disabled(r: CheckResult, config: dict[str, Any]) -> None:
    """Telegram 通知 v1 必须关闭（外部分发要走独立 handoff）。"""
    enabled = config.get("telegram", {}).get("enabled", False)
    if enabled is False:
        r.ok("telegram.enabled === false")
    else:
        r.fail("telegram.enabled === false", f"实际值是 {enabled!r}")


def check_api_server_disabled(r: CheckResult, config: dict[str, Any]) -> None:
    """REST API server v1 必须关闭（无外部触发面）。"""
    enabled = config.get("api_server", {}).get("enabled", False)
    if enabled is False:
        r.ok("api_server.enabled === false")
    else:
        r.fail("api_server.enabled === false", f"实际值是 {enabled!r}")


def check_external_message_consumer_disabled(r: CheckResult, config: dict[str, Any]) -> None:
    """external_message_consumer v1 必须关闭。"""
    enabled = config.get("external_message_consumer", {}).get("enabled", False)
    if enabled is False:
        r.ok("external_message_consumer.enabled === false")
    else:
        r.fail("external_message_consumer.enabled === false", f"实际值是 {enabled!r}")


def check_no_hardcoded_credentials(r: CheckResult, config: dict[str, Any]) -> None:
    """exchange.key / exchange.secret 必须为空字符串（凭证由 wrapper 通过环境变量注入）。"""
    ex = config.get("exchange", {})
    key = ex.get("key", None)
    secret = ex.get("secret", None)
    if key == "" and secret == "":
        r.ok("exchange.key / secret 为空字符串", "凭证由 wrapper 注入 env")
    else:
        # 不打印 key/secret 内容，只说有/无
        has_key = bool(key)
        has_secret = bool(secret)
        r.fail(
            "exchange.key / secret 为空字符串",
            f"配置文件硬编码了 key={'(非空)' if has_key else key!r} secret={'(非空)' if has_secret else secret!r}",
        )


def check_leverage_cap(r: CheckResult, config: dict[str, Any]) -> None:
    """max_leverage_cap 必须 ≤ 5（硬上限）。"""
    cap = config.get("max_leverage_cap")
    if isinstance(cap, (int, float)) and 0 < cap <= MAX_LEVERAGE_HARD_CAP:
        r.ok(f"max_leverage_cap ≤ {MAX_LEVERAGE_HARD_CAP}", f"当前 {cap}")
    else:
        r.fail(
            f"max_leverage_cap ≤ {MAX_LEVERAGE_HARD_CAP}",
            f"实际值 {cap!r}（必须是 0 < cap ≤ {MAX_LEVERAGE_HARD_CAP} 的数）",
        )


def check_risk_per_trade(r: CheckResult, config: dict[str, Any]) -> None:
    """risk_per_trade_pct 必须 ≤ 1%（硬上限）。"""
    val = config.get("risk_per_trade_pct")
    if isinstance(val, (int, float)) and 0 < val <= MAX_RISK_PER_TRADE_PCT:
        r.ok(f"risk_per_trade_pct ≤ {MAX_RISK_PER_TRADE_PCT}", f"当前 {val}")
    else:
        r.fail(
            f"risk_per_trade_pct ≤ {MAX_RISK_PER_TRADE_PCT}",
            f"实际值 {val!r}",
        )


def check_daily_loss_halt(r: CheckResult, config: dict[str, Any]) -> None:
    """daily_loss_halt_pct 必须 ≤ 3%（硬上限）。"""
    val = config.get("daily_loss_halt_pct")
    if isinstance(val, (int, float)) and 0 < val <= MAX_DAILY_LOSS_PCT:
        r.ok(f"daily_loss_halt_pct ≤ {MAX_DAILY_LOSS_PCT}", f"当前 {val}")
    else:
        r.fail(
            f"daily_loss_halt_pct ≤ {MAX_DAILY_LOSS_PCT}",
            f"实际值 {val!r}",
        )


def check_trading_mode(r: CheckResult, config: dict[str, Any]) -> None:
    """trading_mode 必须是 futures（合约），margin_mode 必须是 isolated（逐仓）。"""
    tm = config.get("trading_mode")
    mm = config.get("margin_mode")
    if tm == "futures" and mm == "isolated":
        r.ok("trading_mode=futures + margin_mode=isolated")
    else:
        r.fail(
            "trading_mode=futures + margin_mode=isolated",
            f"实际 trading_mode={tm!r} margin_mode={mm!r}",
        )


def check_testnet_credentials_exist(r: CheckResult) -> None:
    """测试网凭证文件必须存在，且不是模板内容。"""
    if not TESTNET_CRED_PATH.exists():
        r.fail(
            "测试网凭证文件存在",
            f"找不到 {TESTNET_CRED_PATH.relative_to(REPO_ROOT)}",
        )
        return
    try:
        cred = json.loads(TESTNET_CRED_PATH.read_text())
    except json.JSONDecodeError as e:
        r.fail("测试网凭证文件 JSON 合法", str(e))
        return
    api_key = cred.get("apiKey", "")
    api_secret = cred.get("apiSecret", "")
    if "在这里粘贴" in api_key or "在这里粘贴" in api_secret:
        r.fail("测试网凭证已填入真实 Key", "文件还是模板内容")
        return
    if len(api_key) != 64 or len(api_secret) != 64:
        r.fail(
            "测试网凭证 Key 长度",
            f"apiKey 长度={len(api_key)} apiSecret 长度={len(api_secret)}（应为 64）",
        )
        return
    r.ok("测试网凭证文件就绪", f"{TESTNET_CRED_PATH.relative_to(REPO_ROOT)} · key 长度 64 ✓")


def check_no_mainnet_credential_leak(r: CheckResult, config: dict[str, Any]) -> None:
    """配置文件不能引用主网凭证文件路径。"""
    config_str = json.dumps(config, ensure_ascii=False)
    # 主网凭证文件名是 .binance_futures_api.json（无 testnet 后缀）
    bad_patterns = [".binance_futures_api.json", "binance_futures_api.json"]
    found = []
    for pat in bad_patterns:
        # 排除 testnet 变体（.binance_futures_api.testnet.json 是合法的）
        if pat in config_str and ".binance_futures_api.testnet.json" not in config_str.replace(pat, "X" * len(pat), 1):
            # 简化检查：精确判断 config 是否提及主网凭证（去掉测试网部分）
            stripped = config_str.replace(".binance_futures_api.testnet.json", "")
            if pat in stripped:
                found.append(pat)
                break
    if not found:
        r.ok("配置不引用主网凭证文件路径")
    else:
        r.fail(
            "配置不引用主网凭证文件路径",
            f"出现疑似主网凭证引用：{found}",
        )


def check_strategy_name(r: CheckResult, config: dict[str, Any]) -> None:
    """策略名必须是 MainTrendStrategy（v1 唯一支持的策略）。"""
    name = config.get("strategy")
    if name == "MainTrendStrategy":
        r.ok("strategy === MainTrendStrategy")
    else:
        r.fail("strategy === MainTrendStrategy", f"实际值 {name!r}")


# ---------- 主流程 ----------

def main() -> int:
    r = CheckResult()

    config = check_config_exists(r)
    if config is None:
        r.render()
        return r.exit_code

    # 配置文件层面的硬约束
    check_dry_run_true(r, config)
    check_sandbox_true(r, config)
    check_exchange_name(r, config)
    check_pair_whitelist(r, config)
    check_telegram_disabled(r, config)
    check_api_server_disabled(r, config)
    check_external_message_consumer_disabled(r, config)
    check_no_hardcoded_credentials(r, config)
    check_leverage_cap(r, config)
    check_risk_per_trade(r, config)
    check_daily_loss_halt(r, config)
    check_trading_mode(r, config)
    check_strategy_name(r, config)
    check_no_mainnet_credential_leak(r, config)

    # 凭证文件层面
    check_testnet_credentials_exist(r)

    r.render()
    return r.exit_code


if __name__ == "__main__":
    sys.exit(main())
