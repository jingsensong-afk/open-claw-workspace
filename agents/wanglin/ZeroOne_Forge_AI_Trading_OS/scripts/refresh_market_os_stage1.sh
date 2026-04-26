#!/usr/bin/env bash
set -euo pipefail
BASE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS"
STAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[market-os] refresh start: $STAMP"
python3 - <<'PY2'
import json, time
base='/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS/data/market_os_stage1'
proc=base+'/processed/market_signals_v1.json'
pools=base+'/pools'
with open(proc) as f:
    signals=json.load(f)
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
for s in signals:
    if 'last_verified_at' in s:
        s['last_verified_at']=now
with open(proc,'w') as f:
    json.dump(signals,f,ensure_ascii=False,indent=2)
# lightweight rebuild using existing validated signals
agg={}
for s in signals:
    sym=s['symbol']
    a=agg.setdefault(sym,{'symbol':sym,'mentions':0,'source_types':set(),'bull':0,'bear':0,'neutral':0,'narratives':[],'max_price':None,'max_volume':None,'funding':[],'engagement':0,'catalyst':0,'velocity':0,'conf':[],'qual':[],'last_verified_at':now})
    a['mentions'] += 1
    a['source_types'].add(f"{s.get('source')}:{s.get('source_type')}")
    if s.get('sentiment')=='bullish': a['bull'] += 1
    elif s.get('sentiment')=='bearish': a['bear'] += 1
    else: a['neutral'] += 1
    if s.get('narrative'): a['narratives'].append(s['narrative'])
    if s.get('source') == 'binance_announcement': a['catalyst'] += 1
    if s.get('velocity_score') is not None: a['velocity'] += float(s.get('velocity_score') or 0)
    if s.get('price_change_pct') is not None:
        p=abs(float(s['price_change_pct']))
        a['max_price']=p if a['max_price'] is None else max(a['max_price'],p)
    if s.get('volume_score') is not None:
        v=float(s['volume_score'])
        a['max_volume']=v if a['max_volume'] is None else max(a['max_volume'],v)
    if s.get('funding_rate') is not None: a['funding'].append(float(s['funding_rate']))
    if s.get('engagement_score') is not None: a['engagement'] += float(s['engagement_score'])
    if s.get('source_confidence') is not None: a['conf'].append(float(s['source_confidence']))
    if s.get('signal_quality') is not None: a['qual'].append(float(s['signal_quality']))
watch=[]
for sym,a in agg.items():
    narrative_score=min(10,2+len(a['source_types'])+min(a['mentions'],5)+min(a['catalyst'],2))
    sentiment_score=max(-5,min(8,a['bull']-a['bear']))
    attention_score=min(10,a['mentions']+(2 if a['engagement']>50000 else 1 if a['engagement']>15000 else 0)+(1 if a['velocity']>0 else 0))
    liquidity_score=4
    if a['max_volume'] is not None:
        mv=a['max_volume']
        liquidity_score=9 if mv>1e9 else 8 if mv>5e8 else 7 if mv>1e8 else 6 if mv>5e7 else 5
    volatility_score=4 if a['max_price'] is None else (9 if a['max_price']>30 else 8 if a['max_price']>20 else 7 if a['max_price']>12 else 6 if a['max_price']>8 else 5)
    funding_bias=0
    if a['funding']:
        avgf=sum(a['funding'])/len(a['funding'])
        funding_bias=1 if avgf>0 else -1 if avgf<0 else 0
    avg_conf=round(sum(a['conf'])/len(a['conf']),2) if a['conf'] else None
    avg_qual=round(sum(a['qual'])/len(a['qual']),2) if a['qual'] else None
    execution_score=round(0.2*narrative_score+0.16*max(sentiment_score,0)+0.18*attention_score+0.16*liquidity_score+0.1*volatility_score+0.07*max(funding_bias,0)+0.05*min(a['catalyst'],2)+0.04*(avg_conf or 0)*10+0.04*(avg_qual or 0)*10,2)
    status='watch'
    if execution_score>=7.2:
        status='executable'
    elif execution_score>=5.8:
        status='candidate'
    watch.append({'symbol':sym,'narrative_score':narrative_score,'sentiment_score':sentiment_score,'attention_score':attention_score,'liquidity_score':liquidity_score,'volatility_score':volatility_score,'execution_score':execution_score,'risk_level':'high' if volatility_score>=7 else 'medium','status':status,'reason':' | '.join(list(dict.fromkeys(a['narratives']))[:3]),'invalid_condition':None,'updated_at':now,'source_confidence':avg_conf,'signal_quality':avg_qual,'last_verified_at':now})
watch=sorted(watch,key=lambda x:(x['execution_score'],x['attention_score'],x['narrative_score']),reverse=True)
candidate=[x for x in watch if x['status'] in ('candidate','executable')]
execution=[x for x in watch if x['status']=='executable']
for name,data in [('watch_pool.json',watch),('candidate_pool.json',candidate),('execution_pool.json',execution)]:
    with open(pools+'/'+name,'w') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps({'watch':len(watch),'candidate':len(candidate),'execution':len(execution),'top_execution':[x['symbol'] for x in execution[:10]]}, ensure_ascii=False))
PY2
echo "[market-os] refresh done"
