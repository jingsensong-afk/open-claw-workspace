import json, time
from pathlib import Path
root=Path('/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS')
rawdir=root/'data/market_os_stage1/raw'
proc_path=root/'data/market_os_stage1/processed/market_signals_v1.json'
processed=root/'data/market_os_stage1/processed'
pooldir=root/'data/market_os_stage1/pools'
calib=root/'data/market_os_stage1/calibration_layer'
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
signals=json.loads(proc_path.read_text())
seen={(s.get('source'),s.get('source_type'),s.get('symbol'),s.get('narrative'),s.get('raw_ref')) for s in signals}
def add(sig):
    k=(sig.get('source'),sig.get('source_type'),sig.get('symbol'),sig.get('narrative'),sig.get('raw_ref'))
    if k not in seen:
        signals.append(sig); seen.add(k)
for x in json.loads((rawdir/'binance_square_real_fetch_depth_v1.json').read_text()):
    add({'source':'binance_square','source_type':'real_fetch','symbol':x['symbol'],'quote':'USDT','narrative':x['narrative'],'sentiment':x['sentiment'],'engagement_score':x['engagement'],'velocity_score':None,'price_change_pct':None,'volume_score':None,'oi_change_pct':None,'funding_rate':None,'timestamp':now,'raw_ref':'raw/binance_square_real_fetch_depth_v1.json','source_confidence':0.84,'signal_quality':0.82,'last_verified_at':now})
for x in json.loads((rawdir/'x_real_fetch_depth_v1.json').read_text()):
    add({'source':'x','source_type':'real_fetch','symbol':x['symbol'],'quote':'USDT','narrative':x['narrative'],'sentiment':x['sentiment'],'engagement_score':x['engagement'],'velocity_score':None,'price_change_pct':None,'volume_score':None,'oi_change_pct':None,'funding_rate':None,'timestamp':now,'raw_ref':'raw/x_real_fetch_depth_v1.json','source_confidence':0.82,'signal_quality':0.80,'last_verified_at':now})
for x in json.loads((rawdir/'cross_verification_depth_v1.json').read_text()):
    add({'source':x['source'],'source_type':'real_fetch','symbol':x['symbol'],'quote':'USDT','narrative':x['narrative'],'sentiment':x['sentiment'],'engagement_score':16000,'velocity_score':1.5,'price_change_pct':None,'volume_score':x['volume_score'],'oi_change_pct':None,'funding_rate':None,'timestamp':now,'raw_ref':'raw/cross_verification_depth_v1.json','source_confidence':0.86,'signal_quality':0.82,'last_verified_at':now})
proc_path.write_text(json.dumps(signals,ensure_ascii=False,indent=2))
bad_symbols={'币安人生','EUR'}
agg={}
for s in signals:
    sym=s.get('symbol')
    if not sym or sym in bad_symbols:
        continue
    a=agg.setdefault(sym,{'symbol':sym,'capital_sources':set(),'attention_sources':set(),'notes':[]})
    src=s.get('source')
    st=f"{src}:{s.get('source_type')}"
    if src in ('short_cycle_scan','top_volume_24h','open_interest_snapshot','funding_snapshot','binance_board'):
        a['capital_sources'].add(st)
    if src in ('binance_square','x','binance_announcement','binance_new_contract'):
        a['attention_sources'].add(st)
    if s.get('narrative'):
        a['notes'].append(s['narrative'])
A=[]; B=[]; C=[]
for sym,a in agg.items():
    cap=len(a['capital_sources']); att=len(a['attention_sources'])
    item={'symbol':sym,'capital_count':cap,'attention_count':att,'capital_sources':sorted(a['capital_sources'])[:6],'attention_sources':sorted(a['attention_sources'])[:6],'summary':' | '.join(list(dict.fromkeys(a['notes']))[:2]),'updated_at':now}
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
    x['layer2_bucket']='A1_priority' if i<=3 else 'A2_watch' if i<=5 else 'A3_observe'
    if i<=3:
        cand.append({'symbol':x['symbol'],'candidate_level':'priority_candidate','why_selected':x['summary'] or '资金与热度共振最强','trigger_source':x['capital_sources'][:3]+x['attention_sources'][:3],'verification_notes':x['summary'],'priority_rank':i,'updated_at':now})
(processed/'layer1_dual_path_A_resonance.json').write_text(json.dumps(A,ensure_ascii=False,indent=2))
(pooldir/'candidate_pool_v2_from_signal_cards.json').write_text(json.dumps(cand,ensure_ascii=False,indent=2))
report={'updated_at':now,'real_fetch_count':sum(1 for s in signals if s.get('source_type')=='real_fetch'),'A_count':len(A),'B_count':len(B),'C_count':len(C),'candidate_count':len(cand),'candidate_symbols':[x['symbol'] for x in cand],'summary':'已将 real fetch depth upgrade 切到新主链输出，不再生成 v1 candidate/execution 并行池'}
(calib/'real_fetch_depth_upgrade_2026-04-26.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
