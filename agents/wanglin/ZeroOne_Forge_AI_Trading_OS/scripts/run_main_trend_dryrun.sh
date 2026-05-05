#!/usr/bin/env bash
#
# ZeroOne Forge · MainTrendStrategy · Dry-Run 启动包装器
#
# 【职责】
# 1. 调用 preflight_freqtrade_main_dryrun.py 做硬安全检查
# 2. 通过后从 .binance_futures_api.testnet.json 读凭证，注入环境变量
# 3. 用 venv 里的 freqtrade 执行后续命令
#
# 【设计原则（来自 Codex review）】
# - 默认运行方式不暴露裸 freqtrade 命令
# - preflight 失败 → 整个脚本退出，不调 freqtrade
# - 凭证只在子进程 env 中存在，不写日志、不写文件
# - 使用 set -euo pipefail，任何错误立即终止
#
# 【用法】
#   bash agents/wanglin/ZeroOne_Forge_AI_Trading_OS/scripts/run_main_trend_dryrun.sh trade
#   bash ...run_main_trend_dryrun.sh backtesting --timerange 20220601-20260501
#   bash ...run_main_trend_dryrun.sh download-data --timerange 20220601-20260501
#
# 【硬约束】
# 不能 cron 自动调用，必须人工触发（Codex 边界要求）

set -euo pipefail

# 解析路径（脚本所在目录开始往上走）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WANGLIN_OS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WANGLIN_PARTITION_ROOT="$(cd "$WANGLIN_OS_ROOT/.." && pwd)"
REPO_ROOT="$(cd "$WANGLIN_PARTITION_ROOT/../.." && pwd)"

VENV_PYTHON="$WANGLIN_OS_ROOT/.venv/bin/python"
VENV_FREQTRADE="$WANGLIN_OS_ROOT/.venv/bin/freqtrade"
PREFLIGHT="$WANGLIN_OS_ROOT/scripts/preflight_freqtrade_main_dryrun.py"
CONFIG="$WANGLIN_OS_ROOT/config/freqtrade_main_dryrun.json"
TESTNET_KEYFILE="$WANGLIN_PARTITION_ROOT/.binance_futures_api.testnet.json"

# 基本环境检查
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "❌ 找不到 venv Python：$VENV_PYTHON" >&2
    echo "   先按 README 流程建立虚拟环境并装依赖。" >&2
    exit 2
fi
if [[ ! -x "$VENV_FREQTRADE" ]]; then
    echo "❌ 找不到 venv 里的 freqtrade：$VENV_FREQTRADE" >&2
    exit 2
fi

# 0a. 子命令白名单（Codex 要求：Step 1 阶段不允许 trade / hyperopt）
# 进入 Step 8（实盘 dry-run 评估）前，trade 都不在白名单
if [[ $# -lt 1 ]]; then
    echo "❌ 缺少 freqtrade 子命令" >&2
    echo "   用法：$0 <show-config|download-data|backtesting|list-strategies|list-data> ..." >&2
    exit 2
fi

ALLOWED_SUBCOMMANDS=(show-config download-data backtesting list-strategies list-data list-pairs list-markets list-timeframes test-pairlist)
SUBCMD="$1"
ALLOWED=0
for cmd in "${ALLOWED_SUBCOMMANDS[@]}"; do
    if [[ "$SUBCMD" == "$cmd" ]]; then
        ALLOWED=1
        break
    fi
done
if [[ "$ALLOWED" -eq 0 ]]; then
    echo "❌ 拒绝启动：Step 1 阶段不允许 freqtrade 子命令 '$SUBCMD'" >&2
    echo "   当前白名单：${ALLOWED_SUBCOMMANDS[*]}" >&2
    echo "   trade / hyperopt 等需等到后续步骤补齐 risk gate + strategy 后人工放行。" >&2
    exit 2
fi
echo "[0/3] 子命令白名单 ✅  '$SUBCMD'"

# 0b. 拒绝任何外部预置的 FREQTRADE__* 环境变量
# 否则外部 shell 可以用 FREQTRADE__DRY_RUN=false 等绕过 config 安全设置
PRESET_VARS="$(env | grep -E '^FREQTRADE__' | cut -d= -f1 || true)"
if [[ -n "$PRESET_VARS" ]]; then
    echo "❌ 拒绝启动：检测到外部预置的 FREQTRADE__* 环境变量" >&2
    echo "$PRESET_VARS" | sed 's/^/   /' >&2
    echo "   这些可能覆盖 config 的 dry_run/sandbox/strategy 等关键安全设置。" >&2
    echo "   请先 'unset' 它们再重跑。" >&2
    exit 2
fi
echo "[0/3] 无外部预置 FREQTRADE__* 环境变量 ✅"

# 1. Preflight 硬安全检查
echo "[1/3] Preflight 启动安全门 ..."
"$VENV_PYTHON" "$PREFLIGHT"
# preflight 内部会 sys.exit(2)；set -e 会让本脚本同样退出

# 2. 从凭证文件读 key 并注入 env（凭证内容不打印到屏幕）
echo ""
echo "[2/3] 注入测试网凭证到环境变量 ..."
if [[ ! -f "$TESTNET_KEYFILE" ]]; then
    echo "❌ 找不到测试网凭证文件：$TESTNET_KEYFILE" >&2
    exit 2
fi

# 用 Python 解析 JSON 比 jq 更可移植（jq 不一定装）
FREQTRADE__EXCHANGE__KEY="$("$VENV_PYTHON" -c "
import json, sys
cred = json.load(open('$TESTNET_KEYFILE'))
print(cred.get('apiKey', ''), end='')
")"
FREQTRADE__EXCHANGE__SECRET="$("$VENV_PYTHON" -c "
import json, sys
cred = json.load(open('$TESTNET_KEYFILE'))
print(cred.get('apiSecret', ''), end='')
")"

if [[ -z "$FREQTRADE__EXCHANGE__KEY" || -z "$FREQTRADE__EXCHANGE__SECRET" ]]; then
    echo "❌ 凭证文件中 apiKey 或 apiSecret 为空" >&2
    exit 2
fi

export FREQTRADE__EXCHANGE__KEY
export FREQTRADE__EXCHANGE__SECRET

# 显示长度和头尾 4 字符以便人眼核对（但不打印完整 key）
KEY_LEN="${#FREQTRADE__EXCHANGE__KEY}"
KEY_HEAD="${FREQTRADE__EXCHANGE__KEY:0:4}"
KEY_TAIL="${FREQTRADE__EXCHANGE__KEY: -4}"
echo "    凭证已注入 env：长度 ${KEY_LEN}, 头尾 ${KEY_HEAD}...${KEY_TAIL}"

# 3. 调用 freqtrade，把外部参数透传过去
# 显式 cd 到仓库根，确保 config 里的相对路径（user_data_dir / strategy_path）能正确解析
cd "$REPO_ROOT"

USER_DATA_DIR="$WANGLIN_OS_ROOT/user_data"

echo ""
echo "[3/3] 启动 freqtrade ..."
echo "    cwd:           $REPO_ROOT"
echo "    config:        $CONFIG"
echo "    user_data_dir: $USER_DATA_DIR"
echo "    args:          $*"
echo "----"

# exec 让 freqtrade 直接接管当前进程，凭证 env 自动随子进程传过去
# --userdir 用绝对路径，避免 freqtrade 路径解析的相对路径歧义
exec "$VENV_FREQTRADE" "$@" --config "$CONFIG" --userdir "$USER_DATA_DIR"
