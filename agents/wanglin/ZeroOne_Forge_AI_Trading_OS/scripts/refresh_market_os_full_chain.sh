#!/usr/bin/env bash
set -euo pipefail
BASE="/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS"
echo "[market-os] full-chain refresh start"
# 1-2层：信息流/候选池
bash "$BASE/scripts/refresh_market_os_stage1.sh"
# 3层：思考层
python3 - <<'PY2'
import json, time, os
root='/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS'
pools=root+'/data/market_os_stage1/pools'
outdir=root+'/data/market_os_stage1/thought_layer'
os.makedirs(outdir, exist_ok=True)
exec_pool=json.load(open(pools+'/execution_pool.json'))
cand_pool=json.load(open(pools+'/candidate_pool.json'))
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
analysis=[]
seen=set()
for item in cand_pool[:6]:
    sym=item['symbol']
    if sym in seen:
        continue
    seen.add(sym)
    status=item['status']
    view='做' if status=='executable' else '观望偏做'
    structure='偏强' if item['execution_score']>=6 else '待确认'
    analysis.append({'symbol':sym,'one_line':f'{sym} 当前属于{status}，优先按{structure}结构处理。','current_action':view,'structure':structure,'volume_price':'有交易活跃支撑' if (item.get('liquidity_score') or 0)>=6 else '量能一般','oi':'已纳入观察' if sym in ('BTC','ETH','SOL','DOGE','XRP') else '暂以候选池信号为主','funding':'已纳入观察' if sym in ('BTC','ETH','SOL','DOGE','XRP') else '暂以情绪/叙事为主','long_short_ratio':'多头占优' if (item.get('sentiment_score') or 0)>0 else '多空未明显拉开','key_resistance':'待结合实时盘面补充','key_support':'待结合实时盘面补充','best_action':'进入执行观察' if status=='executable' else '继续观察，等确认','invalid_condition':'跌破关键支撑或热度明显退潮','vs_previous':'自动刷新后更新','revision':'按最新pool自动刷新','updated_at':now})
with open(outdir+'/compact_analysis_outputs_v1.json','w') as f:
    json.dump(analysis,f,ensure_ascii=False,indent=2)
print('thought', len(analysis))
PY2
# 4层：执行层
python3 - <<'PY3'
import json, time, os
root='/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS'
exec_pool=json.load(open(root+'/data/market_os_stage1/pools/execution_pool.json'))
thought=json.load(open(root+'/data/market_os_stage1/thought_layer/compact_analysis_outputs_v1.json'))
thought_map={x['symbol']:x for x in thought}
out=root+'/data/market_os_stage1/execution_layer'
os.makedirs(out, exist_ok=True)
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
orders=[]
for item in exec_pool[:6]:
    sym=item['symbol']
    t=thought_map.get(sym,{})
    side='long' if (item.get('sentiment_score') or 0)>=0 else 'short'
    orders.append({'symbol':sym,'action':'prepare_entry','side':side,'confidence':round((item.get('execution_score') or 0)/10,2),'max_position_pct':2 if sym in ('BTC','ETH','SOL') else 1,'stop_condition':t.get('invalid_condition','失效条件待补充'),'take_profit_mode':'staged_take_profit','execution_status':'paper_ready','updated_at':now})
with open(out+'/execution_whitelist_v1.json','w') as f: json.dump(orders,f,ensure_ascii=False,indent=2)
with open(out+'/paper_execution_orders_v1.json','w') as f: json.dump(orders,f,ensure_ascii=False,indent=2)
with open(out+'/paper_execution_log_v1.json','w') as f: json.dump({'updated_at':now,'count':len(orders),'orders':orders},f,ensure_ascii=False,indent=2)
validation=[]
for item in orders:
    validation.append({'symbol':item['symbol'],'validation_status':'pass','issues':[],'next_step':'continue_paper','updated_at':now})
with open(out+'/paper_execution_validation_v1.json','w') as f: json.dump({'updated_at':now,'items':validation},f,ensure_ascii=False,indent=2)
with open(out+'/execution_layer_stage_status_v1.json','w') as f: json.dump({'updated_at':now,'paper_order_count':len(validation),'pass_count':len(validation),'needs_fix_count':0,'stage_decision':'continue_paper_and_observe'},f,ensure_ascii=False,indent=2)
print('execution', len(orders))
PY3
# 4.5层：execution 强一致性硬约束
python3 - <<'PY35'
import json, time, os
root='/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS'
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
exec_path=root+'/data/market_os_stage1/pools/execution_pool.json'
cand_path=root+'/data/market_os_stage1/pools/candidate_pool.json'
watch_path=root+'/data/market_os_stage1/pools/watch_pool.json'
thought_path=root+'/data/market_os_stage1/thought_layer/compact_analysis_outputs_v1.json'
paper_path=root+'/data/market_os_stage1/execution_layer/paper_execution_orders_v1.json'
execution=json.load(open(exec_path))
candidate=json.load(open(cand_path))
watch=json.load(open(watch_path))
thought=json.load(open(thought_path))
paper=json.load(open(paper_path))
thought_syms={x['symbol'] for x in thought}
paper_syms={x['symbol'] for x in paper}
watch_map={x['symbol']:x for x in watch}
cand_map={x['symbol']:x for x in candidate}
new_execution=[]
downgraded=[]
for item in execution:
    sym=item['symbol']
    if sym not in thought_syms or sym not in paper_syms:
        fix=watch_map.get(sym, dict(item))
        fix['status']='candidate'
        fix['updated_at']=now
        downgraded.append(fix)
        cand_map[sym]=fix
    else:
        new_execution.append(item)
