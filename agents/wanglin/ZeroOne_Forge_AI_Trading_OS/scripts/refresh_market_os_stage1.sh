#!/usr/bin/env bash
set -euo pipefail
BASE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS"
STAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[market-os] refresh start: $STAMP"
python3 - <<'PY2'
import json, time
from pathlib import Path
root=Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS')
base=root/'data/market_os_stage1'
raw=base/'raw'
processed=base/'processed'
pools=base/'pools'
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
latest=[]
# 路径1：短周期/资金行为扫描做宽
for name in ['binance_futures_snapshots_v1.json','binance_board_flow_v1.json','short_cycle_pre_signal_candidates_v1.json']:
    p=raw/name
    if not p.exists():
        continue
    arr=json.loads(p.read_text())
    for x in arr:
        sym=x.get('symbol')
        if not sym:
            continue
        if name=='binance_futures_snapshots_v1.json':
            latest.append({'source':'open_interest_snapshot','source_type':'latest_scan','symbol':sym,'narrative':'latest_oi_scan','oi_change_pct':x.get('open_interest'),'funding_rate':x.get('funding_rate'),'volume_score':x.get('quote_volume'),'timestamp':now})
            latest.append({'source':'funding_snapshot','source_type':'latest_scan','symbol':sym,'narrative':'latest_funding_scan','oi_change_pct':x.get('open_interest'),'funding_rate':x.get('funding_rate'),'volume_score':x.get('quote_volume'),'timestamp':now})
        elif name=='binance_board_flow_v1.json':
            latest.append({'source':'binance_board','source_type':'latest_scan','symbol':sym,'narrative':x.get('narrative','latest_board_scan'),'price_change_pct':x.get('price_change_pct'),'volume_score':x.get('quote_volume'),'timestamp':now})
        elif name=='short_cycle_pre_signal_candidates_v1.json':
            latest.append({'source':'short_cycle_scan','source_type':'latest_scan','symbol':sym,'narrative':x.get('narrative','latest_short_cycle_scan'),'price_change_pct':x.get('price_change_pct'),'volume_score':x.get('quote_volume'),'oi_change_pct':x.get('oi_change_pct'),'funding_rate':x.get('funding_rate'),'timestamp':now})
# 路径2：热度扫描做宽
for name, source in [('binance_square_real_fetch_depth_v1.json','binance_square'),('x_real_fetch_depth_v1.json','x'),('cross_verification_depth_v1.json',None)]:
    p=raw/name
    if not p.exists():
        continue
    arr=json.loads(p.read_text())
    for x in arr:
        sym=x.get('symbol')
        if not sym:
            continue
        latest.append({'source':source or x.get('source','cross_verification'),'source_type':'latest_scan','symbol':sym,'narrative':x.get('narrative','latest_attention_scan'),'sentiment':x.get('sentiment'),'engagement_score':x.get('engagement'),'volume_score':x.get('volume_score'),'timestamp':now})
# 去重：同 source+symbol 只保留一条，避免噪音重复灌水
seen=set(); dedup=[]
for s in latest:
    k=(s.get('source'), s.get('symbol'))
    if k in seen:
        continue
    seen.add(k)
    dedup.append(s)
latest=dedup
(processed/'latest_market_signals_v1.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2))
agg={}
for s in latest:
    sym=s.get('symbol')
    if not sym:
        continue
    a=agg.setdefault(sym,{'symbol':sym,'capital_sources':set(),'attention_sources':set(),'notes':[]})
    src=s.get('source')
    st=f"{src}:{s.get('source_type')}"
    if src in ('short_cycle_scan','open_interest_snapshot','funding_snapshot','binance_board'):
        a['capital_sources'].add(st)
    if src in ('binance_square','x','cross_verification'):
        a['attention_sources'].add(st)
    if s.get('narrative'):
        a['notes'].append(s['narrative'])
A=[]; B=[]; C=[]
for sym,a in agg.items():
    cap=len(a['capital_sources']); att=len(a['attention_sources'])
    item={'symbol':sym,'capital_count':cap,'attention_count':att,'capital_sources':sorted(a['capital_sources'])[:8],'attention_sources':sorted(a['attention_sources'])[:8],'summary':' | '.join(list(dict.fromkeys(a['notes']))[:2]),'updated_at':now}
    if cap>0 and att>0:
        item['path_class']='A_resonance'; A.append(item)
    elif cap>0:
        item['path_class']='B_capital_only'; B.append(item)
    elif att>0:
        item['path_class']='C_attention_only'; C.append(item)
A=sorted(A,key=lambda x:(x['capital_count']+x['attention_count'],x['capital_count'],x['attention_count']), reverse=True)
B=sorted(B,key=lambda x:(x['capital_count'],x['attention_count']), reverse=True)
C=sorted(C,key=lambda x:(x['attention_count'],x['capital_count']), reverse=True)
(processed/'layer1_dual_path_A_resonance.json').write_text(json.dumps(A,ensure_ascii=False,indent=2))
(processed/'layer1_dual_path_B_capital_only.json').write_text(json.dumps(B,ensure_ascii=False,indent=2))
(processed/'layer1_dual_path_C_attention_only.json').write_text(json.dumps(C,ensure_ascii=False,indent=2))
cand=[]
for i,x in enumerate(A, start=1):
    x['layer2_bucket']='A1_priority' if i<=5 else 'A2_watch' if i<=10 else 'A3_observe'
    if i<=5:
        cand.append({'symbol':x['symbol'],'candidate_level':'priority_candidate','why_selected':x['summary'] or '资金与热度共振最强','trigger_source':x['capital_sources'][:4]+x['attention_sources'][:4],'verification_notes':x['summary'],'priority_rank':i,'updated_at':now})
(processed/'layer1_dual_path_A_resonance.json').write_text(json.dumps(A,ensure_ascii=False,indent=2))
(pools/'candidate_pool_v2_from_signal_cards.json').write_text(json.dumps(cand,ensure_ascii=False,indent=2))
print(json.dumps({'latest_signal_count':len(latest),'A_count':len(A),'B_count':len(B),'C_count':len(C),'A_symbols':[x['symbol'] for x in A],'B_symbols':[x['symbol'] for x in B],'C_symbols':[x['symbol'] for x in C],'candidate_count':len(cand),'candidate_symbols':[x['symbol'] for x in cand]}, ensure_ascii=False))
PY2
echo "[market-os] refresh done"
