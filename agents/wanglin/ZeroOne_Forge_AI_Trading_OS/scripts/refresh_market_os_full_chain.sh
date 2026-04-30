#!/usr/bin/env bash
set -euo pipefail
BASE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS"
echo "[market-os] full-chain refresh start"
bash "$BASE/scripts/refresh_market_os_stage1.sh"
python3 - <<'PY'
import json, time
from pathlib import Path
root=Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS')
base=root/'data/market_os_stage1'
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
A=json.loads((base/'processed'/'layer1_dual_path_A_resonance.json').read_text())
cand=json.loads((base/'pools'/'candidate_pool_v2_from_signal_cards.json').read_text())
thought=[]
for i,x in enumerate(cand, start=1):
    verdict='do' if i<=2 else 'observe'
    thought.append({'symbol':x['symbol'],'one_line':f"{x['symbol']} 属于资金与热度共振标的，{'进入第四层执行判断' if verdict=='do' else '继续观察，不进入第四层'}。",'judgment':verdict,'execution_view':'可做' if verdict=='do' else '观察','updated_at':now})
(base/'thought_layer'/'thought_candidates_v2.json').write_text(json.dumps(thought,ensure_ascii=False,indent=2))
strategy=[]
for t in thought:
    if t['judgment']!='do':
        continue
    strategy.append({'symbol':t['symbol'],'side':'long','execution_qualified':True,'trigger_conditions':['回踩不破关键结构位','量能/热度未明显衰退','盘口未出现反向失衡'],'execution_actions':{'trial_position_pct':30,'confirm_position_pct':40,'add_position_pct':30,'target_notional':'100U initial test'},'invalid_conditions':['结构位失守','放量反向跌破','热度/资金明显断裂'],'time_stop':{'soft_check':'2h','hard_exit':'4h'},'updated_at':now})
(base/'execution_layer'/'strategy_execution_orders_v2.json').write_text(json.dumps(strategy,ensure_ascii=False,indent=2))
cards=[{'symbol':s['symbol'],'side':s['side'],'execution_qualified':s['execution_qualified'],'trigger_conditions':s['trigger_conditions'],'execution_actions':s['execution_actions'],'invalid_conditions':s['invalid_conditions'],'time_stop':s['time_stop'],'updated_at':now} for s in strategy]
(base/'execution_layer'/'execution_v1_trade_cards_v2.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2))
summary={'channel':'telegram/binance_square','message_type':'strategy_summary','summary':f"A类共振 {len(A)} / 第二层正式候选 {len(cand)} / 第三层最终判断 {sum(1 for x in thought if x['judgment']=='do')} / 第四层策略单 {len(strategy)}",'symbols':[x['symbol'] for x in strategy],'updated_at':now}
(base/'distribution_layer'/'distribution_summary_v2.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
cal={'updated_at':now,'A_count':len(A),'candidate_count':len(cand),'thought_count':len(thought),'thought_do_count':sum(1 for x in thought if x['judgment']=='do'),'strategy_count':len(strategy),'strategy_symbols':[x['symbol'] for x in strategy],'summary':'已按新主链统一刷新：A类共振 -> 第二层正式候选 -> 第三层判断 -> 第四层策略单 -> 第五层分发'}
(base/'calibration_layer'/'calibration_v2_unified_main_chain.json').write_text(json.dumps(cal,ensure_ascii=False,indent=2))
print('thought', len(thought))
print('strategy', len(strategy))
print('distribution', len(summary['symbols']))
print('calibration', len(strategy))
print(json.dumps({'A_symbols':[x['symbol'] for x in A],'candidate_symbols':[x['symbol'] for x in cand],'thought_do_symbols':[x['symbol'] for x in thought if x['judgment']=='do'],'strategy_symbols':[x['symbol'] for x in strategy]}, ensure_ascii=False))
PY
echo "[market-os] full-chain refresh done"
