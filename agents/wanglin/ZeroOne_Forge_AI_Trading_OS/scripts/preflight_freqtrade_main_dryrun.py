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
    """Telegram v1 必须关闭，且 token/chat_id 必须为空字符串（防御深度，防止
    'enabled=false 但留着真 token 等未来误开' 的隐患）。"""
    tg = config.get("telegram", {})
    enabled = tg.get("enabled", False)
    token = tg.get("token", "")
    chat_id = tg.get("chat_id", "")
    if enabled is False and token == "" and chat_id == "":
        r.ok("telegram disabled + 凭证为空")
    else:
        r.fail(
            "telegram disabled + 凭证为空",
            f"enabled={enabled!r} · token{'(非空)' if token else '=空'} · chat_id{'(非空)' if chat_id else '=空'}",
        )


def check_api_server_disabled(r: CheckResult, config: dict[str, Any]) -> None:
    """REST API server v1 必须关闭，且关键字段必须是 placeholder（防御深度）。"""
    api = config.get("api_server", {})
    enabled = api.get("enabled", False)
    listen_ip = api.get("listen_ip_address", "127.0.0.1")
    enable_openapi = api.get("enable_openapi", False)
    username = api.get("username", "disabled")
    password = api.get("password", "disabled-not-used")
    jwt_secret = api.get("jwt_secret_key", "disabled-not-used")

    issues = []
    if enabled is not False:
        issues.append(f"enabled={enabled!r}")
    if listen_ip not in ("127.0.0.1", "localhost"):
        issues.append(f"listen_ip_address={listen_ip!r} (必须是 127.0.0.1 / localhost)")
    if enable_openapi is not False:
        issues.append(f"enable_openapi={enable_openapi!r}")
    if username != "disabled":
        issues.append(f"username 不是 placeholder")
    if password != "disabled-not-used":
        issues.append(f"password 不是 placeholder")
    if jwt_secret != "disabled-not-used":
        issues.append(f"jwt_secret_key 不是 placeholder")

    if not issues:
        r.ok("api_server disabled + 字段全部为 placeholder")
    else:
        r.fail("api_server disabled + 字段全部为 placeholder", "; ".join(issues))


def check_external_message_consumer_disabled(r: CheckResult, config: dict[str, Any]) -> None:
    """external_message_consumer v1 必须关闭。"""
    enabled = config.get("external_message_consumer", {}).get("enabled", False)
    if enabled is False:
        r.ok("external_message_consumer.enabled === false")
    else:
        r.fail("external_message_consumer.enabled === false", f"实际值是 {enabled!r}")


def check_no_external_distribution_fields(r: CheckResult, config: dict[str, Any]) -> None:
    """扫描禁止的外部分发字段（webhook / discord / slack / binance_square / x_distribution）。
    这些字段在 v1 不应该出现，即使存在也必须 enabled=false 且无凭证。"""
    # 这些 top-level 字段如果出现非空启用配置，直接拒绝
    forbidden_top_level = ["webhook", "discord", "slack", "binance_square", "x_distribution"]
    found_active = []
    for field in forbidden_top_level:
        block = config.get(field)
        if block is None:
            continue
        # 块存在了——至少要 enabled=false
        if isinstance(block, dict):
            if block.get("enabled", False) is True:
                found_active.append(f"{field}.enabled=true")
            # 即使 disabled，块里如果有 url/token 等关键字段也提示
            for sus_key in ("url", "token", "webhook_url", "channel_id"):
                if block.get(sus_key):
                    found_active.append(f"{field}.{sus_key} 非空")
        elif block:
            # 不是 dict 但是 truthy → 可疑
            found_active.append(f"{field} = {type(block).__name__}")

    if not found_active:
        r.ok("无外部分发字段（webhook/discord/slack/binance_square/x_distribution）")
    else:
        r.fail(
            "无外部分发字段",
            "; ".join(found_active),
        )


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


def check_risk_module_loadable(r: CheckResult) -> None:
    """风控模块（Step 2）必须可 import、关键函数齐、能从 config 加载、能拒绝坏订单。

    fail closed：任何一步出错都视为风控失效，拒绝启动 freqtrade。
    """
    # 把 wanglin OS 根加进 sys.path，让 risk 包可被 import
    sys.path.insert(0, str(WANGLIN_OS_ROOT))
    try:
        try:
            from risk import (
                AccountState,
                ProposedOrder,
                RiskConfigError,
                load_risk_limits,
                validate_order,
            )
        except ImportError as e:
            r.fail("risk 模块可 import", f"{e}")
            return

        r.ok("risk 模块可 import + 接口齐", "AccountState/ProposedOrder/load_risk_limits/validate_order")

        # 用真实 config 加载风控上限
        try:
            limits = load_risk_limits(CONFIG_PATH)
        except RiskConfigError as e:
            r.fail("load_risk_limits 能从 config 读出风控上限", f"{e}")
            return
        r.ok(
            "load_risk_limits 从 config 读出风控上限",
            f"杠杆≤{limits.max_leverage_cap} / 单笔≤{limits.risk_per_trade_pct} / 日熔断≤{limits.daily_loss_halt_pct}",
        )

        # Smoke check：构造一个明显违规的订单，确认 validate_order fail closed
        from decimal import Decimal as _D
        bad_order = ProposedOrder(
            symbol="DOGE/USDT:USDT",         # 非白名单
            side="long",
            entry_price=_D("0.1"),
            stop_loss_price=None,             # 无止损
            quantity=_D("100000"),            # 超大数量（保证单笔风险违规）
            leverage=_D("100"),               # 远超 5x
        )
        bad_account = AccountState(
            total_equity=_D("100000"),
            available_balance=_D("100000"),
            daily_realized_pnl=_D("0"),
        )
        decision = validate_order(bad_order, bad_account, limits)
        if decision.approved:
            r.fail(
                "validate_order 对明显违规订单 fail closed",
                "明显违规订单竟然被批准了",
            )
            return
        if len(decision.reasons) < 2:
            r.fail(
                "validate_order 一次性返回多重违规",
                f"只返回 {len(decision.reasons)} 条原因，应至少 2 条",
            )
            return
        r.ok(
            "validate_order 对违规订单 fail closed",
            f"返回 {len(decision.reasons)} 条拒绝原因",
        )
    finally:
        # 清理 sys.path 修改，避免污染外部环境
        try:
            sys.path.remove(str(WANGLIN_OS_ROOT))
        except ValueError:
            pass


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
    check_no_external_distribution_fields(r, config)
    check_no_hardcoded_credentials(r, config)
    check_leverage_cap(r, config)
    check_risk_per_trade(r, config)
    check_daily_loss_halt(r, config)
    check_trading_mode(r, config)
    check_strategy_name(r, config)
    check_no_mainnet_credential_leak(r, config)

    # 凭证文件层面
    check_testnet_credentials_exist(r)

    # 风控模块层面（Step 2 起加入）
    check_risk_module_loadable(r)

    r.render()
    return r.exit_code


if __name__ == "__main__":
    sys.exit(main())