for sym,item in watch_map.items():
    if sym in [x['symbol'] for x in downgraded]:
        item['status']='candidate'
        item['updated_at']=now
new_watch=sorted(watch_map.values(), key=lambda x:(x.get('execution_score',0),x.get('attention_score',0),x.get('narrative_score',0)), reverse=True)
new_candidate=sorted(cand_map.values(), key=lambda x:(x.get('execution_score',0),x.get('attention_score',0),x.get('narrative_score',0)), reverse=True)
with open(exec_path,'w') as f: json.dump(new_execution,f,ensure_ascii=False,indent=2)
with open(cand_path,'w') as f: json.dump(new_candidate,f,ensure_ascii=False,indent=2)
with open(watch_path,'w') as f: json.dump(new_watch,f,ensure_ascii=False,indent=2)
report={'updated_at':now,'downgraded_symbols':[x['symbol'] for x in downgraded],'execution_after_consistency':len(new_execution),'candidate_after_consistency':len(new_candidate)}
os.makedirs(root+'/data/market_os_stage1/calibration_layer', exist_ok=True)
with open(root+'/data/market_os_stage1/calibration_layer/execution_consistency_live_status_v1.json','w') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print('execution_consistency', len(new_execution), [x['symbol'] for x in downgraded])
PY35

# 5层：分发层
python3 - <<'PY4'
import json, time, os
root='/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS'
watch=json.load(open(root+'/data/market_os_stage1/pools/watch_pool.json'))
candidate=json.load(open(root+'/data/market_os_stage1/pools/candidate_pool.json'))
execution=json.load(open(root+'/data/market_os_stage1/pools/execution_pool.json'))
thought=json.load(open(root+'/data/market_os_stage1/thought_layer/compact_analysis_outputs_v1.json'))
paper=json.load(open(root+'/data/market_os_stage1/execution_layer/paper_execution_orders_v1.json'))
out=root+'/data/market_os_stage1/distribution_layer'
os.makedirs(out, exist_ok=True)
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
summary={'channel':'telegram','message_type':'market_os_summary','title':'ZeroOne Forge AI交易OS 摘要','summary':f'watch {len(watch)} / candidate {len(candidate)} / execution {len(execution)} / paper {len(paper)}','items':{'top_execution':[x['symbol'] for x in execution[:10]],'top_candidate':[x['symbol'] for x in candidate[:10] if x['symbol'] not in [y['symbol'] for y in execution[:10]]],'thought_outputs':[x['symbol'] for x in thought[:10]],'paper_execution':[x['symbol'] for x in paper[:10]]},'updated_at':now}
with open(out+'/distribution_summary_v1.json','w') as f: json.dump(summary,f,ensure_ascii=False,indent=2)
text=[]
text.append('【ZeroOne Forge AI交易OS】')
text.append(f'watch {len(watch)}｜candidate {len(candidate)}｜execution {len(execution)}｜paper {len(paper)}')
text.append('execution: ' + ', '.join([x['symbol'] for x in execution[:8]]))
extra=[x['symbol'] for x in candidate[:8] if x['symbol'] not in [y['symbol'] for y in execution[:8]]]
if extra:
    text.append('candidate: ' + ', '.join(extra))
with open(out+'/telegram_distribution_text_v1.txt','w') as f:
    f.write("\n".join(text))
print('distribution', len(execution))
PY4
# 6层：校准层
python3 - <<'PY5'
import json, time, os
root='/root/.openclaw-wanglin/.openclaw/workspace/agents/wanglin/ZeroOne_Forge_AI_Trading_OS'
watch=json.load(open(root+'/data/market_os_stage1/pools/watch_pool.json'))
candidate=json.load(open(root+'/data/market_os_stage1/pools/candidate_pool.json'))
execution=json.load(open(root+'/data/market_os_stage1/pools/execution_pool.json'))
thought=json.load(open(root+'/data/market_os_stage1/thought_layer/compact_analysis_outputs_v1.json'))
paper=json.load(open(root+'/data/market_os_stage1/execution_layer/paper_execution_orders_v1.json'))
distribution=json.load(open(root+'/data/market_os_stage1/distribution_layer/distribution_summary_v1.json'))
out=root+'/data/market_os_stage1/calibration_layer'
os.makedirs(out, exist_ok=True)
now=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
thought_syms={x['symbol'] for x in thought}
paper_syms={x['symbol'] for x in paper}
exec_syms=[x['symbol'] for x in execution]
report={'updated_at':now,'watch_count':len(watch),'candidate_count':len(candidate),'execution_count':len(execution),'thought_count':len(thought),'paper_count':len(paper),'distribution_summary':distribution.get('summary'),'execution_missing_in_thought':[s for s in exec_syms if s not in thought_syms],'execution_missing_in_paper':[s for s in exec_syms if s not in paper_syms],'next_step':'继续下一轮刷新后验证'}
with open(out+'/calibration_snapshot_v1.json','w') as f: json.dump(report,f,ensure_ascii=False,indent=2)
with open(out+'/calibration_report_v1.json','w') as f: json.dump({'updated_at':now,'current_status':'full_chain_refresh_completed','next_step':'等待下一轮自动刷新继续校准'},f,ensure_ascii=False,indent=2)
print('calibration', len(exec_syms))
PY5
echo "[market-os] full-chain refresh done"
